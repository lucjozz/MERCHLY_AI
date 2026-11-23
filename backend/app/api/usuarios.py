"""Gestión del equipo: solo admin_principal, siempre en su organización (docs/004-Backend/03, sección 5)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import requiere_rol
from app.models.usuario import Usuario
from app.schemas.usuarios import (
    InvitacionCreada,
    InvitacionEntrada,
    InvitacionSalida,
    MiembroCambio,
    MiembroSalida,
)
from app.services.equipo import (
    ReglaEquipoError,
    cambiar_miembro,
    invitar,
    listar_invitaciones,
    listar_miembros,
    revocar_invitacion,
)

router = APIRouter(prefix="/usuarios", tags=["usuarios"])
solo_admin = requiere_rol("admin_principal")


@router.get("", response_model=list[MiembroSalida])
async def miembros(
    db_session: AsyncSession = Depends(get_db_session), admin: Usuario = Depends(solo_admin)
) -> list[MiembroSalida]:
    return await listar_miembros(db_session, admin.organizacion_id)


@router.patch("/{miembro_id}", response_model=MiembroSalida)
async def cambiar(
    miembro_id: uuid.UUID,
    cambio: MiembroCambio,
    db_session: AsyncSession = Depends(get_db_session),
    admin: Usuario = Depends(solo_admin),
) -> MiembroSalida:
    try:
        miembro = await cambiar_miembro(db_session, admin, miembro_id, cambio)
    except ReglaEquipoError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    if miembro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe ese miembro.")
    return miembro


@router.get("/invitaciones", response_model=list[InvitacionSalida])
async def invitaciones(
    db_session: AsyncSession = Depends(get_db_session), admin: Usuario = Depends(solo_admin)
) -> list[InvitacionSalida]:
    return await listar_invitaciones(db_session, admin.organizacion_id)


@router.post("/invitaciones", response_model=InvitacionCreada, status_code=status.HTTP_201_CREATED)
async def crear_invitacion(
    entrada: InvitacionEntrada,
    db_session: AsyncSession = Depends(get_db_session),
    admin: Usuario = Depends(solo_admin),
) -> InvitacionCreada:
    """Devuelve el token UNA sola vez: el front arma el link para copiarlo."""
    try:
        invitacion, token = await invitar(db_session, admin, entrada)
    except ReglaEquipoError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return InvitacionCreada(**InvitacionSalida.model_validate(invitacion).model_dump(), token=token)


@router.delete("/invitaciones/{invitacion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revocar(
    invitacion_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    admin: Usuario = Depends(solo_admin),
) -> Response:
    if not await revocar_invitacion(db_session, admin.organizacion_id, invitacion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe esa invitación.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
