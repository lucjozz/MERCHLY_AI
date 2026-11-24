"""Endpoints de decisiones humanas (todos exigen autenticación, 013-04)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import ROLES_DECISION, TODOS_LOS_ROLES, requiere_rol
from app.models.usuario import Usuario
from app.schemas.decisiones import DecisionInput, DecisionOutput
from app.services.registrar_decision import (
    EntidadNoEncontradaError,
    TransicionInvalidaError,
    obtener_decision_por_id,
    registrar_decision,
)

router = APIRouter(prefix="/decisiones", tags=["decisiones"])


@router.post("", response_model=DecisionOutput, status_code=status.HTTP_201_CREATED)
async def crear_decision(
    entrada: DecisionInput,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*ROLES_DECISION)),
) -> DecisionOutput:
    """Registra una decisión. 404 si el producto no existe (o es de otra
    organización); 409 si la transición de estado no es válida."""
    try:
        return await registrar_decision(
            db_session=db_session,
            entrada=entrada,
            user_id=usuario.id,
            organizacion_id=usuario.organizacion_id,
        )
    except EntidadNoEncontradaError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except TransicionInvalidaError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este producto ya tiene una decisión que no permite eso. Recargá la página para ver su estado.",
        ) from error


@router.get("/{decision_id}", response_model=DecisionOutput)
async def obtener_decision(
    decision_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> DecisionOutput:
    """Una decisión de la organización del usuario (404 si no)."""
    decision = await obtener_decision_por_id(db_session, usuario.organizacion_id, decision_id)
    if decision is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe esa decisión.")
    return decision
