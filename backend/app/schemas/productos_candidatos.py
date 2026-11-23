"""Schemas de productos candidatos (salida). Ver 013-04, sección 5:
el listado usa un schema resumido; el detalle, el completo."""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.investigador_producto import NivelEstimado

TAMANO_PAGINA_MAXIMO = 100


class EstadoProducto(str, Enum):
    CANDIDATO = "candidato"
    EN_REVISION = "en_revision"
    EN_CATALOGO = "en_catalogo"
    DESCARTADO = "descartado"


class ProductoCandidatoResumen(BaseModel):
    """Lo necesario para una fila del listado."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre_producto: str
    categoria: str
    mercado_objetivo: str
    precio_estimado_proveedor: float | None = None
    precio_sugerido_venta: float | None = None
    nivel_demanda_estimado: NivelEstimado
    nivel_competencia_estimado: NivelEstimado
    riesgos_identificados: list[str]
    estado: EstadoProducto
    creado_en: datetime


class ProductoCandidatoDetalle(ProductoCandidatoResumen):
    """Detalle completo de un producto."""

    fuentes_evidencia: list[str]
    investigacion_id: uuid.UUID


class ProductosCandidatosListado(BaseModel):
    """Una página de resultados de productos candidatos."""

    productos: list[ProductoCandidatoResumen]
    total: int = Field(ge=0)
    pagina: int = Field(ge=1)
    tamano_pagina: int = Field(ge=1, le=TAMANO_PAGINA_MAXIMO)
