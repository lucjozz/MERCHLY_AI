"""GET /tipo-cambio: dólar oficial del BCB (DEC-035). Exige sesión (los 4 roles)."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from redis.asyncio import Redis

from app.core.dependencias import TODOS_LOS_ROLES, requiere_rol
from app.core.redis import get_redis_client
from app.models.usuario import Usuario
from app.services.tipo_cambio import TipoCambioNoDisponibleError, obtener_tipo_cambio

router = APIRouter(prefix="/tipo-cambio", tags=["tipo-cambio"])


class TipoCambioSalida(BaseModel):
    valor: float
    fecha: str | None
    fuente: str
    actualizado: str
    desactualizado: bool


@router.get("", response_model=TipoCambioSalida)
async def tipo_cambio(
    _: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
    redis: Redis = Depends(get_redis_client),
) -> TipoCambioSalida:
    try:
        tc = await obtener_tipo_cambio(redis)
    except TipoCambioNoDisponibleError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No pudimos obtener el tipo de cambio del BCB en este momento.",
        )
    return TipoCambioSalida(**tc.__dict__)
