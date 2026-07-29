"""Agente Investigador de Producto — orquestación.

Implementa el ciclo completo descrito en el contrato técnico
(``docs/007-Agentes/03-Agente-Investigador-de-Producto.md``): validar
entrada, invocar al proveedor de investigación con política de
reintentos, persistir los resultados en ``productos_candidatos``
(``docs/006-BaseDatos/02-Esquema-Fase1.md``) y devolver la salida
estructurada.
"""

import asyncio
import logging
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.producto_candidato import ProductoCandidato
from app.schemas.investigador_producto import (
    InvestigacionInput,
    InvestigacionMetadata,
    InvestigacionOutput,
    ProductoCandidatoOutput,
)
from app.services.proveedores.base import ProveedorInvestigacion, ProveedorInvestigacionError

logger = logging.getLogger(__name__)

# Política de reintentos, contrato sección 8: "máximo 2 reintentos por
# fuente, con espera de 5 segundos entre intentos".
MAX_REINTENTOS = 2
ESPERA_ENTRE_REINTENTOS_SEGUNDOS = 5


class AgenteInvestigadorProducto:
    """Orquesta una investigación de producto de punta a punta.

    Attributes:
        proveedor: implementación concreta de ``ProveedorInvestigacion``
            (hoy, ``ProveedorInvestigacionSimulado``; en el futuro, una
            integración real con Gemini).
        db_session: sesión async de SQLAlchemy para persistir resultados.
    """

    def __init__(self, proveedor: ProveedorInvestigacion, db_session: AsyncSession) -> None:
        self.proveedor = proveedor
        self.db_session = db_session

    async def ejecutar(self, entrada: InvestigacionInput) -> InvestigacionOutput:
        """Ejecuta una investigación completa.

        Args:
            entrada: solicitud ya validada por ``InvestigacionInput``
                (Pydantic aplica las validaciones de la sección 2 del
                contrato al construir el objeto).

        Returns:
            InvestigacionOutput: productos encontrados y su metadata. Si
            el proveedor falla tras agotar los reintentos, se devuelve una
            lista vacía con el motivo en ``riesgos_identificados`` del
            único elemento de metadata posible (contrato, sección 8:
            "escalamiento ... en vez de inventar productos"), en lugar de
            lanzar una excepción hacia el llamador.
        """
        productos = await self._investigar_con_reintentos(entrada)

        confianza = "normal" if productos else "baja"
        investigacion_id = uuid4()

        if productos:
            await self._persistir(productos, entrada, investigacion_id)

        metadata = InvestigacionMetadata(
            categoria_consultada=entrada.categoria,
            mercado_objetivo=entrada.mercado_objetivo,
            total_productos_evaluados=len(productos),
            total_productos_devueltos=len(productos),
            confianza=confianza,
            investigacion_id=investigacion_id,
        )

        return InvestigacionOutput(productos=productos, metadata=metadata)

    async def _investigar_con_reintentos(
        self, entrada: InvestigacionInput
    ) -> list[ProductoCandidatoOutput]:
        """Invoca al proveedor, reintentando ante fallas (contrato, sección 8)."""
        ultimo_error: Exception | None = None

        for intento in range(MAX_REINTENTOS + 1):
            try:
                return await self.proveedor.investigar(entrada)
            except ProveedorInvestigacionError as error:
                ultimo_error = error
                logger.warning(
                    "Fallo del proveedor de investigación (intento %s/%s): %s",
                    intento + 1,
                    MAX_REINTENTOS + 1,
                    error,
                )
                if intento < MAX_REINTENTOS:
                    await asyncio.sleep(ESPERA_ENTRE_REINTENTOS_SEGUNDOS)

        logger.error(
            "El proveedor de investigación agotó los reintentos para la "
            "categoría '%s': %s",
            entrada.categoria,
            ultimo_error,
        )
        return []

    async def _persistir(
        self,
        productos: list[ProductoCandidatoOutput],
        entrada: InvestigacionInput,
        investigacion_id: UUID,
    ) -> None:
        """Persiste los productos encontrados en ``productos_candidatos``.

        Todas las filas de una misma ejecución comparten
        ``investigacion_id`` (el mismo que se reporta en la metadata de
        salida), conforme a ``docs/006-BaseDatos/02-Esquema-Fase1.md``. El
        ``estado`` nace en ``'candidato'`` (default del modelo); ningún
        producto pasa a ``'en_catalogo'`` desde este método, conforme a la
        sección 7 del contrato del agente ("requiere aprobación humana
        explícita").
        """
        for producto in productos:
            fila = ProductoCandidato(
                investigacion_id=investigacion_id,
                nombre_producto=producto.nombre_producto,
                categoria=producto.categoria,
                mercado_objetivo=entrada.mercado_objetivo,
                precio_estimado_proveedor=producto.precio_estimado_proveedor,
                precio_sugerido_venta=producto.precio_sugerido_venta,
                nivel_demanda_estimado=producto.nivel_demanda_estimado.value,
                nivel_competencia_estimado=producto.nivel_competencia_estimado.value,
                fuentes_evidencia=producto.fuentes_evidencia,
                riesgos_identificados=producto.riesgos_identificados,
            )
            self.db_session.add(fila)

        await self.db_session.commit()
