"""Cuotas por organización para los agentes que cuestan dinero (013-04, sección 4).

Fail-open: si Redis no responde se deja pasar y se loguea (un agente caído
por Redis sería peor que unos pedidos de más; el tope duro de gasto se
configura además en el panel del proveedor de IA).
"""

import logging
import uuid

from fastapi import HTTPException, status
from redis.asyncio import Redis

from app.services.limites import RedisError, consumir_cuota

logger = logging.getLogger(__name__)
VENTANA_CUOTA_SEGUNDOS = 3600


async def aplicar_cuota(redis: Redis, nombre: str, organizacion_id: uuid.UUID, limite: int) -> None:
    """Consume una unidad de la cuota horaria de la organización (429 si se agotó)."""
    try:
        espera = await consumir_cuota(
            redis, nombre, str(organizacion_id), limite, VENTANA_CUOTA_SEGUNDOS
        )
    except RedisError:
        logger.warning("Redis no disponible: cuota '%s' no aplicada (fail-open)", nombre)
        return
    if espera:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Llegaste al límite de uso por hora de este agente. Probá más tarde.",
            headers={"Retry-After": str(espera)},
        )
