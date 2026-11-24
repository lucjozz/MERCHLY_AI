"""Inventario del negocio y catálogo público (docs/007-Agentes/08, sección 2). Sin FastAPI.

Todo filtrado por organización (además de RLS) y con borrado lógico.
La IA lee SOLO ``catalogo_publico``: nunca ``listar_inventario``.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventario import InventarioFoto, InventarioProducto
from app.schemas.inventario import (
    FotoSalida,
    ItemCatalogoPublico,
    ProductoInventario,
    ProductoInventarioEdicion,
    ProductoInventarioEntrada,
    ResumenInventario,
)

MAX_FOTOS_POR_PRODUCTO = 6


def _vigentes(organizacion_id: uuid.UUID):
    return (InventarioProducto.organizacion_id == organizacion_id, InventarioProducto.eliminado_en.is_(None))


def disponibles(p: InventarioProducto) -> int:
    return max(p.stock - p.stock_reservado, 0)


def margen_unitario(p: InventarioProducto) -> Decimal | None:
    if p.precio_venta is None or p.costo_unitario is None:
        return None
    return p.precio_venta - p.costo_unitario - (p.gastos_unitarios or Decimal("0"))


async def _fotos_por_producto(
    db_session: AsyncSession, organizacion_id: uuid.UUID, ids: list[uuid.UUID]
) -> dict[uuid.UUID, list[uuid.UUID]]:
    if not ids:
        return {}
    filas = await db_session.execute(
        select(InventarioFoto.producto_id, InventarioFoto.id)
        .where(InventarioFoto.organizacion_id == organizacion_id, InventarioFoto.producto_id.in_(ids))
        .order_by(InventarioFoto.orden, InventarioFoto.creado_en)
    )
    resultado: dict[uuid.UUID, list[uuid.UUID]] = {}
    for producto_id, foto_id in filas:
        resultado.setdefault(producto_id, []).append(foto_id)
    return resultado


def vista_privada(p: InventarioProducto, foto_ids: list[uuid.UUID]) -> ProductoInventario:
    return ProductoInventario(
        id=p.id, nombre=p.nombre, descripcion=p.descripcion, especificaciones=p.especificaciones or {},
        precio_venta=p.precio_venta, publicado=p.publicado, sku=p.sku, costo_unitario=p.costo_unitario,
        gastos_unitarios=p.gastos_unitarios, proveedor=p.proveedor, notas_internas=p.notas_internas,
        stock=p.stock, stock_reservado=p.stock_reservado, disponibles=disponibles(p),
        margen_unitario=margen_unitario(p), origen=p.origen, foto_ids=foto_ids,
        creado_en=p.creado_en, actualizado_en=p.actualizado_en,
    )


def vista_publica(p: InventarioProducto, foto_ids: list[uuid.UUID]) -> ItemCatalogoPublico:
    return ItemCatalogoPublico(
        id=p.id, nombre=p.nombre, descripcion=p.descripcion, especificaciones=p.especificaciones or {},
        precio_venta=p.precio_venta, disponibles=disponibles(p), foto_ids=foto_ids,
    )


def _filtro_busqueda(buscar: str | None):
    if not buscar:
        return ()
    patron = f"%{buscar.replace('%', '').replace('_', '')}%"
    return (or_(InventarioProducto.nombre.ilike(patron), InventarioProducto.sku.ilike(patron)),)


async def listar_inventario(
    db_session: AsyncSession, organizacion_id: uuid.UUID, pagina: int, tamano_pagina: int, buscar: str | None = None
) -> tuple[list[ProductoInventario], int, ResumenInventario]:
    filtros = (*_vigentes(organizacion_id), *_filtro_busqueda(buscar))
    total = await db_session.scalar(select(func.count()).select_from(InventarioProducto).where(*filtros)) or 0
    productos = list(
        (
            await db_session.execute(
                select(InventarioProducto)
                .where(*filtros)
                .order_by(InventarioProducto.nombre, InventarioProducto.id)
                .offset((pagina - 1) * tamano_pagina)
                .limit(tamano_pagina)
            )
        ).scalars()
    )
    fotos = await _fotos_por_producto(db_session, organizacion_id, [p.id for p in productos])
    return [vista_privada(p, fotos.get(p.id, [])) for p in productos], total, await resumen(db_session, organizacion_id)


async def resumen(db_session: AsyncSession, organizacion_id: uuid.UUID) -> ResumenInventario:
    p = InventarioProducto
    fila = (
        await db_session.execute(
            select(
                func.count(),
                func.coalesce(func.sum(p.stock), 0),
                func.count().filter(p.stock - p.stock_reservado <= 0),
                func.count().filter(p.publicado.is_(True)),
                func.coalesce(func.sum(p.stock * (func.coalesce(p.costo_unitario, 0) + func.coalesce(p.gastos_unitarios, 0))), 0),
            ).where(*_vigentes(organizacion_id))
        )
    ).one()
    return ResumenInventario(
        productos=fila[0], unidades=int(fila[1]), sin_stock=fila[2], publicados=fila[3], valor_a_costo=Decimal(fila[4])
    )


async def catalogo_publico(
    db_session: AsyncSession, organizacion_id: uuid.UUID, buscar: str | None = None, limite: int = 200
) -> list[ItemCatalogoPublico]:
    """Lo único que ve la IA: productos publicados, sin datos privados."""
    productos = list(
        (
            await db_session.execute(
                select(InventarioProducto)
                .where(*_vigentes(organizacion_id), InventarioProducto.publicado.is_(True), *_filtro_busqueda(buscar))
                .order_by(InventarioProducto.nombre, InventarioProducto.id)
                .limit(limite)
            )
        ).scalars()
    )
    fotos = await _fotos_por_producto(db_session, organizacion_id, [p.id for p in productos])
    return [vista_publica(p, fotos.get(p.id, [])) for p in productos]


async def obtener(
    db_session: AsyncSession, organizacion_id: uuid.UUID, producto_id: uuid.UUID, para_actualizar: bool = False
) -> InventarioProducto | None:
    consulta = select(InventarioProducto).where(InventarioProducto.id == producto_id, *_vigentes(organizacion_id))
    if para_actualizar:
        consulta = consulta.with_for_update()
    return (await db_session.execute(consulta)).scalar_one_or_none()


async def obtener_vista(db_session: AsyncSession, organizacion_id: uuid.UUID, p: InventarioProducto) -> ProductoInventario:
    fotos = await _fotos_por_producto(db_session, organizacion_id, [p.id])
    return vista_privada(p, fotos.get(p.id, []))


def _nuevo(organizacion_id: uuid.UUID, entrada: ProductoInventarioEntrada, origen: str) -> InventarioProducto:
    return InventarioProducto(id=uuid.uuid4(), organizacion_id=organizacion_id, origen=origen, **entrada.model_dump())


async def crear(
    db_session: AsyncSession, organizacion_id: uuid.UUID, entrada: ProductoInventarioEntrada, origen: str = "manual"
) -> ProductoInventario:
    producto = _nuevo(organizacion_id, entrada, origen)
    db_session.add(producto)
    await db_session.commit()
    await db_session.refresh(producto)
    return vista_privada(producto, [])


async def crear_varios(
    db_session: AsyncSession, organizacion_id: uuid.UUID, entradas: list[ProductoInventarioEntrada]
) -> int:
    db_session.add_all([_nuevo(organizacion_id, e, "importado") for e in entradas])
    await db_session.commit()
    return len(entradas)


class StockMenorQueReservadoError(Exception):
    pass


async def editar(
    db_session: AsyncSession, organizacion_id: uuid.UUID, producto_id: uuid.UUID, cambios: ProductoInventarioEdicion
) -> tuple[ProductoInventario, dict] | None:
    """Devuelve la vista actualizada y un resumen de cambios para la bitácora (sin textos largos)."""
    producto = await obtener(db_session, organizacion_id, producto_id, para_actualizar=True)
    if producto is None:
        return None
    enviados = cambios.model_dump(exclude_unset=True)
    if "stock" in enviados and enviados["stock"] is not None and enviados["stock"] < producto.stock_reservado:
        await db_session.rollback()
        raise StockMenorQueReservadoError()
    detalle: dict = {}
    for campo, valor in enviados.items():
        if campo in ("nombre", "stock", "publicado") and valor is None:
            continue  # campos obligatorios: None no los borra
        anterior = getattr(producto, campo)
        if anterior != valor:
            if campo in ("precio_venta", "costo_unitario", "gastos_unitarios", "stock", "publicado"):
                detalle[f"{campo}_antes"] = None if anterior is None else str(anterior)
                detalle[f"{campo}_ahora"] = None if valor is None else str(valor)
            else:
                detalle.setdefault("otros_campos", "")
                detalle["otros_campos"] = (detalle["otros_campos"] + f" {campo}").strip()
            setattr(producto, campo, valor)
    await db_session.commit()
    await db_session.refresh(producto)
    return await obtener_vista(db_session, organizacion_id, producto), detalle


async def eliminar(db_session: AsyncSession, organizacion_id: uuid.UUID, producto_id: uuid.UUID) -> bool:
    producto = await obtener(db_session, organizacion_id, producto_id, para_actualizar=True)
    if producto is None:
        return False
    producto.eliminado_en = datetime.now(timezone.utc)
    producto.publicado = False
    await db_session.commit()
    return True


# ------------------------------------------------------------------ fotos


class DemasiadasFotosError(Exception):
    pass


async def agregar_foto(
    db_session: AsyncSession, organizacion_id: uuid.UUID, producto_id: uuid.UUID, contenido: bytes
) -> FotoSalida | None:
    producto = await obtener(db_session, organizacion_id, producto_id, para_actualizar=True)
    if producto is None:
        return None
    cantidad = await db_session.scalar(
        select(func.count()).select_from(InventarioFoto).where(
            InventarioFoto.organizacion_id == organizacion_id, InventarioFoto.producto_id == producto_id
        )
    ) or 0
    if cantidad >= MAX_FOTOS_POR_PRODUCTO:
        await db_session.rollback()
        raise DemasiadasFotosError()
    foto = InventarioFoto(
        id=uuid.uuid4(), organizacion_id=organizacion_id, producto_id=producto_id,
        orden=cantidad, tipo="image/webp", tamano=len(contenido), contenido=contenido,
    )
    salida = FotoSalida(id=foto.id, tamano=foto.tamano)  # antes del commit: después la fila queda vencida
    db_session.add(foto)
    await db_session.commit()
    return salida


async def obtener_foto(db_session: AsyncSession, organizacion_id: uuid.UUID, foto_id: uuid.UUID) -> InventarioFoto | None:
    return (
        await db_session.execute(
            select(InventarioFoto)
            .join(InventarioProducto, InventarioProducto.id == InventarioFoto.producto_id)
            .where(InventarioFoto.id == foto_id, InventarioFoto.organizacion_id == organizacion_id, *_vigentes(organizacion_id))
        )
    ).scalar_one_or_none()


async def borrar_foto(
    db_session: AsyncSession, organizacion_id: uuid.UUID, producto_id: uuid.UUID, foto_id: uuid.UUID
) -> bool:
    foto = (
        await db_session.execute(
            select(InventarioFoto).where(
                InventarioFoto.id == foto_id,
                InventarioFoto.producto_id == producto_id,
                InventarioFoto.organizacion_id == organizacion_id,
            )
        )
    ).scalar_one_or_none()
    if foto is None:
        return False
    await db_session.delete(foto)  # borrado real: el dueño la sacó, no se guarda
    await db_session.commit()
    return True
