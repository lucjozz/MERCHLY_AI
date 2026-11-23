"""restablecer_password

Revision ID: 202611240002
Revises: 202611240001
Create Date: 2026-11-24 01:00:00

Recuperación de contraseña por email (DEC-036): token de un solo uso, 1 hora,
guardado como SHA-256. Sin RLS (se busca por token antes de saber el usuario).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202611240002"
down_revision: Union[str, None] = "202611240001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "restablecimientos_password",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("usado_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_restablecimientos_token_hash", "restablecimientos_password", ["token_hash"], unique=True)
    op.create_index("ix_restablecimientos_usuario_id", "restablecimientos_password", ["usuario_id"])
    op.execute("GRANT SELECT, INSERT, UPDATE ON restablecimientos_password TO merchly_app")


def downgrade() -> None:
    op.drop_table("restablecimientos_password")
