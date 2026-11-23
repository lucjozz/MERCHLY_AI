"""Endpoints del historial de campañas (docs/004-Backend/03, sección 1)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import ROLES_DECISION, TODOS_LOS_ROLES, contexto_peticion, requiere_rol
from app.services.auditoria import registrar_evento
from app.models.usuario import Usuario
from app.schemas.campanas import CampanaDetalle, CampanaEdicion, CampanasListado
from app.services.campanas import editar_campana, eliminar_campana, listar_campanas, obtener_campana

router = APIRouter(prefix="/campanas", tags=["campanas"])
NO_ENCONTRADA = "No existe esa campaña."


@router.get("", response_model=CampanasListado)
async def listar(
    pagina: int = Query(default=1, ge=1, le=10_000),
    tamano_pagina: int = Query(default=20, ge=1, le=100),
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> CampanasListado:
    campanas, total = await listar_campanas(db_session, usuario.organizacion_id, pagina, tamano_pagina)
    return CampanasListado(campanas=campanas, total=total, pagina=pagina, tamano_pagina=tamano_pagina)


@router.get("/{campana_id}", response_model=CampanaDetalle)
async def detalle(
    campana_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> CampanaDetalle:
    campana = await obtener_campana(db_session, usuario.organizacion_id, campana_id)
    if campana is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_ENCONTRADA)
    return campana


@router.patch("/{campana_id}", response_model=CampanaDetalle)
async def editar(
    campana_id: uuid.UUID,
    cambios: CampanaEdicion,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*ROLES_DECISION)),
) -> CampanaDetalle:
    campana = await editar_campana(db_session, usuario.organizacion_id, campana_id, cambios)
    if campana is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_ENCONTRADA)
    return campana


@router.delete("/{campana_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(
    campana_id: uuid.UUID,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*ROLES_DECISION)),
) -> Response:
    if not await eliminar_campana(db_session, usuario.organizacion_id, campana_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_ENCONTRADA)
    await registrar_evento(
        "campana_borrada", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
        objetivo_tipo="campana", objetivo_id=campana_id, **contexto_peticion(request),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
