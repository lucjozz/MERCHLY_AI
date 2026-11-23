"""Model for ``invitaciones`` (docs/004-Backend/03, sección 5).

El token solo existe en el link que se le pasa a la persona invitada; en la
base se guarda su SHA-256. Sin RLS (se busca por token antes de saber la
organización): la app filtra por organización en la administración.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo, DeOrganizacion


class Invitacion(DeOrganizacion, ConMarcaDeTiempo, Base):
    __tablename__ = "invitaciones"

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(30), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    aceptada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    revocada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    creado_por: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
