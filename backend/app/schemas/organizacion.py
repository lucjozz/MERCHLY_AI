"""Schemas del perfil del negocio y del uso del plan (docs/004-Backend/03, secciones 3 y 6)."""

import re
import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.base import EntradaEstricta


class PerfilEntrada(EntradaEstricta):
    """Perfil que completa el admin en el onboarding o en Configuración."""

    nombre: str = Field(min_length=2, max_length=120)
    pais: str = Field(min_length=2, max_length=2)
    rubro: str = Field(min_length=2, max_length=120)
    presupuesto_mensual: Decimal | None = Field(default=None, ge=0, le=Decimal("100000000"))
    moneda: Literal["BOB", "USD"] = "BOB"
    tipo_cambio: Decimal | None = Field(default=None, gt=0, le=Decimal("100000"))
    costo_envio_unitario_usd: Decimal = Field(default=Decimal("0"), ge=0, le=Decimal("100000"))
    impuestos_importacion_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)

    @field_validator("pais")
    @classmethod
    def pais_iso(cls, valor: str) -> str:
        valor = valor.upper()
        if not re.fullmatch(r"[A-Z]{2}", valor):
            raise ValueError("pais debe ser un código ISO de 2 letras")
        return valor


class OrganizacionSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    plan: str
    pais: str
    rubro: str | None
    presupuesto_mensual: float | None
    moneda: str
    tipo_cambio: float | None
    costo_envio_unitario_usd: float
    impuestos_importacion_pct: float
    onboarding_completo: bool


class UsoCuota(BaseModel):
    agente: str
    limite_por_hora: int
    usadas: int
    restantes: int
    se_renueva_en_segundos: int


class UsoPlan(BaseModel):
    plan: str
    cuotas: list[UsoCuota]
    disponible: bool = True  # False si Redis no respondió (no se pudo medir)
