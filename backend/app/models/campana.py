"""Model for ``campanas``: historial de campañas (docs/004-Backend/03, sección 1).

Datos de negocio: protegidos por RLS por organización.
"""

import uuid

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo, DeOrganizacion


class Campana(DeOrganizacion, ConMarcaDeTiempo, Base):
    __tablename__ = "campanas"

    creado_por: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    productos_candidato_ids: Mapped[list] = mapped_column(JSONB, nullable=False)
    canales: Mapped[list] = mapped_column(JSONB, nullable=False)
    tono: Mapped[str] = mapped_column(String(20), nullable=False)
    idioma: Mapped[str] = mapped_column(String(2), nullable=False)
    modelo: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # {"angulos": [...], "copy_por_canal": {canal: [{titulo, cuerpo}]},
    #  "publico_objetivo": str, "advertencias": [...]}
    contenido: Mapped[dict] = mapped_column(JSONB, nullable=False)
    editada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
