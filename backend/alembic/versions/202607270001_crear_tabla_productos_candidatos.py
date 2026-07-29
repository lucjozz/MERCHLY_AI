"""crear_tabla_productos_candidatos

Revision ID: 202607270001
Revises:
Create Date: 2026-07-27 00:00:00

Crea la tabla `productos_candidatos`, documentada en
`docs/006-BaseDatos/02-Esquema-Fase1.md`, que persiste los resultados del
Agente Investigador de Producto
(`docs/007-Agentes/03-Agente-Investigador-de-Producto.md`).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "202607270001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "productos_candidatos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nombre_producto", sa.String(length=255), nullable=False),
        sa.Column("categoria", sa.String(length=120), nullable=False),
        sa.Column("mercado_objetivo", sa.String(length=2), nullable=False),
        sa.Column("precio_estimado_proveedor", sa.Numeric(12, 2), nullable=True),
        sa.Column("precio_sugerido_venta", sa.Numeric(12, 2), nullable=True),
        sa.Column("nivel_demanda_estimado", sa.String(length=10), nullable=False),
        sa.Column("nivel_competencia_estimado", sa.String(length=10), nullable=False),
        sa.Column(
            "fuentes_evidencia",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "riesgos_identificados",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "estado",
            sa.String(length=20),
            nullable=False,
            server_default="candidato",
        ),
        sa.Column("investigacion_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "nivel_demanda_estimado IN ('alto', 'medio', 'bajo')",
            name="ck_productos_candidatos_nivel_demanda",
        ),
        sa.CheckConstraint(
            "nivel_competencia_estimado IN ('alto', 'medio', 'bajo')",
            name="ck_productos_candidatos_nivel_competencia",
        ),
        sa.CheckConstraint(
            "estado IN ('candidato', 'en_catalogo', 'descartado')",
            name="ck_productos_candidatos_estado",
        ),
    )
    op.create_index(
        "ix_productos_candidatos_categoria",
        "productos_candidatos",
        ["categoria"],
    )
    op.create_index(
        "ix_productos_candidatos_investigacion_id",
        "productos_candidatos",
        ["investigacion_id"],
    )
    op.create_index(
        "ix_productos_candidatos_estado",
        "productos_candidatos",
        ["estado"],
    )


def downgrade() -> None:
    op.drop_index("ix_productos_candidatos_estado", table_name="productos_candidatos")
    op.drop_index(
        "ix_productos_candidatos_investigacion_id", table_name="productos_candidatos"
    )
    op.drop_index("ix_productos_candidatos_categoria", table_name="productos_candidatos")
    op.drop_table("productos_candidatos")
