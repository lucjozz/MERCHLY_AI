"""Model for ``usuarios`` (docs/013-Seguridad/01 y 04)."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo

ROLES_VALIDOS = (
    "admin_principal",
    "responsable_tecnico",
    "responsable_negocio",
    "usuario_operativo",
)


class Usuario(ConMarcaDeTiempo, Base):
    """Un usuario humano del sistema.

    Attributes:
        organizacion_id: el negocio al que pertenece. Los roles valen solo
            dentro de esa organización.
        email: identificador de login, único y siempre en minúsculas.
        password_hash: hash bcrypt. ``None`` para usuarios que solo entran
            con Google. Nunca se guarda ni se loguea la contraseña.
        google_sub: identificador estable de la cuenta de Google vinculada.
        nombre: nombre para mostrar.
        rol: uno de los 4 roles de 02-Roles-y-Permisos.md.
        activo: un usuario inactivo no puede autenticarse.
        token_version: se incrementa para invalidar todas las sesiones del
            usuario (cambio de contraseña, cierre forzado).
    """

    __tablename__ = "usuarios"

    organizacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizaciones.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_sub: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    token_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
