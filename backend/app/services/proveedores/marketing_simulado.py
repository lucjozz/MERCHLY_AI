"""Proveedor de marketing provisional (sin integración real con ChatGPT).

**Este proveedor es un placeholder.** Devuelve contenido sintético pero
estructuralmente válido, marcado explícitamente como simulado en
``advertencias``, para que el resto del sistema (validación, orquestación,
API) pueda construirse y probarse de punta a punta antes de integrar el
proveedor real (ChatGPT, ver ``docs/100-Organizacion/06-Agentes-IA.md``).
Mismo criterio ya usado en ``app/services/proveedores/simulado.py`` para
el Agente Investigador de Producto.

No usar en decisiones de negocio reales — ver
``docs/007-Agentes/04-Registro-de-Agentes.md`` para el seguimiento de
este pendiente.
"""

from app.models.producto_candidato import ProductoCandidato
from app.schemas.marketing import CanalMarketing, CopyVariante, MarketingInput
from app.services.proveedores.marketing_base import (
    ProveedorMarketing,
    ResultadoProveedorMarketing,
)


class ProveedorMarketingSimulado(ProveedorMarketing):
    """Proveedor determinístico usado hasta que exista integración real."""

    async def generar_campana(
        self, entrada: MarketingInput, productos: list[ProductoCandidato]
    ) -> ResultadoProveedorMarketing:
        """Devuelve contenido sintético, claramente marcado como tal.

        Args:
            entrada: solicitud validada, con productos ya verificados.
            productos: filas reales de los productos referenciados.

        Returns:
            ResultadoProveedorMarketing: contenido simulado.
        """
        nombres = ", ".join(producto.nombre_producto for producto in productos)

        angulos = [
            f"Angulo simulado para {nombres} (tono: {entrada.tono.value})",
        ]

        copy_por_canal: dict[CanalMarketing, list[CopyVariante]] = {
            canal: [
                CopyVariante(
                    titulo=f"[Simulado] {producto.nombre_producto} — {canal.value}",
                    cuerpo=(
                        f"Copy simulado para {producto.nombre_producto} en "
                        f"{canal.value}. No usar en publicaciones reales."
                    ),
                )
                for producto in productos
            ]
            for canal in entrada.canales_objetivo
        }

        advertencias = [
            "Resultado generado por el proveedor simulado "
            "(ProveedorMarketingSimulado); no usar en campañas reales."
        ]
        productos_sin_evidencia = [
            producto.nombre_producto for producto in productos if not producto.fuentes_evidencia
        ]
        if productos_sin_evidencia:
            advertencias.append(
                "Sin evidencia registrada para: " + ", ".join(productos_sin_evidencia)
            )

        return ResultadoProveedorMarketing(
            angulos_de_campana=angulos,
            copy_por_canal=copy_por_canal,
            publico_objetivo_sugerido=f"Público objetivo simulado para: {nombres}",
            advertencias=advertencias,
        )
