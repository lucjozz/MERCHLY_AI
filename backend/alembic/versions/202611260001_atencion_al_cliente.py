"""atencion_al_cliente

Revision ID: 202611260001
Revises: 202611250001
Create Date: 2026-11-23 00:00:00

docs/007-Agentes/09 (DEC-039): configuración del agente, QR de pago, zonas de
envío, conversaciones, mensajes (append-only), pedidos y notificaciones.
Todas con RLS forzado por organización.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202611260001"
down_revision: Union[str, None] = "202611250001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROL_APP = "merchly_app"
POLITICA = "organizacion_id = NULLIF(current_setting('app.organizacion_id', true), '')::uuid"
UUID = postgresql.UUID(as_uuid=True)


def _ts() -> list[sa.Column]:
    return [
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("eliminado_en", sa.DateTime(timezone=True), nullable=True),
    ]


def _base() -> list[sa.Column]:
    return [
        sa.Column("id", UUID, primary_key=True),
        sa.Column("organizacion_id", UUID, sa.ForeignKey("organizaciones.id"), nullable=False, index=True),
    ]


def _rls(tabla: str, permisos: str) -> None:
    op.execute(f"ALTER TABLE {tabla} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {tabla} FORCE ROW LEVEL SECURITY")
    op.execute(f"CREATE POLICY aislamiento_organizacion ON {tabla} USING ({POLITICA}) WITH CHECK ({POLITICA})")
    op.execute(f"GRANT {permisos} ON {tabla} TO {ROL_APP}")


TABLAS = ("notificaciones", "pedidos", "mensajes", "conversaciones", "zonas_envio", "qr_pagos", "atencion_config")


def upgrade() -> None:
    op.create_table(
        "atencion_config", *_base(),
        sa.Column("encendido", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("completar_ventas", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("presentacion", sa.String(300), nullable=True),
        sa.Column("info_negocio", sa.Text(), nullable=True),
        sa.Column("minutos_reserva", sa.Integer(), nullable=False, server_default="120"),
        *_ts(),
        sa.UniqueConstraint("organizacion_id", name="uq_atencion_config_organizacion"),
        sa.CheckConstraint("minutos_reserva BETWEEN 15 AND 2880", name="ck_atencion_config_reserva"),
    )
    _rls("atencion_config", "SELECT, INSERT, UPDATE")

    op.create_table(
        "qr_pagos", *_base(),
        sa.Column("etiqueta", sa.String(80), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False, server_default="image/png"),
        sa.Column("tamano", sa.Integer(), nullable=False),
        sa.Column("contenido", sa.LargeBinary(), nullable=False),
        *_ts(),
        sa.CheckConstraint("tamano > 0 AND tamano <= 2097152", name="ck_qr_pagos_tamano"),
    )
    _rls("qr_pagos", "SELECT, INSERT, UPDATE")

    op.create_table(
        "zonas_envio", *_base(),
        sa.Column("nombre", sa.String(80), nullable=False),
        sa.Column("precio", sa.Numeric(10, 2), nullable=False),
        sa.Column("notas", sa.String(200), nullable=True),
        *_ts(),
        sa.CheckConstraint("precio >= 0", name="ck_zonas_envio_precio"),
    )
    _rls("zonas_envio", "SELECT, INSERT, UPDATE")

    op.create_table(
        "conversaciones", *_base(),
        sa.Column("canal", sa.String(20), nullable=False),
        sa.Column("contacto", sa.String(120), nullable=False),
        sa.Column("nombre_contacto", sa.String(120), nullable=True),
        sa.Column("atendida_por", sa.String(10), nullable=False, server_default="agente"),
        sa.Column("ultimo_mensaje_en", sa.DateTime(timezone=True), nullable=True),
        *_ts(),
        sa.CheckConstraint("canal IN ('simulador', 'whatsapp', 'instagram', 'facebook')", name="ck_conversaciones_canal"),
        sa.CheckConstraint("atendida_por IN ('agente', 'humano')", name="ck_conversaciones_atendida_por"),
    )
    _rls("conversaciones", "SELECT, INSERT, UPDATE")

    op.create_table(
        "mensajes", *_base(),
        sa.Column("conversacion_id", UUID, sa.ForeignKey("conversaciones.id"), nullable=False, index=True),
        sa.Column("rol", sa.String(10), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("adjuntos", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("simulado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rol IN ('comprador', 'agente', 'vendedor', 'sistema')", name="ck_mensajes_rol"),
    )
    _rls("mensajes", "SELECT, INSERT")  # append-only

    op.create_table(
        "pedidos", *_base(),
        sa.Column("conversacion_id", UUID, sa.ForeignKey("conversaciones.id"), nullable=True, index=True),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("items", postgresql.JSONB(), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("zona_envio", sa.String(80), nullable=True),
        sa.Column("costo_envio", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("nombre_comprador", sa.String(120), nullable=True),
        sa.Column("direccion", sa.String(300), nullable=True),
        sa.Column("qr_id", UUID, sa.ForeignKey("qr_pagos.id"), nullable=True),
        sa.Column("reservado_hasta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stock_reservado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("decidido_por", UUID, sa.ForeignKey("usuarios.id"), nullable=True),
        sa.Column("decidido_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("simulado", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_ts(),
        sa.CheckConstraint(
            "estado IN ('pedido_armado', 'reservado', 'pago_por_confirmar', 'pagado', 'entregado', 'vencido', 'rechazado', 'cancelado')",
            name="ck_pedidos_estado",
        ),
        sa.CheckConstraint("subtotal >= 0 AND costo_envio >= 0 AND total >= 0", name="ck_pedidos_montos"),
    )
    op.create_index("ix_pedidos_estado", "pedidos", ["estado"])
    _rls("pedidos", "SELECT, INSERT, UPDATE")

    op.create_table(
        "notificaciones", *_base(),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("titulo", sa.String(150), nullable=False),
        sa.Column("cuerpo", sa.String(500), nullable=True),
        sa.Column("pedido_id", UUID, sa.ForeignKey("pedidos.id"), nullable=True),
        sa.Column("conversacion_id", UUID, sa.ForeignKey("conversaciones.id"), nullable=True),
        sa.Column("leida_en", sa.DateTime(timezone=True), nullable=True),
        *_ts(),
    )
    _rls("notificaciones", "SELECT, INSERT, UPDATE")


def downgrade() -> None:
    for tabla in TABLAS:
        op.execute(f"DROP POLICY IF EXISTS aislamiento_organizacion ON {tabla}")
        op.drop_table(tabla)
