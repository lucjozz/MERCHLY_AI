import uuid 
from datetime import datetime
from sqlalchemy import  DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column


from app.models.base import Base, ConMarcaDeTiempo

ACCIONES_VALIDAS = ["approve","discard","request_review"]

class DecisionRecord(ConMarcaDeTiempo, Base):
    """Una decisión humana sobre una entidad del sistema (ej. un producto
    candidato). Es el registro central del que dependen context, evidence
    y outcomes.

    Attributes:
        decision_type: tipo de decisión (ej. "product_selection").
        entity_type: tipo de entidad sobre la que se decide (ej.
            "product_candidate").
        entity_id: UUID de la entidad concreta (ej. el id de un
            ProductoCandidato). No es una foreign key real, porque
            decision_type/entity_type pueden apuntar a distintas tablas
            en el futuro (no solo productos candidatos).
        action: la acción tomada (approve/discard/request_review).
        user_id: quién tomó la decisión. No es una foreign key todavía
            porque no existe tabla de usuarios (013-Seguridad pendiente).
        reason: motivo en texto libre, dado por el humano.
    """

    __tablename__ = "decision_records"

    decision_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    user_id: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
class DecisionContext(ConMarcaDeTiempo, Base):
    """La 'foto' de la información disponible al momento de decidir.

    Se guarda separada del producto en sí porque los datos del producto
    pueden cambiar después — la decisión debe conservar el contexto tal
    como era en ese momento, no el estado actual.

    Attributes:
        decision_id: la decisión a la que pertenece este contexto.
        context_data: los datos del contexto, en formato flexible (mercado,
            categoría, precio, demanda, competencia, margen, etc.).
    """

    __tablename__ = "decision_context"

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("decision_records.id"),
        nullable=False,
    )
    context_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
class DecisionEvidence(ConMarcaDeTiempo, Base):
    """Una fuente de evidencia que respaldó una decisión.

    Separada de DecisionContext a propósito: el contexto es "qué datos
    había", la evidencia es "de dónde salieron esos datos" — son cosas
    distintas, y una decisión puede tener varias fuentes de evidencia.

    Attributes:
        decision_id: la decisión a la que pertenece esta evidencia.
        source_type: tipo de fuente (ej. "market_research").
        source_url: URL de la fuente, si aplica.
        source_title: título descriptivo de la fuente.
        evidence: el contenido relevante extraído de la fuente.
    """

    __tablename__ = "decision_evidence"

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("decision_records.id"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    evidence: Mapped[str] = mapped_column(Text, nullable=False) 
class DecisionOutcome(ConMarcaDeTiempo, Base):
    """El resultado real, medido después de ejecutar una decisión.

    Es la pieza que conecta 'qué se decidió' con 'qué pasó realmente' —
    la base de lo que un futuro agente de automatización necesita para
    aprender qué decisiones funcionaron.

    Attributes:
        decision_id: la decisión a la que pertenece este resultado.
        outcome_type: tipo de resultado medido (ej. "product_performance").
        outcome_data: los datos del resultado, en formato flexible
            (ventas, ingresos, ganancia, ROI, etc.).
        measured_at: cuándo se midió este resultado — puede ser mucho
            después de la decisión en sí (ej. ventas a los 30 días).
    """

    __tablename__ = "decision_outcomes"

    decision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("decision_records.id"),
        nullable=False,
    )
    outcome_type: Mapped[str] = mapped_column(String(50), nullable=False)
    outcome_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    measured_at: Mapped[datetime] = mapped_column(nullable=False)