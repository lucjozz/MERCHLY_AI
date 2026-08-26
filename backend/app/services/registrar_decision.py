"""Servicio para registrar y consultar decisiones humanas."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decisiones import DecisionContext, DecisionEvidence, DecisionRecord
from app.models.producto_candidato import ProductoCandidato
from app.schemas.decisiones import AccionDecision, DecisionInput

ACCION_A_ESTADO = {
    AccionDecision.APROBAR: "en_catalogo",
    AccionDecision.DESCARTAR: "descartado",
}


async def registrar_decision(
    db_session: AsyncSession, entrada: DecisionInput
) -> DecisionRecord:
    """Registra una decisión humana y, si aplica, ejecuta el cambio de
    estado real sobre la entidad decidida.

    Args:
        db_session: sesión async de SQLAlchemy.
        entrada: la decisión ya validada por DecisionInput.

    Returns:
        DecisionRecord: la decisión recién creada, ya persistida.

    Raises:
        ValueError: si entity_type es "product_candidate" pero no existe
            ningún producto con ese entity_id.
    """
    if entrada.entity_type == "product_candidate":
        producto = await db_session.get(ProductoCandidato, entrada.entity_id)
        if producto is None:
            raise ValueError(
                f"No existe un producto candidato con id {entrada.entity_id}."
            )

        nuevo_estado = ACCION_A_ESTADO.get(entrada.action)
        if nuevo_estado is not None:
            producto.estado = nuevo_estado

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