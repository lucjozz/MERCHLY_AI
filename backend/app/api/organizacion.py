"""Perfil del negocio y uso del plan (docs/004-Backend/03, secciones 3 y 6)."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import TODOS_LOS_ROLES, contexto_peticion, requiere_rol
from app.services.auditoria import registrar_evento
from app.core.redis import get_redis_client
from app.models.usuario import Usuario
from app.schemas.organizacion import OrganizacionSalida, PerfilEntrada, UsoPlan
from app.services.organizacion import actualizar_perfil, obtener_organizacion, uso_del_plan

router = APIRouter(prefix="/organizacion", tags=["organizacion"])


@router.get("", response_model=OrganizacionSalida)
async def mi_organizacion(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> OrganizacionSalida:
    organizacion = await obtener_organizacion(db_session, usuario.organizacion_id)
    if organizacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe la organización.")
    return organizacion


@router.put("/perfil", response_model=OrganizacionSalida)
async def guardar_perfil(
    perfil: PerfilEntrada,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol("admin_principal")),
) -> OrganizacionSalida:
    """Solo el admin del negocio. Marca el onboarding como completo."""
    organizacion = await actualizar_perfil(db_session, usuario.organizacion_id, perfil)
    if organizacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe la organización.")
    await registrar_evento(
        "perfil_actualizado", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
        detalle={"moneda": perfil.moneda, "dolar": "propio" if perfil.tipo_cambio else "bcb"},
        **contexto_peticion(request),
    )
    return organizacion


@router.get("/uso", response_model=UsoPlan)
async def uso(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
    redis: Redis = Depends(get_redis_client),
) -> UsoPlan:
    organizacion = await obtener_organizacion(db_session, usuario.organizacion_id)
    if organizacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe la organización.")
    return await uso_del_plan(redis, organizacion)
