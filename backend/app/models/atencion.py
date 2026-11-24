"""Models del Agente de Atención al Cliente (docs/007-Agentes/09). Todo con RLS por organización."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, LargeBinary, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo, DeOrganizacion

ESTADOS_PEDIDO = (
    "pedido_armado", "reservado", "pago_por_confirmar", "pagado", "entregado", "vencido", "rechazado", "cancelado",
)
ROLES_MENSAJE = ("comprador", "agente", "vendedor", "sistema")
CANALES = ("simulador", "whatsapp", "instagram", "facebook")


class AtencionConfig(DeOrganizacion, ConMarcaDeTiempo, Base):
    """Configuración del agente: una fila por organización (sección 2 del contrato)."""

    __tablename__ = "atencion_config"

    encendido: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    completar_ventas: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    presentacion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    info_negocio: Mapped[str | None] = mapped_column(Text, nullable=True)  # horarios, dirección, formas de pago...
    minutos_reserva: Mapped[int] = mapped_column(Integer, nullable=False, default=120, server_default="120")


class QrPago(DeOrganizacion, ConMarcaDeTiempo, Base):
    __tablename__ = "qr_pagos"

    etiqueta: Mapped[str] = mapped_column(String(80), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="image/png")
    tamano: Mapped[int] = mapped_column(Integer, nullable=False)
    contenido: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)


class ZonaEnvio(DeOrganizacion, ConMarcaDeTiempo, Base):
    __tablename__ = "zonas_envio"

    nombre: Mapped[str] = mapped_column(String(80), nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    notas: Mapped[str | None] = mapped_column(String(200), nullable=True)


class Conversacion(DeOrganizacion, ConMarcaDeTiempo, Base):
    __tablename__ = "conversaciones"

    canal: Mapped[str] = mapped_column(String(20), nullable=False)
    contacto: Mapped[str] = mapped_column(String(120), nullable=False)  # teléfono o usuario del canal
    nombre_contacto: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # "agente": responde la IA · "humano": la tomó una persona (el agente no responde)
    atendida_por: Mapped[str] = mapped_column(String(10), nullable=False, default="agente", server_default="agente")
    ultimo_mensaje_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Mensaje(DeOrganizacion, Base):
    """Append-only: el rol de la app no puede editarlos ni borrarlos."""

    __tablename__ = "mensajes"
    __mapper_args__ = {"eager_defaults": False}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversaciones.id"), nullable=False, index=True
    )
    rol: Mapped[str] = mapped_column(String(10), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    # [{"tipo": "qr", "qr_id": "..."}, {"tipo": "producto", "producto_id": "...", "foto_id": "..."}]
    adjuntos: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    simulado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Pedido(DeOrganizacion, ConMarcaDeTiempo, Base):
    __tablename__ = "pedidos"

    conversacion_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversaciones.id"), nullable=True, index=True
    )
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    # [{"producto_id", "nombre", "cantidad", "precio_unitario"}]: precios copiados del inventario al armar
    items: Mapped[list] = mapped_column(JSONB, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    zona_envio: Mapped[str | None] = mapped_column(String(80), nullable=True)
    costo_envio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    nombre_comprador: Mapped[str | None] = mapped_column(String(120), nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    qr_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("qr_pagos.id"), nullable=True)
    reservado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stock_reservado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    decidido_por: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    decidido_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    simulado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Notificacion(DeOrganizacion, ConMarcaDeTiempo, Base):
    __tablename__ = "notificaciones"

    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    cuerpo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pedido_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pedidos.id"), nullable=True)
    conversacion_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversaciones.id"), nullable=True
    )
    leida_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
