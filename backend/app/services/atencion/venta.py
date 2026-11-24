"""Sub-agente Venta (docs/007-Agentes/09, sección 3.5). Sin FastAPI.

pedido_armado ─► reservado ─► pago_por_confirmar ─► pagado ─► entregado
                    │                │
                    └─► vencido      └─► rechazado        (y cancelado)

Reglas que nunca se rompen:
* Precios y totales los calcula este módulo con el precio del inventario, no la IA.
* El agente puede reservar (si el dueño activó "Completar ventas") e informar
  que el comprador dice haber pagado. **Solo una persona marca un pedido como pagado.**
* El stock se descuenta recién al confirmar el pago; las reservas vencen solas.
"""

import uuid
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.atencion import Conversacion, Pedido, ZonaEnvio
from app.models.inventario import InventarioProducto
from app.models.organizacion import Organizacion
from app.services.atencion.configuracion import obtener_config, qr_principal
from app.services.atencion.conversaciones import agregar_mensaje, ahora, notificar
from app.services.atencion.dinero import formatear

MAX_ITEMS = 10
MAX_CANTIDAD = 100
ABIERTOS = ("pedido_armado", "reservado", "pago_por_confirmar")

# Transiciones que puede hacer una PERSONA desde la pantalla de pedidos.
TRANSICIONES_VENDEDOR = {
    "confirmar_pago": ("pedido_armado", "reservado", "pago_por_confirmar"),
    "rechazar_pago": ("reservado", "pago_por_confirmar"),
    "entregado": ("pagado",),
    "cancelar": ABIERTOS,
}


class VentaError(Exception):
    """Mensaje apto para el comprador o el vendedor."""


class TransicionInvalidaError(Exception):
    def __init__(self, estado: str) -> None:
        super().__init__(estado)
        self.estado = estado


@dataclass
class ResultadoPedido:
    pedido: Pedido
    qr_id: uuid.UUID | None


async def _productos_bloqueados(
    db_session: AsyncSession, organizacion_id: uuid.UUID, ids: list[uuid.UUID]
) -> dict[uuid.UUID, InventarioProducto]:
    filas = (
        await db_session.execute(
            select(InventarioProducto)
            .where(
                InventarioProducto.organizacion_id == organizacion_id,
                InventarioProducto.id.in_(ids),
                InventarioProducto.eliminado_en.is_(None),
            )
            .order_by(InventarioProducto.id)  # orden fijo: evita deadlocks entre pedidos simultáneos
            .with_for_update()
        )
    ).scalars()
    return {p.id: p for p in filas}


async def _liberar(db_session: AsyncSession, pedido: Pedido) -> None:
    if not pedido.stock_reservado:
        return
    productos = await _productos_bloqueados(
        db_session, pedido.organizacion_id, [uuid.UUID(i["producto_id"]) for i in pedido.items]
    )
    for item in pedido.items:
        p = productos.get(uuid.UUID(item["producto_id"]))
        if p is not None:
            p.stock_reservado = max(p.stock_reservado - int(item["cantidad"]), 0)
    pedido.stock_reservado = False


async def vencer_reservas(db_session: AsyncSession, organizacion_id: uuid.UUID) -> int:
    """Libera las reservas vencidas. Se llama al usar el agente o la pantalla (sin procesos de fondo)."""
    vencidos = list(
        (
            await db_session.execute(
                select(Pedido)
                .where(
                    Pedido.organizacion_id == organizacion_id,
                    Pedido.estado == "reservado",
                    Pedido.reservado_hasta < ahora(),
                )
                .with_for_update(skip_locked=True)
            )
        ).scalars()
    )
    for pedido in vencidos:
        await _liberar(db_session, pedido)
        pedido.estado = "vencido"
    if vencidos:
        await db_session.flush()
    return len(vencidos)


