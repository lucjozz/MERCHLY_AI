"""refresh_rotado_en

Revision ID: 202611230002
Revises: 202611230001
Create Date: 2026-11-23 01:00:00

Distingue un refresh token ROTADO (canjeado por uno nuevo) de uno REVOCADO
(logout, robo detectado). Un token rotado hace menos de unos segundos se
tolera (requests paralelos del navegador que refrescan a la vez); pasada
esa ventana, reusarlo se trata como robo (docs/013-Seguridad/04, sección 3).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202611230002"
down_revision: Union[str, None] = "202611230001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("refresh_tokens", sa.Column("rotado_en", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("refresh_tokens", "rotado_en")
