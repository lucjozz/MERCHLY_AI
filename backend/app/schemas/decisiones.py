"""Schemas de decisiones humanas (013-04, secciones 5 y 6)."""

import json
import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.base import EntradaEstricta

CONTEXT_DATA_MAX_BYTES = 16_384


class AccionDecision(str, Enum):
    """Las tres acciones humanas posibles sobre una entidad."""

    APROBAR = "approve"
    DESCARTAR = "discard"
    SOLICITAR_REVISION = "request_review"


class EvidenciaInput(EntradaEstricta):
    """Una fuente de evidencia que respalda la decisión (topes = columnas)."""

    source_type: str = Field(min_length=1, max_length=50)
    source_url: str | None = Field(default=None, max_length=500)
    source_title: str | None = Field(default=None, max_length=255)
    evidence: str = Field(min_length=1, max_length=5_000)

    @field_validator("source_url")
    @classmethod
    def solo_http(cls, valor: str | None) -> str | None:
        """Evita esquemas peligrosos (javascript:, data:) en URLs que se muestran."""
        if valor and not valor.lower().startswith(("http://", "https://")):
            raise ValueError("source_url debe empezar con http:// o https://")
        return valor


class DecisionInput(EntradaEstricta):
    """Entrada para registrar una decisión. ``user_id`` y ``organizacion_id``
    salen del token, NUNCA del body (extra="forbid" los rechaza)."""

    decision_type: str = Field(min_length=1, max_length=50)
    entity_type: str = Field(min_length=1, max_length=50)
    entity_id: uuid.UUID
    action: AccionDecision
    reason: str = Field(min_length=1, max_length=2_000)
    context_data: dict | None = None
    evidencias: list[EvidenciaInput] = Field(default_factory=list, max_length=20)

    @field_validator("context_data")
    @classmethod
    def context_data_acotado(cls, valor: dict | None) -> dict | None:
        if valor is not None and len(json.dumps(valor, default=str)) > CONTEXT_DATA_MAX_BYTES:
            raise ValueError(f"context_data supera {CONTEXT_DATA_MAX_BYTES} bytes")
        return valor


class EvidenciaDetalle(BaseModel):
    """Una evidencia ya guardada."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_type: str
    source_url: str | None
    source_title: str | None
    evidence: str


class DecisionOutput(BaseModel):
    """Una decisión ya registrada, con su contexto y evidencias."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    decision_type: str
    entity_type: str
    entity_id: uuid.UUID
    action: AccionDecision
    user_id: str
    reason: str
    creado_en: datetime
    estado_resultante: str | None = None
    context_data: dict | None = None
    evidencias: list[EvidenciaDetalle] = Field(default_factory=list)