async def armar_pedido(
    db_session: AsyncSession,
    conversacion: Conversacion,
    items: list[tuple[uuid.UUID, int]],
    zona: ZonaEnvio | None,
    nombre_comprador: str | None,
    direccion: str | None,
    simulado: bool,
) -> ResultadoPedido:
    """Arma el pedido con los precios del inventario. Reserva y adjunta el QR solo si el dueño lo permitió."""
    org = conversacion.organizacion_id
    if not items or len(items) > MAX_ITEMS:
        raise VentaError("No entendí qué productos querés.")
    cantidades: dict[uuid.UUID, int] = {}
    for producto_id, cantidad in items:
        if not 1 <= cantidad <= MAX_CANTIDAD:
            raise VentaError("La cantidad no es válida.")
        cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

    await vencer_reservas(db_session, org)
    abierto = (
        await db_session.execute(
            select(Pedido).where(
                Pedido.organizacion_id == org, Pedido.conversacion_id == conversacion.id, Pedido.estado.in_(ABIERTOS)
            )
        )
    ).scalars().first()
    if abierto is not None:
        raise VentaError("Ya tenés un pedido abierto: primero terminemos ese o pedile al vendedor que lo cancele.")

    config = await obtener_config(db_session, org)
    qr = await qr_principal(db_session, org) if config.completar_ventas else None
    reservar = config.completar_ventas and qr is not None

    productos = await _productos_bloqueados(db_session, org, list(cantidades))
    lineas = []
    subtotal = Decimal("0")
    for producto_id, cantidad in cantidades.items():
        p = productos.get(producto_id)
        if p is None or not p.publicado:
            raise VentaError("Ese producto ya no está en el catálogo.")
        if p.precio_venta is None:
            raise VentaError(f"«{p.nombre}» todavía no tiene precio: te lo confirma el vendedor.")
        disponibles = p.stock - p.stock_reservado
        if disponibles < cantidad:
            raise VentaError(
                f"De «{p.nombre}» quedan {max(disponibles, 0)} disponibles." if disponibles > 0 else f"«{p.nombre}» está agotado."
            )
        lineas.append({"producto_id": str(p.id), "nombre": p.nombre, "cantidad": cantidad, "precio_unitario": str(p.precio_venta)})
        subtotal += p.precio_venta * cantidad
    if reservar:  # recién después de validar TODO: nunca una reserva a medias
        for producto_id, cantidad in cantidades.items():
            productos[producto_id].stock_reservado += cantidad

    costo_envio = zona.precio if zona is not None else Decimal("0")
    pedido = Pedido(
        id=uuid.uuid4(), organizacion_id=org, conversacion_id=conversacion.id,
        estado="reservado" if reservar else "pedido_armado", items=lineas, subtotal=subtotal,
        zona_envio=zona.nombre if zona else None, costo_envio=costo_envio, total=subtotal + costo_envio,
        nombre_comprador=(nombre_comprador or conversacion.nombre_contacto or None),
        direccion=(direccion or None) and direccion[:300], qr_id=qr.id if reservar else None,
        reservado_hasta=ahora() + timedelta(minutes=config.minutos_reserva) if reservar else None,
        stock_reservado=reservar, simulado=simulado,
    )
    db_session.add(pedido)
    await db_session.flush()
    moneda = await _moneda(db_session, org)
    if reservar:
        titulo = f"Pedido reservado: {formatear(pedido.total, moneda)}"
        cuerpo = "El agente mandó el QR. Cuando el comprador avise que pagó, revisá tu cuenta y confirmá el pago."
    else:
        titulo = f"Nuevo pedido para cerrar: {formatear(pedido.total, moneda)}"
        cuerpo = (
            "«Completar ventas» está activado pero no hay un QR cargado: cargá uno en Configuración."
            if config.completar_ventas else "El agente armó el pedido; vos cerrás la venta con el comprador."
        )
    await notificar(db_session, org, "pedido", titulo, cuerpo, pedido_id=pedido.id, conversacion_id=conversacion.id)
    return ResultadoPedido(pedido=pedido, qr_id=pedido.qr_id)


async def informar_pago(db_session: AsyncSession, conversacion: Conversacion) -> Pedido | None:
    """El comprador dice que pagó: el pedido queda POR CONFIRMAR y se avisa al vendedor. Nunca lo marca pagado."""
    await vencer_reservas(db_session, conversacion.organizacion_id)
    pedido = (
        await db_session.execute(
            select(Pedido).where(
                Pedido.organizacion_id == conversacion.organizacion_id,
                Pedido.conversacion_id == conversacion.id,
                Pedido.estado.in_(("reservado", "pedido_armado")),
            ).order_by(Pedido.creado_en.desc()).with_for_update()
        )
    ).scalars().first()
    if pedido is None:
        return None
    pedido.estado = "pago_por_confirmar"
    moneda = await _moneda(db_session, conversacion.organizacion_id)
    await notificar(
        db_session, conversacion.organizacion_id, "pago_informado",
        f"Revisá tu cuenta: {pedido.nombre_comprador or 'un comprador'} dice que pagó {formatear(pedido.total, moneda)}",
        "Confirmá el pago solo cuando veas la plata en tu cuenta.", pedido_id=pedido.id, conversacion_id=conversacion.id,
    )
    return pedido


