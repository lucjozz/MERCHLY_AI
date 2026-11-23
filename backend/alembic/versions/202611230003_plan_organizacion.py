"""plan_organizacion

Revision ID: 202611230003
Revises: 202611230002
Create Date: 2026-11-23 02:00:00

Plan de cada organización (docs/007-Agentes/07, DEC-033): define qué
modelos de IA usan sus agentes. Lo cambia solo el sistema.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202611230003"
down_revision: Union[str, None] = "202611230002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "organizaciones",
        sa.Column("plan", sa.String(length=20), nullable=False, server_default="beta"),
    )
    op.create_check_constraint(
        "ck_organizaciones_plan", "organizaciones", "plan IN ('beta', 'emprendedor', 'negocio')"
    )


def downgrade() -> None:
    op.drop_constraint("ck_organizaciones_plan", "organizaciones", type_="check")
    op.drop_column("organizaciones", "plan")
