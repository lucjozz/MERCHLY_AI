"""Schemas del inventario (docs/007-Agentes/08, sección 2).

``ItemCatalogoPublico`` es lo ÚNICO que ve la IA: nunca agregarle campos
privados (costo, gastos, proveedor, notas, stock real). Lo verifica un test.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.base import EntradaEstricta

Monto = Annotated[Decimal, Field(ge=0, le=Decimal("99999999.99"), max_digits=10, decimal_places=2)]
MAX_ESPECIFICACIONES = 20


def _validar_especificaciones(valor: dict[str, str] | None) -> dict[str, str] | None:
    if valor is None:
        return None
    if len(valor) > MAX_ESPECIFICACIONES:
        raise ValueError(f"Máximo {MAX_ESPECIFICACIONES} especificaciones.")
    limpio = {}
    for clave, texto in valor.items():
        clave, texto = str(clave).strip(), str(texto).strip()
        if not clave or len(clave) > 60 or len(texto) > 200:
            raise ValueError("Cada especificación: nombre de hasta 60 caracteres y valor de hasta 200.")
        limpio[clave] = texto
    return limpio


class ProductoInventarioEntrada(EntradaEstricta):
    nombre: str = Field(min_length=1, max_length=200)
    descripcion: str | None = Field(default=None, max_length=2000)
    especificaciones: dict[str, str] = Field(default_factory=dict)
    precio_venta: Monto | None = None
    publicado: bool = False
    sku: str | None = Field(default=None, max_length=60)
    costo_unitario: Monto | None = None
    gastos_unitarios: Monto | None = None
    proveedor: str | None = Field(default=None, max_length=200)
    notas_internas: str | None = Field(default=None, max_length=2000)
    stock: int = Field(default=0, ge=0, le=1_000_000)

    _especificaciones = field_validator("especificaciones")(_validar_especificaciones)


class ProductoInventarioEdicion(EntradaEstricta):
    """Edición parcial: solo se cambian los campos enviados."""

    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    descripcion: str | None = Field(default=None, max_length=2000)
    especificaciones: dict[str, str] | None = None
    precio_venta: Monto | None = None
    publicado: bool | None = None
    sku: str | None = Field(default=None, max_length=60)
    costo_unitario: Monto | None = None
    gastos_unitarios: Monto | None = None
    proveedor: str | None = Field(default=None, max_length=200)
    notas_internas: str | None = Field(default=None, max_length=2000)
    stock: int | None = Field(default=None, ge=0, le=1_000_000)

    _especificaciones = field_validator("especificaciones")(_validar_especificaciones)


class ProductoInventario(BaseModel):
    """Vista PRIVADA del dueño: todos los campos."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nombre: str
    descripcion: str | None
    especificaciones: dict[str, str]
    precio_venta: Decimal | None
    publicado: bool
    sku: str | None
    costo_unitario: Decimal | None
    gastos_unitarios: Decimal | None
    proveedor: str | None
    notas_internas: str | None
    stock: int
    stock_reservado: int
    disponibles: int
    margen_unitario: Decimal | None
    origen: str
    foto_ids: list[uuid.UUID]
    creado_en: datetime
    actualizado_en: datetime


class ResumenInventario(BaseModel):
    productos: int
    unidades: int
    sin_stock: int
    publicados: int
    valor_a_costo: Decimal


class InventarioListado(BaseModel):
    productos: list[ProductoInventario]
    total: int
    pagina: int
    tamano_pagina: int
    resumen: ResumenInventario


class ItemCatalogoPublico(BaseModel):
    """Vista PÚBLICA (la cara pública que usa la IA). Solo campos que puede decir a un comprador."""

    id: uuid.UUID
    nombre: str
    descripcion: str | None
    especificaciones: dict[str, str]
    precio_venta: Decimal | None
    disponibles: int
    foto_ids: list[uuid.UUID]


class FotoEntrada(EntradaEstricta):
    # ~1 MB de base64 (el tope global del body); el navegador achica la foto antes.
    imagen_base64: str = Field(min_length=100, max_length=1_000_000)


class FotoSalida(BaseModel):
    id: uuid.UUID
    tamano: int


class ImportarVistaPreviaEntrada(EntradaEstricta):
    nombre_archivo: str = Field(min_length=1, max_length=200)
    contenido_base64: str = Field(min_length=4, max_length=1_000_000)


class FilaImportada(BaseModel):
    fila: int
    nombre: str | None
    sku: str | None
    descripcion: str | None
    precio_venta: Decimal | None
    costo_unitario: Decimal | None
    stock: int | None
    problemas: list[str]


class ImportarVistaPrevia(BaseModel):
    formato: str
    columnas: dict[str, str | None]  # campo → columna del archivo que se usó
    filas: list[FilaImportada]
    descartadas: int


class ImportarConfirmacion(EntradaEstricta):
    productos: list[ProductoInventarioEntrada] = Field(min_length=1, max_length=500)


class ImportarResultado(BaseModel):
    creados: int
