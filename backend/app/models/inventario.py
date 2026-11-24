"""Models del inventario del negocio (docs/007-Agentes/08, sección 2).

Una sola tabla con dos vistas: el inventario privado del dueño (todos los
campos) y el catálogo público que usa la IA (solo productos publicados y
solo campos públicos; ver ``app/services/inventario.py::catalogo_publico``).
"""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, LargeBinary, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo, DeOrganizacion

ORIGENES = ("aprobado", "importado", "manual")


class InventarioProducto(DeOrganizacion, ConMarcaDeTiempo, Base):
    __tablename__ = "inventario_productos"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_inventario_stock"),
        CheckConstraint("stock_reservado >= 0 AND stock_reservado <= stock", name="ck_inventario_reservado"),
        CheckConstraint("origen IN ('aprobado', 'importado', 'manual')", name="ck_inventario_origen"),
    )

    # Públicos (también los ve la IA si el producto está publicado)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    especificaciones: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    precio_venta: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    publicado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    # Privados (solo el dueño)
    sku: Mapped[str | None] = mapped_column(String(60), nullable=True)
    costo_unitario: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    gastos_unitarios: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    proveedor: Mapped[str | None] = mapped_column(String(200), nullable=True)
    notas_internas: Mapped[str | None] = mapped_column(Text, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    stock_reservado: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    origen: Mapped[str] = mapped_column(String(20), nullable=False, default="manual", server_default="manual")
    producto_candidato_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("productos_candidatos.id"), nullable=True
    )


class InventarioFoto(DeOrganizacion, ConMarcaDeTiempo, Base):
    """Foto ya re-codificada (WebP, sin metadatos). Se sirve solo con sesión de la organización."""

    __tablename__ = "inventario_fotos"

    producto_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventario_productos.id"), nullable=False, index=True
    )
    orden: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="image/webp")
    tamano: Mapped[int] = mapped_column(Integer, nullable=False)
    contenido: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
