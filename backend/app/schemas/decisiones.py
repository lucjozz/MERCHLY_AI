import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AccionDecision(str, Enum):
    """Las tres acciones humanas posibles sobre una entidad."""

    APROBAR = "approve"
    DESCARTAR = "discard"
    SOLICITAR_REVISION = "request_review"


class EvidenciaInput(BaseModel):
    """Una fuente de evidencia que respalda la decisión."""

    source_type: str
    source_url: str | None = None
    source_title: str | None = None
    evidence: str


class DecisionInput(BaseModel):
    """Entrada para registrar una nueva decisión humana."""

    decision_type: str
    entity_type: str
    entity_id: uuid.UUID
    action: AccionDecision
    user_id: str
    reason: str = Field(min_length=1)
    context_data: dict | None = None
    evidencias: list[EvidenciaInput] = Field(default_factory=list)
class EvidenciaDetalle(BaseModel):
    """Una evidencia ya guardada, tal como vive en la base de datos."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    source_type: str
    source_url: str | None
    source_title: str | None
    evidence: str


class DecisionOutput(BaseModel):
    """Una decisión ya registrada, con su contexto y evidencias."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    decision_type: str
    entity_type: str
    entity_id: uuid.UUID
    action: AccionDecision
    user_id: str
    reason: str
    creado_en: datetime
    context_data: dict | None = None
    evidencias: list[EvidenciaDetalle] = Field(default_factory=list)