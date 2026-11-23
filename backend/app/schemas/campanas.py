"""Schemas del historial de campañas (docs/004-Backend/03, sección 1)."""

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import EntradaEstricta
from app.schemas.marketing import CanalMarketing

Texto300 = Annotated[str, Field(min_length=1, max_length=300)]


class CopyEditable(EntradaEstricta):
    titulo: str = Field(max_length=150)
    cuerpo: str = Field(max_length=1500)


class ContenidoCampana(BaseModel):
    angulos: list[str] = Field(default_factory=list)
    copy_por_canal: dict[CanalMarketing, list[CopyEditable]] = Field(default_factory=dict)
    publico_objetivo: str = ""
    advertencias: list[str] = Field(default_factory=list)


class CampanaEdicion(EntradaEstricta):
    """Lo que una persona puede editar. Nunca organización, autor ni modelo."""

    titulo: str | None = Field(default=None, min_length=1, max_length=150)
    angulos: list[Texto300] | None = Field(default=None, max_length=6)
    copy_por_canal: dict[CanalMarketing, Annotated[list[CopyEditable], Field(max_length=5)]] | None = None
    publico_objetivo: str | None = Field(default=None, max_length=600)


class CampanaResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    titulo: str
    canales: list[CanalMarketing]
    tono: str
    modelo: str | None
    editada: bool
    creado_en: datetime


class CampanaDetalle(CampanaResumen):
    productos_candidato_ids: list[uuid.UUID]
    idioma: str
    contenido: ContenidoCampana
    actualizado_en: datetime


class CampanasListado(BaseModel):
    campanas: list[CampanaResumen]
    total: int
    pagina: int
    tamano_pagina: int
