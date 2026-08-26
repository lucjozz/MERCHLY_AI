import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decisiones import DecisionContext, DecisionEvidence, DecisionRecord
from app.schemas.decisiones import DecisionInput


async def registrar_decision(
    db_session: AsyncSession, entrada: DecisionInput
) -> DecisionRecord:
    """Registra una decisión humana, con su contexto y evidencias si vienen.

    Args:
        db_session: sesión async de SQLAlchemy.
        entrada: la decisión ya validada por DecisionInput.

    Returns:
        DecisionRecord: la decisión recién creada, ya persistida.
    """
    decision = DecisionRecord(
        id=uuid.uuid4(),
        decision_type=entrada.decision_type,
        entity_type=entrada.entity_type,
        entity_id=entrada.entity_id,
        action=entrada.action.value,
        user_id=entrada.user_id,
        reason=entrada.reason,
    )
    db_session.add(decision)
    await db_session.flush()

    if entrada.context_data is not None:
        contexto = DecisionContext(
            id=uuid.uuid4(),
            decision_id=decision.id,
            context_data=entrada.context_data,
        )
        db_session.add(contexto)

    for evidencia_input in entrada.evidencias:
        evidencia = DecisionEvidence(
            id=uuid.uuid4(),
            decision_id=decision.id,
            source_type=evidencia_input.source_type,
            source_url=evidencia_input.source_url,
            source_title=evidencia_input.source_title,
            evidence=evidencia_input.evidence,
        )
        db_session.add(evidencia)

    await db_session.commit()
    await db_session.refresh(decision)
    return decision


async def obtener_decision_por_id(
    db_session: AsyncSession, decision_id: uuid.UUID
) -> DecisionRecord | None:
    """Busca una decisión por su ID."""
    consulta = select(DecisionRecord).where(DecisionRecord.id == decision_id)
    resultado = await db_session.execute(consulta)
    return resultado.scalar_one_or_none()