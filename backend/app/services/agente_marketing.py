"""Agente de Marketing — orquestación.

Implementa el contrato técnico en
``docs/007-Agentes/06-Agente-de-Marketing.md``: valida que los productos
referenciados existan y estén en ``estado = 'en_catalogo'``, invoca al
proveedor con política de reintentos, combina el resultado con una
distribución de presupuesto determinística (no generada por IA) y arma
la salida. No persiste nada (contrato, sección 3).
"""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.producto_candidato import ProductoCandidato
from app.schemas.marketing import MarketingInput, MarketingMetadata, MarketingOutput
from app.services.proveedores.marketing_base import ProveedorMarketing, ProveedorMarketingError

logger = logging.getLogger(__name__)

# Contrato, sección 8: misma política que el Investigador de Producto.
MAX_REINTENTOS = 2
ESPERA_ENTRE_REINTENTOS_SEGUNDOS = 5

_ESTADO_REQUERIDO = "en_catalogo"


class ProductosInvalidosError(Exception):
    """Se lanza cuando algún producto referenciado no existe o no está
    en estado 'en_catalogo' (contrato, sección 2). El endpoint la
    traduce a un 422 — es un error de validación de la solicitud, no una
    falla del agente."""


class AgenteMarketing:
    """Orquesta la generación de una propuesta de campaña de punta a punta.

    Attributes:
        proveedor: implementación concreta de ``ProveedorMarketing``.
        db_session: sesión async de SQLAlchemy, de solo lectura para
            este agente (no persiste nada, contrato sección 3).
    """

    def __init__(self, proveedor: ProveedorMarketing, db_session: AsyncSession) -> None:
        self.proveedor = proveedor
        self.db_session = db_session

    async def ejecutar(self, entrada: MarketingInput) -> MarketingOutput:
        """Genera una propuesta de campaña.

        Args:
            entrada: solicitud ya validada por ``MarketingInput``.

        Returns:
            MarketingOutput: la propuesta completa. Si el proveedor falla
            tras agotar los reintentos, se devuelve una respuesta vacía
            con la advertencia correspondiente (contrato, sección 8), en
            vez de lanzar una excepción hacia el llamador.

        Raises:
            ProductosInvalidosError: si algún producto no existe o no
            está en estado 'en_catalogo'. Se levanta antes de invocar al
            proveedor, para no gastar cuota en una solicitud inválida.
        """
        productos = await self._obtener_y_validar_productos(entrada)
        resultado = await self._generar_con_reintentos(entrada, productos)

        if resultado is None:
            return MarketingOutput(
                productos_candidato_ids=entrada.productos_candidato_ids,
                advertencias=[
                    "No se pudo generar la campaña: el proveedor de "
                    "marketing falló tras agotar los reintentos."
                ],
                metadata=MarketingMetadata(
                    idioma_destino=entrada.idioma_destino, tono=entrada.tono
                ),
            )

        return MarketingOutput(
            productos_candidato_ids=entrada.productos_candidato_ids,
            angulos_de_campana=resultado.angulos_de_campana,
            copy_por_canal=resultado.copy_por_canal,
            publico_objetivo_sugerido=resultado.publico_objetivo_sugerido,
            distribucion_presupuesto_sugerida=self._distribuir_presupuesto(entrada),
            advertencias=resultado.advertencias,
            metadata=MarketingMetadata(
                idioma_destino=entrada.idioma_destino, tono=entrada.tono
            ),
        )

    async def _obtener_y_validar_productos(
        self, entrada: MarketingInput
    ) -> list[ProductoCandidato]:
        """Busca los productos y valida existencia + estado (contrato, sección 2)."""
        consulta = select(ProductoCandidato).where(
            ProductoCandidato.id.in_(entrada.productos_candidato_ids),
            ProductoCandidato.eliminado_en.is_(None),
        )
        resultado = await self.db_session.execute(consulta)
        productos = list(resultado.scalars().all())

        encontrados = {producto.id for producto in productos}
        faltantes = [
            str(pid) for pid in entrada.productos_candidato_ids if pid not in encontrados
        ]
        if faltantes:
            raise ProductosInvalidosError(
                f"No existen o fueron eliminados los productos: {', '.join(faltantes)}"
            )

        invalidos = [
            f"{producto.id} (estado: {producto.estado})"
            for producto in productos
            if producto.estado != _ESTADO_REQUERIDO
        ]
        if invalidos:
            raise ProductosInvalidosError(
                "Solo se puede generar marketing para productos en estado "
                f"'{_ESTADO_REQUERIDO}'. Inválidos: {', '.join(invalidos)}"
            )

        return productos

    async def _generar_con_reintentos(
        self, entrada: MarketingInput, productos: list[ProductoCandidato]
    ):
        """Invoca al proveedor, reintentando ante fallas (contrato, sección 8)."""
        ultimo_error: Exception | None = None

        for intento in range(MAX_REINTENTOS + 1):
            try:
                return await self.proveedor.generar_campana(entrada, productos)
            except ProveedorMarketingError as error:
                ultimo_error = error
                logger.warning(
                    "Fallo del proveedor de marketing (intento %s/%s): %s",
                    intento + 1,
                    MAX_REINTENTOS + 1,
                    error,
                )
                if intento < MAX_REINTENTOS:
                    await asyncio.sleep(ESPERA_ENTRE_REINTENTOS_SEGUNDOS)

        logger.error(
            "El proveedor de marketing agotó los reintentos: %s", ultimo_error
        )
        return None

    @staticmethod
    def _distribuir_presupuesto(entrada: MarketingInput) -> dict | None:
        """Reparte el presupuesto de referencia en partes iguales entre canales.

        Es una sugerencia orientativa determinística (contrato, sección 3),
        no generada por el proveedor de IA. Simplificación deliberada de
        v1: reparto uniforme; una versión futura podría ponderar por canal
        si se detecta una necesidad real de hacerlo de forma distinta.
        """
        if entrada.presupuesto_mensual_referencia is None:
            return None

        proporcion = round(1 / len(entrada.canales_objetivo), 4)
        return {canal: proporcion for canal in entrada.canales_objetivo}
