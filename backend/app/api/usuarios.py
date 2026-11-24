"""Gestión del equipo: solo admin_principal, siempre en su organización (docs/004-Backend/03, sección 5)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import contexto_peticion, requiere_rol, verificar_reautenticacion
from app.services.auditoria import hash_corto, registrar_evento
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


@router.patch("/{miembro_id}", response_model=MiembroSalida, dependencies=[Depends(verificar_reautenticacion)])
async def cambiar(
    miembro_id: uuid.UUID,
    cambio: MiembroCambio,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    admin: Usuario = Depends(solo_admin),
) -> MiembroSalida:
    previo = await db_session.get(Usuario, miembro_id)
    antes = (previo.rol, previo.activo) if previo is not None and previo.organizacion_id == admin.organizacion_id else None
    try:
        miembro = await cambiar_miembro(db_session, admin, miembro_id, cambio)
    except ReglaEquipoError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    if miembro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe ese miembro.")
    if antes is not None:
        comunes = {"organizacion_id": admin.organizacion_id, "usuario_id": admin.id, "objetivo_tipo": "usuario",
                   "objetivo_id": miembro.id, **contexto_peticion(request)}
        if miembro.rol != antes[0]:
            await registrar_evento("rol_cambiado", detalle={"miembro": miembro.nombre, "antes": antes[0], "despues": miembro.rol}, **comunes)
        if miembro.activo != antes[1]:
            await registrar_evento("usuario_reactivado" if miembro.activo else "usuario_desactivado", detalle={"miembro": miembro.nombre}, **comunes)
    return miembro


@router.get("/invitaciones", response_model=list[InvitacionSalida])
async def invitaciones(
    db_session: AsyncSession = Depends(get_db_session), admin: Usuario = Depends(solo_admin)
) -> list[InvitacionSalida]:
    return await listar_invitaciones(db_session, admin.organizacion_id)


@router.post("/invitaciones", response_model=InvitacionCreada, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(verificar_reautenticacion)])
async def crear_invitacion(
    entrada: InvitacionEntrada,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    admin: Usuario = Depends(solo_admin),
) -> InvitacionCreada:
    """Devuelve el token UNA sola vez: el front arma el link para copiarlo."""
    try:
        invitacion, token = await invitar(db_session, admin, entrada)
    except ReglaEquipoError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    await registrar_evento(
        "invitacion_creada", organizacion_id=admin.organizacion_id, usuario_id=admin.id, objetivo_tipo="invitacion",
        objetivo_id=invitacion.id, detalle={"rol": invitacion.rol, "email_hash": hash_corto(invitacion.email)},
        **contexto_peticion(request),
    )
    return InvitacionCreada(**InvitacionSalida.model_validate(invitacion).model_dump(), token=token)


@router.delete("/invitaciones/{invitacion_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(verificar_reautenticacion)])
async def revocar(
    invitacion_id: uuid.UUID,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    admin: Usuario = Depends(solo_admin),
) -> Response:
    if not await revocar_invitacion(db_session, admin.organizacion_id, invitacion_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe esa invitación.")
    await registrar_evento(
        "invitacion_revocada", organizacion_id=admin.organizacion_id, usuario_id=admin.id,
        objetivo_tipo="invitacion", objetivo_id=invitacion_id, **contexto_peticion(request),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
