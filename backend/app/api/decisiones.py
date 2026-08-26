import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.decisiones import DecisionInput, DecisionOutput
from app.services.registrar_decision import obtener_decision_por_id, registrar_decision

router = APIRouter(prefix="/decisiones", tags=["decisiones"])


@router.post(
    "",
    response_model=DecisionOutput,
    status_code=status.HTTP_201_CREATED,
)
async def crear_decision(
    entrada: DecisionInput,
    db_session: AsyncSession = Depends(get_db_session),
) -> DecisionOutput:
    """Registra una nueva decisión humana.

    Args:
        entrada: la decisión a registrar (acción, motivo, contexto y
            evidencias opcionales).
        db_session: sesión de base de datos inyectada.

    Returns:
        DecisionOutput: la decisión recién creada.
    """
    decision = await registrar_decision(db_session=db_session, entrada=entrada)
    return decision


@router.get(
    "/{decision_id}",
    response_model=DecisionOutput,
    status_code=status.HTTP_200_OK,
)
async def obtener_decision(
    decision_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
) -> DecisionOutput:
    """Busca una decisión específica por su ID."""
    decision = await obtener_decision_por_id(
        db_session=db_session, decision_id=decision_id
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe una decisión con id {decision_id}.",
        )

    return decision