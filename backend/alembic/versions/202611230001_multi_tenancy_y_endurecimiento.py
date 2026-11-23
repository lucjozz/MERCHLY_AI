"""multi_tenancy_y_endurecimiento

Revision ID: 202611230001
Revises: 202609150001
Create Date: 2026-11-23 00:00:00

Implementa docs/013-Seguridad/04-Endurecimiento-para-Lanzamiento.md:

1. Tabla ``organizaciones`` + organización inicial con todos los datos
   existentes (backfill).
2. ``organizacion_id`` NOT NULL en usuarios, productos_candidatos y las 4
   tablas decision_*.
3. ``usuarios``: email en minúsculas (CHECK), password_hash opcional,
   google_sub, token_version.
4. Estado ``en_revision`` en productos_candidatos.
5. Tabla ``refresh_tokens``.
6. Rol de base de datos ``merchly_app`` (sin superusuario, sin BYPASSRLS,
   no dueño) con privilegios mínimos: decisiones append-only y sin DELETE.
7. Row-Level Security con FORCE en las 5 tablas de negocio.

La contraseña de ``merchly_app`` se toma de la variable de entorno
``DB_APP_PASSWORD`` (si no está, el rol se crea sin login, útil en CI).
"""

import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202611230001"
down_revision: Union[str, None] = "202609150001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROL_APP = "merchly_app"
TABLAS_CON_RLS = (
    "productos_candidatos",
    "decision_records",
    "decision_context",
    "decision_evidence",
    "decision_outcomes",
)
TABLAS_DECISIONES = TABLAS_CON_RLS[1:]
ORG_INICIAL_NOMBRE = "MERCHLY (organización inicial)"

POLITICA = (
    "organizacion_id = NULLIF(current_setting('app.organizacion_id', true), '')::uuid"
)


