import uuid 
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.investigador_producto import NivelEstimado

class EstadoProducto(str, Enum):

    CANDIDATO = "candidato"
    EN_CATALOGO = "en_catalogo"
    DESCARTADO = "descartado"

class ProductoCandidatoDetalle(BaseModel):

    model_config = {"from_attributes": True}

    id: uuid.UUID
    nombre_producto: str
    categoria: str
    mercado_objetivo: str
    precio_estimado_proveedor: float | None = None
    precio_sugerido_venta: float | None = None
    nivel_demanda_estimado: NivelEstimado
    nivel_competencia_estimado: NivelEstimado
    fuentes_evidencia: list[str]
    riesgos_identificados: list[str]
    estado: EstadoProducto
    investigacion_id: uuid.UUID
    creado_en: datetime

class ProductosCandidatosListado(BaseModel):
    """Una página de resultados de productos candidatos."""

    productos: list[ProductoCandidatoDetalle]
    total: int = Field(ge=0)
    pagina: int = Field(ge=1)
    tamano_pagina: int = Field(ge=1, le=100)          