"""perfil_campanas_invitaciones

Revision ID: 202611240001
Revises: 202611230003
Create Date: 2026-11-24 00:00:00

docs/004-Backend/03 (DEC-034):
1. Perfil del negocio en `organizaciones` (onboarding, moneda, margen).
2. `campanas`: historial de campañas, con RLS por organización.
3. `invitaciones`: alta de miembros del equipo por link (token hasheado).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202611240001"
down_revision: Union[str, None] = "202611230003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROL_APP = "merchly_app"
POLITICA = "organizacion_id = NULLIF(current_setting('app.organizacion_id', true), '')::uuid"
ROLES = "'admin_principal', 'responsable_tecnico', 'responsable_negocio', 'usuario_operativo'"


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    # 1. Perfil del negocio
    columnas = [
        sa.Column("pais", sa.String(2), nullable=False, server_default="BO"),
        sa.Column("rubro", sa.String(120), nullable=True),
        sa.Column("presupuesto_mensual", sa.Numeric(12, 2), nullable=True),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="BOB"),
        sa.Column("tipo_cambio", sa.Numeric(10, 4), nullable=True),
        sa.Column("costo_envio_unitario_usd", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("impuestos_importacion_pct", sa.Numeric(5, 2), nullable=False, server_default="0"),
        sa.Column("onboarding_completo", sa.Boolean(), nullable=False, server_default=sa.false()),
    ]
    for columna in columnas:
        op.add_column("organizaciones", columna)
    op.create_check_constraint("ck_organizaciones_moneda", "organizaciones", "moneda IN ('BOB', 'USD')")
    op.create_check_constraint("ck_organizaciones_tipo_cambio", "organizaciones", "tipo_cambio IS NULL OR tipo_cambio > 0")
    op.create_check_constraint(
        "ck_organizaciones_impuestos", "organizaciones", "impuestos_importacion_pct BETWEEN 0 AND 100"
    )
    op.create_check_constraint("ck_organizaciones_envio", "organizaciones", "costo_envio_unitario_usd >= 0")

    # 2. Campañas (datos de negocio: RLS)
    op.create_table(
        "campanas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacion_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizaciones.id"), nullable=False),
        sa.Column("creado_por", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("titulo", sa.String(150), nullable=False),
        sa.Column("productos_candidato_ids", postgresql.JSONB(), nullable=False),
        sa.Column("canales", postgresql.JSONB(), nullable=False),
        sa.Column("tono", sa.String(20), nullable=False),
        sa.Column("idioma", sa.String(2), nullable=False),
        sa.Column("modelo", sa.String(80), nullable=True),
        sa.Column("contenido", postgresql.JSONB(), nullable=False),
        sa.Column("editada", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_timestamps(),
    )
    op.create_index("ix_campanas_organizacion_id", "campanas", ["organizacion_id"])
    op.create_index("ix_campanas_creado_en", "campanas", ["creado_en"])
    op.execute("ALTER TABLE campanas ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE campanas FORCE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY aislamiento_organizacion ON campanas USING ({POLITICA}) WITH CHECK ({POLITICA})")
    op.execute(f"GRANT SELECT, INSERT, UPDATE ON campanas TO {ROL_APP}")

    # 3. Invitaciones (se buscan por token ANTES de saber la organización: sin RLS,
    #    la app filtra por organización en todas las consultas de administración).
    op.create_table(
        "invitaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organizacion_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizaciones.id"), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("rol", sa.String(30), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("aceptada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("creado_por", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=False),
        *_timestamps(),
        sa.CheckConstraint("email = lower(email)", name="ck_invitaciones_email_minusculas"),
        sa.CheckConstraint(f"rol IN ({ROLES})", name="ck_invitaciones_rol"),
    )
    op.create_index("ix_invitaciones_token_hash", "invitaciones", ["token_hash"], unique=True)
    op.create_index("ix_invitaciones_organizacion_id", "invitaciones", ["organizacion_id"])
    op.execute(f"GRANT SELECT, INSERT, UPDATE ON invitaciones TO {ROL_APP}")


def downgrade() -> None:
    op.drop_table("invitaciones")
    op.execute("DROP POLICY IF EXISTS aislamiento_organizacion ON campanas")
    op.drop_table("campanas")
    for nombre in ("ck_organizaciones_moneda", "ck_organizaciones_tipo_cambio", "ck_organizaciones_impuestos", "ck_organizaciones_envio"):
        op.drop_constraint(nombre, "organizaciones", type_="check")
    for columna in ("pais", "rubro", "presupuesto_mensual", "moneda", "tipo_cambio",
                    "costo_envio_unitario_usd", "impuestos_importacion_pct", "onboarding_completo"):
        op.drop_column("organizaciones", columna)