def _literal(valor: str) -> str:
    """Escapa un literal de texto SQL (para DDL, que no acepta parámetros)."""
    return "'" + valor.replace("'", "''") + "'"


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    # 1. organizaciones + organización inicial
    op.create_table(
        "organizaciones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
    )
    op.execute(
        "INSERT INTO organizaciones (id, nombre) "
        f"VALUES (gen_random_uuid(), {_literal(ORG_INICIAL_NOMBRE)})"
    )
    org_inicial = f"(SELECT id FROM organizaciones WHERE nombre = {_literal(ORG_INICIAL_NOMBRE)})"

    # 2. organizacion_id en todas las tablas con dueño
    for tabla in ("usuarios", *TABLAS_CON_RLS):
        op.add_column(tabla, sa.Column("organizacion_id", postgresql.UUID(as_uuid=True), nullable=True))
        op.execute(f"UPDATE {tabla} SET organizacion_id = {org_inicial}")
        op.alter_column(tabla, "organizacion_id", nullable=False)
        op.create_foreign_key(
            f"fk_{tabla}_organizacion", tabla, "organizaciones", ["organizacion_id"], ["id"]
        )
        op.create_index(f"ix_{tabla}_organizacion_id", tabla, ["organizacion_id"])

    # 3. usuarios
    op.execute("UPDATE usuarios SET email = lower(trim(email))")
    op.create_check_constraint("ck_usuarios_email_minusculas", "usuarios", "email = lower(email)")
    op.alter_column("usuarios", "password_hash", nullable=True)
    op.add_column("usuarios", sa.Column("google_sub", sa.String(length=255), nullable=True))
    op.create_index("ix_usuarios_google_sub", "usuarios", ["google_sub"], unique=True)
    op.add_column(
        "usuarios", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0")
    )
    op.create_check_constraint(
        "ck_usuarios_tiene_credencial",
        "usuarios",
        "password_hash IS NOT NULL OR google_sub IS NOT NULL",
    )

    # 4. estado en_revision
    op.drop_constraint("ck_productos_candidatos_estado", "productos_candidatos", type_="check")
    op.create_check_constraint(
        "ck_productos_candidatos_estado",
        "productos_candidatos",
        "estado IN ('candidato', 'en_revision', 'en_catalogo', 'descartado')",
    )

    # 5. refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("familia", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revocado_en", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_refresh_tokens_usuario_id", "refresh_tokens", ["usuario_id"])
    op.create_index("ix_refresh_tokens_familia", "refresh_tokens", ["familia"])

    # 6. rol de la aplicación con privilegios mínimos
    password = os.environ.get("DB_APP_PASSWORD", "")
    login = f"LOGIN PASSWORD {_literal(password)}" if password else "NOLOGIN"
    op.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{ROL_APP}') THEN
                CREATE ROLE {ROL_APP} NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS NOINHERIT;
            END IF;
        END $$;
        """
    )
    op.execute(f"ALTER ROLE {ROL_APP} {login} NOSUPERUSER NOBYPASSRLS")
    op.execute(f"ALTER ROLE {ROL_APP} SET statement_timeout = '15s'")
    op.execute(f"ALTER ROLE {ROL_APP} SET idle_in_transaction_session_timeout = '30s'")
    op.execute(
        f"DO $$ BEGIN EXECUTE format('GRANT CONNECT ON DATABASE %I TO {ROL_APP}', current_database()); END $$;"
    )
    op.execute(f"GRANT USAGE ON SCHEMA public TO {ROL_APP}")
    op.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
    for tabla in ("productos_candidatos", "usuarios", "organizaciones", "refresh_tokens"):
        op.execute(f"GRANT SELECT, INSERT, UPDATE ON {tabla} TO {ROL_APP}")
    for tabla in TABLAS_DECISIONES:
        # Append-only: la app no puede editar ni borrar decisiones.
        op.execute(f"GRANT SELECT, INSERT ON {tabla} TO {ROL_APP}")

    # 7. Row-Level Security
    for tabla in TABLAS_CON_RLS:
        op.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {tabla} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY aislamiento_organizacion ON {tabla} "
            f"USING ({POLITICA}) WITH CHECK ({POLITICA})"
        )


def downgrade() -> None:
    for tabla in TABLAS_CON_RLS:
        op.execute(f"DROP POLICY IF EXISTS aislamiento_organizacion ON {tabla}")
        op.execute(f"ALTER TABLE {tabla} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {tabla} DISABLE ROW LEVEL SECURITY")
    for tabla in ("productos_candidatos", "usuarios", "organizaciones", "refresh_tokens", *TABLAS_DECISIONES):
        op.execute(f"REVOKE ALL ON {tabla} FROM {ROL_APP}")

    op.drop_table("refresh_tokens")
    op.execute("UPDATE productos_candidatos SET estado = 'candidato' WHERE estado = 'en_revision'")
    op.drop_constraint("ck_productos_candidatos_estado", "productos_candidatos", type_="check")
    op.create_check_constraint(
        "ck_productos_candidatos_estado",
        "productos_candidatos",
        "estado IN ('candidato', 'en_catalogo', 'descartado')",
    )
    op.drop_constraint("ck_usuarios_tiene_credencial", "usuarios", type_="check")
    op.drop_column("usuarios", "token_version")
    op.drop_index("ix_usuarios_google_sub", table_name="usuarios")
    op.drop_column("usuarios", "google_sub")
    op.alter_column("usuarios", "password_hash", nullable=False)
    op.drop_constraint("ck_usuarios_email_minusculas", "usuarios", type_="check")
    for tabla in ("usuarios", *TABLAS_CON_RLS):
        op.drop_index(f"ix_{tabla}_organizacion_id", table_name=tabla)
        op.drop_constraint(f"fk_{tabla}_organizacion", tabla, type_="foreignkey")
        op.drop_column(tabla, "organizacion_id")
    op.drop_table("organizaciones")
