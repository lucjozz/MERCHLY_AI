"""Shared SQLAlchemy declarative base and mixins.

Implements the conventions defined in
``docs/006-BaseDatos/01-Convenciones-de-Base-de-Datos.md``: UUID primary
keys and the standard timestamp columns (``creado_en``, ``actualizado_en``,
``eliminado_en``) that every table must have.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base shared by every model in the application."""


class ConMarcaDeTiempo:
    """Mixin adding the standard timestamp columns to a model.

    See ``docs/006-BaseDatos/01-Convenciones-de-Base-de-Datos.md``,
    section 3 ("Timestamps Obligatorios").

    Attributes:
        id: UUID primary key, generated in the application.
        creado_en: creation timestamp, set once by the database.
        actualizado_en: last-update timestamp, refreshed on every UPDATE.
        eliminado_en: soft-delete timestamp; NULL while the row is active.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    eliminado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
