"""Servicio para registrar y consultar decisiones humanas."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.decisiones import DecisionContext, DecisionEvidence, DecisionRecord
from app.models.producto_candidato import ProductoCandidato
from app.schemas.decisiones import AccionDecision, DecisionInput, DecisionOutput, EvidenciaDetalle

ACCION_A_ESTADO = {
    AccionDecision.APROBAR: "en_catalogo",
    AccionDecision.DESCARTAR: "descartado",
}


def _opciones_carga_completa():
    """Opciones de carga ansiosa (eager load) para contexto y evidencias.

    Necesario porque la sesión es async: acceder a una relación no
    cargada fuera de un `await` explícito revienta con
    `MissingGreenlet`. Sin esto (bug corregido en DEC-030), además,
    `DecisionRecord.contexto` y `DecisionRecord.evidencias` no existían
    como atributos y la API siempre devolvía context_data=None y
    evidencias=[] aunque estuvieran persistidos.
    """
    return (selectinload(DecisionRecord.contexto), selectinload(DecisionRecord.evidencias))


def _a_decision_output(decision: DecisionRecord) -> DecisionOutput:
    """Convierte un DecisionRecord ya cargado (con contexto y evidencias)
    en su DecisionOutput.

    Se hace a mano, en vez de dejar que Pydantic use `from_attributes`
    directamente sobre el ORM, porque `context_data` vive en la relación
    `contexto` (un DecisionContext), no como atributo plano de
    DecisionRecord — usar `from_attributes` directo es exactamente lo
    que producía el bug de DEC-030 (siempre None / [] en la respuesta).
    """
    return DecisionOutput(
        id=decision.id,
        decision_type=decision.decision_type,
        entity_type=decision.entity_type,
        entity_id=decision.entity_id,
        action=decision.action,
        user_id=decision.user_id,
        reason=decision.reason,
        creado_en=decision.creado_en,
        context_data=decision.contexto.context_data if decision.contexto else None,
        evidencias=[
            EvidenciaDetalle.model_validate(evidencia, from_attributes=True)
            for evidencia in decision.evidencias
        ],
    )


async def registrar_decision(
    db_session: AsyncSession, entrada: DecisionInput
) -> DecisionOutput:
    """Registra una decisión humana y, si aplica, ejecuta el cambio de
    estado real sobre la entidad decidida.

    Args:
        db_session: sesión async de SQLAlchemy.
        entrada: la decisión ya validada por DecisionInput.

    Returns:
        DecisionOutput: la decisión recién creada, ya persistida, con su
        contexto y evidencias (si se enviaron) incluidos en la respuesta.

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

    decision_completa = await _obtener_decision_orm_por_id(
        db_session=db_session, decision_id=decision.id
    )
    assert decision_completa is not None  # acabamos de crearla en esta misma transacción
    return _a_decision_output(decision_completa)


async def _obtener_decision_orm_por_id(
    db_session: AsyncSession, decision_id: uuid.UUID
) -> DecisionRecord | None:
    """Busca el DecisionRecord ORM por su ID, con contexto y evidencias
    ya cargados (ver `_opciones_carga_completa`)."""
    consulta = (
        select(DecisionRecord)
        .where(DecisionRecord.id == decision_id)
        .options(*_opciones_carga_completa())
    )
    resultado = await db_session.execute(consulta)
    return resultado.scalar_one_or_none()


async def obtener_decision_por_id(
    db_session: AsyncSession, decision_id: uuid.UUID
) -> DecisionOutput | None:
    """Busca una decisión por su ID, ya convertida a DecisionOutput con
    su contexto y evidencias incluidos."""
    decision = await _obtener_decision_orm_por_id(
        db_session=db_session, decision_id=decision_id
    )
    return _a_decision_output(decision) if decision is not None else None