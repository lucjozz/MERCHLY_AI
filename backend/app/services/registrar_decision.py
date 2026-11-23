"""Servicio para registrar y consultar decisiones humanas. Sin FastAPI.

Máquina de estados de productos (013-04, sección 6.1):

    candidato   --approve-->        en_catalogo (final)
    candidato   --discard-->        descartado  (final)
    candidato   --request_review--> en_revision
    en_revision --approve-->        en_catalogo (final)
    en_revision --discard-->        descartado  (final)

Cualquier otra combinación lanza ``TransicionInvalidaError`` (409) y NO se
registra nada. La fila del producto se bloquea (``FOR UPDATE``) durante la
decisión: dos envíos simultáneos se serializan y el segundo ve el estado
ya cambiado (y recibe 409). Las decisiones son append-only: el rol de la
app no tiene UPDATE ni DELETE sobre decision_*.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.decisiones import DecisionContext, DecisionEvidence, DecisionRecord
from app.schemas.decisiones import AccionDecision, DecisionInput, DecisionOutput, EvidenciaDetalle
from app.services.consulta_productos_candidatos import obtener_producto_candidato_por_id

ENTIDAD_PRODUCTO = "product_candidate"

TRANSICIONES: dict[tuple[str, AccionDecision], str] = {
    ("candidato", AccionDecision.APROBAR): "en_catalogo",
    ("candidato", AccionDecision.DESCARTAR): "descartado",
    ("candidato", AccionDecision.SOLICITAR_REVISION): "en_revision",
    ("en_revision", AccionDecision.APROBAR): "en_catalogo",
    ("en_revision", AccionDecision.DESCARTAR): "descartado",
}


class EntidadNoEncontradaError(ValueError):
    """La entidad no existe o es de otra organización (-> 404)."""


class TransicionInvalidaError(Exception):
    """La acción no es válida para el estado actual (-> 409)."""

    def __init__(self, estado_actual: str, accion: AccionDecision) -> None:
        self.estado_actual = estado_actual
        self.accion = accion
        super().__init__(
            f"No se puede aplicar '{accion.value}' a un producto en estado '{estado_actual}'."
        )


def _opciones_carga_completa():
    """Carga ansiosa de contexto y evidencias (sesión async, ver DEC-030)."""
    return (selectinload(DecisionRecord.contexto), selectinload(DecisionRecord.evidencias))


def _a_decision_output(decision: DecisionRecord, estado_resultante: str | None = None) -> DecisionOutput:
    return DecisionOutput(
        id=decision.id,
        decision_type=decision.decision_type,
        entity_type=decision.entity_type,
        entity_id=decision.entity_id,
        action=decision.action,
        user_id=decision.user_id,
        reason=decision.reason,
        creado_en=decision.creado_en,
        estado_resultante=estado_resultante,
        context_data=decision.contexto.context_data if decision.contexto else None,
        evidencias=[
            EvidenciaDetalle.model_validate(evidencia, from_attributes=True)
            for evidencia in decision.evidencias
        ],
    )


async def registrar_decision(
    db_session: AsyncSession,
    entrada: DecisionInput,
    user_id: uuid.UUID,
    organizacion_id: uuid.UUID,
) -> DecisionOutput:
    """Registra una decisión humana y aplica la transición de estado.

    Raises:
        EntidadNoEncontradaError: el producto no existe / es de otra org.
        TransicionInvalidaError: la acción no vale para el estado actual.
    """
    estado_resultante: str | None = None
    if entrada.entity_type == ENTIDAD_PRODUCTO:
        producto = await obtener_producto_candidato_por_id(
            db_session, organizacion_id, entrada.entity_id, para_actualizar=True
        )
        if producto is None:
            raise EntidadNoEncontradaError("No existe ese producto.")
        estado_actual = producto.estado
        estado_resultante = TRANSICIONES.get((estado_actual, entrada.action))
        if estado_resultante is None:
            # Se lee el estado ANTES del rollback: después el objeto queda
            # expirado y leerlo dispararía IO fuera de contexto async.
            await db_session.rollback()
            raise TransicionInvalidaError(estado_actual, entrada.action)
        producto.estado = estado_resultante

    decision = DecisionRecord(
        id=uuid.uuid4(),
        organizacion_id=organizacion_id,
        decision_type=entrada.decision_type,
        entity_type=entrada.entity_type,
        entity_id=entrada.entity_id,
        action=entrada.action.value,
        user_id=str(user_id),
        reason=entrada.reason,
    )
    db_session.add(decision)
    await db_session.flush()

    if entrada.context_data is not None:
        db_session.add(
            DecisionContext(
                id=uuid.uuid4(),
                organizacion_id=organizacion_id,
                decision_id=decision.id,
                context_data=entrada.context_data,
            )
        )
    for evidencia_input in entrada.evidencias:
        db_session.add(
            DecisionEvidence(
                id=uuid.uuid4(),
                organizacion_id=organizacion_id,
                decision_id=decision.id,
                source_type=evidencia_input.source_type,
                source_url=evidencia_input.source_url,
                source_title=evidencia_input.source_title,
                evidence=evidencia_input.evidence,
            )
        )

    await db_session.commit()

    completa = await _obtener_decision_orm_por_id(db_session, organizacion_id, decision.id)
    if completa is None:  # no debería pasar: se acaba de crear en esta organización
        raise RuntimeError("La decisión recién creada no se pudo releer.")
    return _a_decision_output(completa, estado_resultante)


async def _obtener_decision_orm_por_id(
    db_session: AsyncSession, organizacion_id: uuid.UUID, decision_id: uuid.UUID
) -> DecisionRecord | None:
    consulta = (
        select(DecisionRecord)
        .where(DecisionRecord.id == decision_id, DecisionRecord.organizacion_id == organizacion_id)
        .options(*_opciones_carga_completa())
    )
    return (await db_session.execute(consulta)).scalar_one_or_none()


async def obtener_decision_por_id(
    db_session: AsyncSession, organizacion_id: uuid.UUID, decision_id: uuid.UUID
) -> DecisionOutput | None:
    """Una decisión de la organización, o None (404, también si es de otra)."""
    decision = await _obtener_decision_orm_por_id(db_session, organizacion_id, decision_id)
    return _a_decision_output(decision) if decision is not None else None
