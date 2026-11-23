"""Model for ``refresh_tokens`` (docs/013-Seguridad/04, sección 3).

El refresh token nunca se guarda en claro: solo su SHA-256. Cada uso lo
ROTA (``rotado_en``) y nace uno nuevo de la misma ``familia``. Reusar un
token rotado dentro de la ventana de gracia (requests paralelos) emite
otro hermano; fuera de la ventana se asume robo y se REVOCA (``revocado_en``)
toda la familia. Logout también revoca la familia.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo


class RefreshToken(ConMarcaDeTiempo, Base):
    """Un refresh token emitido a un usuario."""

    __tablename__ = "refresh_tokens"

    usuario_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    familia: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rotado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    revocado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
