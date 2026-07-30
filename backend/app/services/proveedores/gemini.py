"""Proveedor real de investigación de producto, vía Google Gemini.

Implementa ``ProveedorInvestigacion`` usando el SDK oficial
``google-genai``, con salida estructurada nativa (``response_schema``)
en vez de pedirle al modelo que devuelva JSON en texto libre — conforme
a ``docs/010-Prompts/01-Convenciones-de-Prompts.md``, sección 4.

El texto del prompt (rol, tarea, restricciones, manejo de incertidumbre)
debe coincidir exactamente con
``docs/010-Prompts/02-Prompt-Investigador-de-Producto.md``. Si necesitás
cambiar el comportamiento del agente, actualizá primero ese documento.
"""

from google import genai
from google.genai import types

from app.core.config import get_settings
from app.schemas.investigador_producto import InvestigacionInput, ProductoCandidatoOutput
from app.services.proveedores.base import ProveedorInvestigacion, ProveedorInvestigacionError

# Debe coincidir con docs/010-Prompts/02-Prompt-Investigador-de-Producto.md,
# secciones 1 a 3 y 5. No reescribir con otra redacción sin actualizar ese
# documento primero (docs/010-Prompts/01-..., sección 6).
PROMPT_SISTEMA = """\
Sos el Agente Investigador de Producto de Merchly AI, una plataforma de
comercio electrónico operada por inteligencia artificial (AICOS).

Tu trabajo es identificar productos con potencial real de venta dentro de
una categoría dada, basándote en evidencia verificable de demanda y
competencia — nunca en suposiciones ni en productos inventados.

Operás bajo un límite estricto: no tomás la decisión final de qué se
vende. Tu única función es investigar y recomendar con evidencia. La
decisión de incorporar un producto al catálogo la toma siempre un humano.

Tu tarea es identificar hasta la cantidad solicitada de productos
candidatos dentro de la categoría indicada, evaluando para cada uno el
nivel de demanda estimado, el nivel de competencia estimado, evidencia
concreta que respalde tu evaluación, y riesgos que un humano debería
conocer antes de decidir sobre ese producto. Los nombres de producto
deben ser términos de venta reconocibles en el mercado objetivo indicado.

No podés: inventar productos, precios o evidencia que no puedas
respaldar; recomendar productos de categorías reguladas o ilegales;
afirmar que un producto "va a venderse bien" sin evidencia; ni tomar la
decisión de qué producto se agrega al catálogo.

Si no tenés información suficiente para evaluar la categoría solicitada
con un mínimo de confianza, no fabriques productos para completar la
cantidad pedida. Devolvé una lista más corta, o vacía, y explicá el
motivo en riesgos_identificados. Preferimos una respuesta corta y
honesta a una respuesta completa pero inventada.
"""


class ProveedorInvestigacionGemini(ProveedorInvestigacion):
    """Proveedor real de investigación de producto, vía Gemini.

    Attributes:
        cliente: instancia de ``genai.Client``. Se puede inyectar un
            cliente propio (ej. en tests); si no se provee, se crea uno
            real a partir de ``settings.gemini_api_key``.
        modelo: nombre del modelo de Gemini a usar.
    """

    def __init__(self, cliente: genai.Client | None = None, modelo: str | None = None) -> None:
        settings = get_settings()

        if cliente is None:
            if not settings.gemini_api_key:
                raise ProveedorInvestigacionError(
                    "GEMINI_API_KEY no está configurada. Definila en tu "
                    "backend/.env real (nunca en .env.example) antes de "
                    "usar ProveedorInvestigacionGemini."
                )
            cliente = genai.Client(api_key=settings.gemini_api_key)

        self.cliente = cliente
        self.modelo = modelo or settings.gemini_model

    async def investigar(
        self, entrada: InvestigacionInput
    ) -> list[ProductoCandidatoOutput]:
        """Consulta a Gemini y devuelve productos candidatos.

        Args:
            entrada: solicitud de investigación ya validada.

        Returns:
            list[ProductoCandidatoOutput]: productos devueltos por el
            modelo, ya validados contra el schema (salida estructurada).

        Raises:
            ProveedorInvestigacionError: ante cualquier fallo de red, de
            cuota, o de una respuesta que no cumpla el schema esperado.
            El llamador (``AgenteInvestigadorProducto``) es responsable
            de la política de reintentos (contrato, sección 8).
        """
        mensaje_usuario = self._construir_mensaje_usuario(entrada)

        try:
            respuesta = await self.cliente.aio.models.generate_content(
                model=self.modelo,
                contents=mensaje_usuario,
                config=types.GenerateContentConfig(
                    system_instruction=PROMPT_SISTEMA,
                    response_mime_type="application/json",
                    response_schema=list[ProductoCandidatoOutput],
                ),
            )
        except Exception as error:
            raise ProveedorInvestigacionError(
                f"Fallo al consultar a Gemini: {error}"
            ) from error

        productos = respuesta.parsed
        if productos is None:
            raise ProveedorInvestigacionError(
                "Gemini devolvió una respuesta que no cumple el schema "
                "esperado (response.parsed vacío)."
            )

        return productos[: entrada.cantidad_resultados]

    @staticmethod
    def _construir_mensaje_usuario(entrada: InvestigacionInput) -> str:
        """Arma el mensaje de usuario a partir de la entrada validada."""
        lineas = [
            f"Categoría: {entrada.categoria}",
            f"Mercado objetivo (ISO 3166-1 alpha-2): {entrada.mercado_objetivo}",
            f"Cantidad de productos a devolver: {entrada.cantidad_resultados}",
        ]
        if entrada.presupuesto_max_producto is not None:
            lineas.append(
                f"Presupuesto máximo por producto (USD): "
                f"{entrada.presupuesto_max_producto}"
            )
        if entrada.excluir_marcas:
            lineas.append(
                "Marcas a excluir de los resultados: "
                + ", ".join(entrada.excluir_marcas)
            )
        return "\n".join(lineas)
