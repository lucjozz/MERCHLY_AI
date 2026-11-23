"""eventos_auditoria

Revision ID: 202611240003
Revises: 202611240002
Create Date: 2026-11-24 02:00:00

Bitácora de auditoría de seguridad (docs/013-Seguridad/06, DEC-037).
Append-only: el rol de la app solo puede INSERT y SELECT. RLS: cada
organización lee solo sus eventos; insertar se permite siempre (un login
fallido ocurre antes de saber la organización).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202611240003"
down_revision: Union[str, None] = "202611240002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ORG_ACTUAL = "NULLIF(current_setting('app.organizacion_id', true), '')::uuid"


def upgrade() -> None:
    op.create_table(
        "eventos_auditoria",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacion_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizaciones.id"), nullable=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("accion", sa.String(50), nullable=False),
        sa.Column("objetivo_tipo", sa.String(30), nullable=True),
        sa.Column("objetivo_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("detalle", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("user_agent", sa.String(200), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_eventos_auditoria_org_fecha", "eventos_auditoria", ["organizacion_id", "creado_en"])
    op.create_index("ix_eventos_auditoria_accion", "eventos_auditoria", ["accion"])
    op.execute("ALTER TABLE eventos_auditoria ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE eventos_auditoria FORCE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY leer_propia_organizacion ON eventos_auditoria FOR SELECT USING (organizacion_id = {ORG_ACTUAL})")
    op.execute("CREATE POLICY registrar_eventos ON eventos_auditoria FOR INSERT WITH CHECK (true)")
    op.execute("GRANT SELECT, INSERT ON eventos_auditoria TO merchly_app")  # sin UPDATE ni DELETE


def downgrade() -> None:
    op.drop_table("eventos_auditoria")
