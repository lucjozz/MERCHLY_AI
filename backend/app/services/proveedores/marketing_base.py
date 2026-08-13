"""Proveedor abstracto de generación de campañas para el Agente de Marketing.

El contrato técnico (``docs/007-Agentes/06-Agente-de-Marketing.md``,
sección 1) asigna "ChatGPT" como proveedor actual (rol "Marketing IA" en
``docs/100-Organizacion/06-Agentes-IA.md``). Esta abstracción permite
construir y testear el resto del sistema con un proveedor simulado antes
de integrar el proveedor real — mismo patrón ya validado con
``ProveedorInvestigacion`` (ver ``app/services/proveedores/base.py``).
"""

from abc import ABC, abstractmethod

from app.models.producto_candidato import ProductoCandidato
from app.schemas.marketing import CanalMarketing, CopyVariante, MarketingInput


class ProveedorMarketingError(Exception):
    """Se lanza cuando el proveedor de marketing no puede completar la solicitud."""


class ResultadoProveedorMarketing:
    """Contenido generado por el proveedor, antes de combinarse con la
    distribución de presupuesto (determinística, no generada por IA) y
    las advertencias derivadas de datos faltantes (calculadas por el
    servicio, no por el proveedor).

    Attributes:
        angulos_de_campana: mensajes centrales propuestos.
        copy_por_canal: variantes de copy por canal solicitado.
        publico_objetivo_sugerido: descripción del público objetivo.
        advertencias: afirmaciones que el proveedor no pudo verificar.
    """

    def __init__(
        self,
        angulos_de_campana: list[str],
        copy_por_canal: dict[CanalMarketing, list[CopyVariante]],
        publico_objetivo_sugerido: str,
        advertencias: list[str],
    ) -> None:
        self.angulos_de_campana = angulos_de_campana
        self.copy_por_canal = copy_por_canal
        self.publico_objetivo_sugerido = publico_objetivo_sugerido
        self.advertencias = advertencias


class ProveedorMarketing(ABC):
    """Port que cualquier proveedor de generación de campañas debe implementar."""

    @abstractmethod
    async def generar_campana(
        self, entrada: MarketingInput, productos: list[ProductoCandidato]
    ) -> ResultadoProveedorMarketing:
        """Genera el contenido de campaña para los productos dados.

        Args:
            entrada: solicitud ya validada (schema) y con productos ya
                verificados como existentes y en estado 'en_catalogo'.
            productos: las filas reales de ``productos_candidatos``
                referenciadas, para que el proveedor use su evidencia
                real (``fuentes_evidencia``, ``riesgos_identificados``).

        Returns:
            ResultadoProveedorMarketing: el contenido generado.

        Raises:
            ProveedorMarketingError: si el proveedor no puede completar
            la solicitud. El llamador (``AgenteMarketing``) es
            responsable de la política de reintentos (contrato, sección 8).
        """
        raise NotImplementedError