async def obtener_pedido(
    db_session: AsyncSession, organizacion_id: uuid.UUID, pedido_id: uuid.UUID, para_actualizar: bool = False
) -> Pedido | None:
    consulta = select(Pedido).where(Pedido.id == pedido_id, Pedido.organizacion_id == organizacion_id)
    if para_actualizar:
        consulta = consulta.with_for_update()
    return (await db_session.execute(consulta)).scalar_one_or_none()


async def listar_pedidos(
    db_session: AsyncSession, organizacion_id: uuid.UUID, estados: tuple[str, ...] | None = None, limite: int = 100
) -> list[Pedido]:
    await vencer_reservas(db_session, organizacion_id)
    await db_session.commit()
    consulta = select(Pedido).where(Pedido.organizacion_id == organizacion_id)
    if estados:
        consulta = consulta.where(Pedido.estado.in_(estados))
    return list((await db_session.execute(consulta.order_by(Pedido.creado_en.desc()).limit(limite))).scalars())


MENSAJES_AL_COMPRADOR = {
    "confirmar_pago": "¡Listo! El vendedor confirmó tu pago de {total}. Gracias por tu compra, te avisamos para la entrega.",
    "rechazar_pago": "No pudimos ver tu pago todavía. Escribinos y lo revisamos con vos.",
    "entregado": "Tu pedido figura como entregado. ¡Gracias por comprar!",
    "cancelar": "Tu pedido fue cancelado. Si querés, armamos uno nuevo.",
}
ESTADO_FINAL = {"confirmar_pago": "pagado", "rechazar_pago": "rechazado", "entregado": "entregado", "cancelar": "cancelado"}


async def decidir(
    db_session: AsyncSession, organizacion_id: uuid.UUID, pedido_id: uuid.UUID, accion: str, usuario_id: uuid.UUID
) -> Pedido | None:
    """Acción de una PERSONA sobre un pedido. 409 si el estado no lo permite."""
    pedido = await obtener_pedido(db_session, organizacion_id, pedido_id, para_actualizar=True)
    if pedido is None:
        return None
    estado_actual = pedido.estado  # leer ANTES del rollback (después la fila queda vencida)
    if estado_actual not in TRANSICIONES_VENDEDOR[accion]:
        await db_session.rollback()
        raise TransicionInvalidaError(estado_actual)

    if accion == "confirmar_pago":
        productos = await _productos_bloqueados(db_session, organizacion_id, [uuid.UUID(i["producto_id"]) for i in pedido.items])
        for item in pedido.items:
            p = productos.get(uuid.UUID(item["producto_id"]))
            cantidad = int(item["cantidad"])
            reservado = cantidad if pedido.stock_reservado else 0
            if p is None or p.stock < cantidad or (not pedido.stock_reservado and p.stock - p.stock_reservado < cantidad):
                nombre = item["nombre"]
                await db_session.rollback()
                raise VentaError(f"No alcanza el stock de «{nombre}»: revisá el inventario antes de confirmar.")
            p.stock -= cantidad
            p.stock_reservado = max(p.stock_reservado - reservado, 0)
        pedido.stock_reservado = False
    elif accion in ("rechazar_pago", "cancelar"):
        await _liberar(db_session, pedido)

    pedido.estado = ESTADO_FINAL[accion]
    pedido.decidido_por = usuario_id
    pedido.decidido_en = ahora()
    if pedido.conversacion_id is not None:
        conversacion = await db_session.get(Conversacion, pedido.conversacion_id)
        if conversacion is not None:
            moneda = await _moneda(db_session, organizacion_id)
            await agregar_mensaje(
                db_session, conversacion, "sistema",
                MENSAJES_AL_COMPRADOR[accion].format(total=formatear(pedido.total, moneda)), simulado=pedido.simulado,
            )
    await db_session.commit()
    await db_session.refresh(pedido)
    return pedido


async def _moneda(db_session: AsyncSession, organizacion_id: uuid.UUID) -> str:
    org = await db_session.get(Organizacion, organizacion_id)
    return getattr(org, "moneda", "BOB") or "BOB"
