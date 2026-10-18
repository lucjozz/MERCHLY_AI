"""Pydantic schemas para autenticación (docs/013-Seguridad/01-)."""

import uuid

from pydantic import BaseModel


class LoginInput(BaseModel):
    """Entrada de login (contrato, sección 4.1)."""

    email: str
    password: str


class LoginOutput(BaseModel):
    """Salida de un login exitoso (contrato, sección 4.1)."""

    access_token: str
    token_type: str = "bearer"
    expira_en: int


class UsuarioActual(BaseModel):
    """El usuario autenticado actual (contrato, sección 4.2)."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    nombre: str
    rol: str
    activo: bool