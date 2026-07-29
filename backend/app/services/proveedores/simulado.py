"""Provisional research provider (no real LLM/web-search integration yet).

**Este proveedor es un placeholder.** Devuelve resultados sintéticos pero
estructuralmente válidos, para que el resto del sistema (validación,
persistencia, API) pueda construirse y probarse de punta a punta antes de
que exista una integración real con Gemini (proveedor asignado en
``docs/100-Organizacion/06-Agentes-IA.md``) y con búsqueda web.

Reemplazar por una implementación real es un prerequisito antes de operar
sobre una tienda real — usar este proveedor en producción violaría la
sección 8 del contrato del agente ("no debe presentar resultados
fabricados"). Ver ``docs/007-Agentes/04-Registro-de-Agentes.md`` para el
seguimiento de este pendiente.
"""

from app.schemas.investigador_producto import (
    InvestigacionInput,
    NivelEstimado,
    ProductoCandidatoOutput,
)
from app.services.proveedores.base import ProveedorInvestigacion


class ProveedorInvestigacionSimulado(ProveedorInvestigacion):
    """Deterministic stub provider used until a real integration exists."""

    async def investigar(
        self, entrada: InvestigacionInput
    ) -> list[ProductoCandidatoOutput]:
        """Return synthetic candidates, clearly marked as simulated.

        Args:
            entrada: validated research request.

        Returns:
            list[ProductoCandidatoOutput]: up to ``entrada.cantidad_resultados``
            synthetic candidates.
        """
        cantidad = entrada.cantidad_resultados
        resultados: list[ProductoCandidatoOutput] = []

        for indice in range(1, cantidad + 1):
            nombre = f"{entrada.categoria.title()} — candidato {indice} (simulado)"
            if any(
                marca.strip().lower() in nombre.lower()
                for marca in entrada.excluir_marcas
            ):
                continue

            resultados.append(
                ProductoCandidatoOutput(
                    nombre_producto=nombre,
                    categoria=entrada.categoria,
                    precio_estimado_proveedor=None,
                    precio_sugerido_venta=None,
                    nivel_demanda_estimado=NivelEstimado.MEDIO,
                    nivel_competencia_estimado=NivelEstimado.MEDIO,
                    fuentes_evidencia=[],
                    riesgos_identificados=[
                        "Resultado generado por el proveedor simulado "
                        "(ProveedorInvestigacionSimulado); no usar para "
                        "decisiones de negocio reales."
                    ],
                )
            )

        return resultados
