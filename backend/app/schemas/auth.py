"""Pydantic schemas para autenticación (docs/013-Seguridad/01 y 04)."""

import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.base import EntradaEstricta


def normalizar_email(valor: str) -> str:
    """Emails siempre en minúsculas y sin espacios (013-04, sección 3.2)."""
    return valor.strip().lower()


class LoginInput(EntradaEstricta):
    """Entrada de login. Límite de 128 caracteres en la contraseña: una
    contraseña enorme no llega a bcrypt (anti-DoS). Las contraseñas NO se
    recortan (un espacio al final es parte de la contraseña)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    normalizar_email_valido = field_validator("email")(normalizar_email)


class RefreshInput(EntradaEstricta):
    refresh_token: str = Field(min_length=20, max_length=128)


class LogoutInput(EntradaEstricta):
    refresh_token: str | None = Field(default=None, min_length=20, max_length=128)


class GoogleLoginInput(EntradaEstricta):
    id_token: str = Field(min_length=20, max_length=4096)


class SesionOutput(BaseModel):
    """Par de tokens. Solo lo recibe el BFF de Next (servidor), que los
    guarda en cookies HttpOnly: el navegador nunca los ve."""

    access_token: str
    token_type: str = "bearer"  # noqa: S105 (tipo de token, no un secreto)
    expira_en: int
    refresh_token: str
    refresh_expira_en: int


class UsuarioActual(BaseModel):
    """El usuario autenticado actual."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    nombre: str
    rol: str
    activo: bool
    organizacion_id: uuid.UUID
    organizacion_nombre: str | None = None
