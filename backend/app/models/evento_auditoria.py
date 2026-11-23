"""Model for ``eventos_auditoria`` (docs/013-Seguridad/06). Append-only por privilegios de base."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class EventoAuditoria(Base):
    """Todos los valores se generan en la app: el INSERT no necesita RETURNING.

    Importante: con RLS, un INSERT ... RETURNING exige que la fila devuelta
    cumpla la política de LECTURA; un login (sin organización fijada) fallaba.
    """

    __tablename__ = "eventos_auditoria"
    __mapper_args__ = {"eager_defaults": False}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organizacion_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizaciones.id"), nullable=True
    )
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)
    objetivo_tipo: Mapped[str | None] = mapped_column(String(30), nullable=True)
    objetivo_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    detalle: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"), default=dict)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc), nullable=False
    )
