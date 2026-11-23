"""Schemas de gestión del equipo (docs/004-Backend/03, sección 5)."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.auth import normalizar_email
from app.schemas.base import EntradaEstricta

Rol = Literal["admin_principal", "responsable_tecnico", "responsable_negocio", "usuario_operativo"]


class MiembroSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    nombre: str
    rol: str
    activo: bool
    creado_en: datetime


class InvitacionEntrada(EntradaEstricta):
    email: str = Field(min_length=3, max_length=255)
    rol: Rol

    normalizar_email_valido = field_validator("email")(normalizar_email)

    @field_validator("email")
    @classmethod
    def formato_email(cls, valor: str) -> str:
        if "@" not in valor or valor.startswith("@") or valor.endswith("@") or " " in valor:
            raise ValueError("email inválido")
        return valor


class InvitacionSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    rol: str
    expira_en: datetime
    aceptada_en: datetime | None
    revocada_en: datetime | None
    creado_en: datetime


class InvitacionCreada(InvitacionSalida):
    """Solo en la respuesta de creación: el token no se puede volver a ver."""

    token: str


class MiembroCambio(EntradaEstricta):
    rol: Rol | None = None
    activo: bool | None = None


class AceptarInvitacionEntrada(EntradaEstricta):
    """Las contraseñas no se recortan (igual que en el login)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    token: str = Field(min_length=12, max_length=40)  # código de invitación (con o sin guiones)
    nombre: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=12, max_length=128)
