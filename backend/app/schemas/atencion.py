"""Schemas del Agente de Atención al Cliente (docs/007-Agentes/09)."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import EntradaEstricta


class ConfigEntrada(EntradaEstricta):
    encendido: bool
    completar_ventas: bool
    presentacion: str | None = Field(default=None, max_length=300)
    info_negocio: str | None = Field(default=None, max_length=2000)
    minutos_reserva: int = Field(default=120, ge=15, le=2880)


class ConfigSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    encendido: bool
    completar_ventas: bool
    presentacion: str | None
    info_negocio: str | None
    minutos_reserva: int
    proveedor: str  # "openai" o "simulado"
    plan_incluye: bool


class QrEntrada(EntradaEstricta):
    etiqueta: str = Field(min_length=1, max_length=80)
    imagen_base64: str = Field(min_length=100, max_length=1_000_000)


class QrSalida(BaseModel):
    id: uuid.UUID
    etiqueta: str


class ZonaEntrada(EntradaEstricta):
    nombre: str = Field(min_length=1, max_length=80)
    precio: Decimal = Field(ge=0, le=Decimal("99999.99"), max_digits=7, decimal_places=2)
    notas: str | None = Field(default=None, max_length=200)


class ZonasEntrada(EntradaEstricta):
    zonas: list[ZonaEntrada] = Field(max_length=30)


class ZonaSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    precio: Decimal
    notas: str | None


class MensajeSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rol: str
    texto: str
    adjuntos: list[dict]
    simulado: bool
    creado_en: datetime


class ConversacionResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    canal: str
    contacto: str
    nombre_contacto: str | None
    atendida_por: str
    ultimo_mensaje_en: datetime | None
    creado_en: datetime


class ConversacionDetalle(ConversacionResumen):
    mensajes: list[MensajeSalida]


class ConversacionCambio(EntradaEstricta):
    atendida_por: str = Field(pattern="^(agente|humano)$")


class MensajeVendedorEntrada(EntradaEstricta):
    texto: str = Field(min_length=1, max_length=2000)


class SimuladorEntrada(EntradaEstricta):
    conversacion_id: uuid.UUID | None = None
    texto: str = Field(min_length=1, max_length=1000)
    nombre: str | None = Field(default=None, max_length=120)


class SimuladorSalida(BaseModel):
    conversacion_id: uuid.UUID
    atendida_por: str
    proveedor: str
    mensajes: list[MensajeSalida]


class PedidoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversacion_id: uuid.UUID | None
    estado: str
    items: list[dict]
    subtotal: Decimal
    zona_envio: str | None
    costo_envio: Decimal
    total: Decimal
    nombre_comprador: str | None
    direccion: str | None
    reservado_hasta: datetime | None
    simulado: bool
    decidido_en: datetime | None
    creado_en: datetime


class NotificacionSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tipo: str
    titulo: str
    cuerpo: str | None
    pedido_id: uuid.UUID | None
    conversacion_id: uuid.UUID | None
    leida_en: datetime | None
    creado_en: datetime


class NotificacionesListado(BaseModel):
    notificaciones: list[NotificacionSalida]
    sin_leer: int
