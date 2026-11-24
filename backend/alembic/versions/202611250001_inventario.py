"""inventario

Revision ID: 202611250001
Revises: 202611240003
Create Date: 2026-11-23 00:00:00

docs/007-Agentes/08 (DEC-039): inventario del negocio (vista privada del dueño
y catálogo público de la IA sobre la misma tabla) y sus fotos. RLS por
organización; el rol de la app no puede borrar filas (borrado lógico), salvo
fotos, que se borran de verdad para no guardar imágenes que el dueño sacó.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202611250001"
down_revision: Union[str, None] = "202611240003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROL_APP = "merchly_app"
POLITICA = "organizacion_id = NULLIF(current_setting('app.organizacion_id', true), '')::uuid"


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
    ]


def _rls(tabla: str) -> None:
    op.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {tabla} FORCE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY aislamiento_organizacion ON {tabla} USING ({POLITICA}) WITH CHECK ({POLITICA})")


def upgrade() -> None:
    op.create_table(
        "inventario_productos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacion_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizaciones.id"), nullable=False),
        sa.Column("nombre", sa.String(200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("especificaciones", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("precio_venta", sa.Numeric(12, 2), nullable=True),
        sa.Column("publicado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sku", sa.String(60), nullable=True),
        sa.Column("costo_unitario", sa.Numeric(12, 2), nullable=True),
        sa.Column("gastos_unitarios", sa.Numeric(12, 2), nullable=True),
        sa.Column("proveedor", sa.String(200), nullable=True),
        sa.Column("notas_internas", sa.Text(), nullable=True),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("stock_reservado", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("origen", sa.String(20), nullable=False, server_default="manual"),
        sa.Column(
            "producto_candidato_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("productos_candidatos.id"), nullable=True
        ),
        *_timestamps(),
        sa.CheckConstraint("stock >= 0", name="ck_inventario_stock"),
        sa.CheckConstraint("stock_reservado >= 0 AND stock_reservado <= stock", name="ck_inventario_reservado"),
        sa.CheckConstraint("origen IN ('aprobado', 'importado', 'manual')", name="ck_inventario_origen"),
        sa.CheckConstraint("precio_venta IS NULL OR precio_venta >= 0", name="ck_inventario_precio"),
        sa.CheckConstraint("costo_unitario IS NULL OR costo_unitario >= 0", name="ck_inventario_costo"),
        sa.CheckConstraint("gastos_unitarios IS NULL OR gastos_unitarios >= 0", name="ck_inventario_gastos"),
    )
    op.create_index("ix_inventario_productos_organizacion_id", "inventario_productos", ["organizacion_id"])
    _rls("inventario_productos")
    op.execute(f"GRANT SELECT, INSERT, UPDATE ON inventario_productos TO {ROL_APP}")

    op.create_table(
        "inventario_fotos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacion_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizaciones.id"), nullable=False),
        sa.Column("producto_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inventario_productos.id"), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tipo", sa.String(20), nullable=False, server_default="image/webp"),
        sa.Column("tamano", sa.Integer(), nullable=False),
        sa.Column("contenido", sa.LargeBinary(), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("tamano > 0 AND tamano <= 2097152", name="ck_inventario_fotos_tamano"),
    )
    op.create_index("ix_inventario_fotos_organizacion_id", "inventario_fotos", ["organizacion_id"])
    op.create_index("ix_inventario_fotos_producto_id", "inventario_fotos", ["producto_id"])
    _rls("inventario_fotos")
    op.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON inventario_fotos TO {ROL_APP}")


def downgrade() -> None:
    for tabla in ("inventario_fotos", "inventario_productos"):
        op.execute(f"DROP POLICY IF EXISTS aislamiento_organizacion ON {tabla}")
        op.drop_table(tabla)
