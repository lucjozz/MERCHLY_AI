"""dos_pasos

Revision ID: 202611270001
Revises: 202611260001
Create Date: 2026-11-24 00:00:00

docs/013-Seguridad/09: verificación en dos pasos (TOTP) en `usuarios`.
La clave se guarda cifrada (AES-GCM) y los códigos de respaldo como hash.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202611270001"
down_revision: Union[str, None] = "202611260001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("totp_secreto", sa.Text(), nullable=True))
    op.add_column("usuarios", sa.Column("totp_pendiente", sa.Text(), nullable=True))
    op.add_column("usuarios", sa.Column("totp_activado", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("usuarios", sa.Column("totp_ultimo_paso", sa.BigInteger(), nullable=True))
    op.add_column(
        "usuarios", sa.Column("codigos_respaldo", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb"))
    )
    op.create_check_constraint(
        "ck_usuarios_totp_activado", "usuarios", "NOT totp_activado OR totp_secreto IS NOT NULL"
    )


def downgrade() -> None:
    op.drop_constraint("ck_usuarios_totp_activado", "usuarios", type_="check")
    for columna in ("codigos_respaldo", "totp_ultimo_paso", "totp_activado", "totp_pendiente", "totp_secreto"):
        op.drop_column("usuarios", columna)
