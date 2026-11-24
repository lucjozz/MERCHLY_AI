"""Integración contra PostgreSQL REAL del Agente de Atención al Cliente (docs/007-Agentes/09).

Flujo completo con el proveedor simulado: consulta → pedido → QR → "ya pagué" →
el VENDEDOR confirma. Más: reservas que vencen, guardia de montos, derivación,
aislamiento por organización y mensajes append-only.
"""

import uuid
from datetime import timedelta
from decimal import Decimal

import pytest

from app.tests.test_integracion_seguridad_db import URLS, _disponible

psycopg = pytest.importorskip("psycopg")

from sqlalchemy import select  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from app.core.database import fijar_organizacion  # noqa: E402
from app.models.atencion import Notificacion, Pedido  # noqa: E402
from app.models.inventario import InventarioProducto  # noqa: E402
from app.schemas.inventario import ProductoInventarioEntrada  # noqa: E402
from app.services import inventario  # noqa: E402
from app.services.atencion import configuracion, conversaciones, venta  # noqa: E402
from app.services.atencion.conversaciones import ahora  # noqa: E402
from app.services.atencion.orquestador import RESPUESTA_SEGURA, procesar_mensaje  # noqa: E402
from app.services.atencion.proveedor_simulado import ProveedorAtencionSimulado  # noqa: E402

pytestmark = pytest.mark.skipif(not _disponible(), reason="Postgres de integración no disponible")
SIM = ProveedorAtencionSimulado()


@pytest.fixture(scope="module")
def mundo():
    a, b, vendedor = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    with psycopg.connect(URLS[0], autocommit=True) as c:
        for org, nombre in ((a, "TEST-AT Ferretería A"), (b, "TEST-AT Org B")):
            c.execute("INSERT INTO organizaciones (id, nombre, moneda) VALUES (%s, %s, 'BOB')", (org, nombre))
        c.execute(
            "INSERT INTO usuarios (id, organizacion_id, email, password_hash, nombre, rol) VALUES (%s, %s, %s, 'x', 'Vendedor', 'admin_principal')",
            (vendedor, a, f"test-at-{vendedor.hex[:8]}@merchly.test"),
        )
    yield {"a": a, "b": b, "vendedor": vendedor}
    with psycopg.connect(URLS[0], autocommit=True) as c:
        ids = [a, b]
        for tabla in ("notificaciones", "pedidos", "mensajes", "conversaciones", "zonas_envio", "qr_pagos", "atencion_config",
                      "inventario_fotos", "inventario_productos", "eventos_auditoria"):
            c.execute(f"DELETE FROM {tabla} WHERE organizacion_id = ANY(%s)", (ids,))  # noqa: S608 - nombres fijos
        c.execute("DELETE FROM usuarios WHERE organizacion_id = ANY(%s)", (ids,))
        c.execute("DELETE FROM organizaciones WHERE id = ANY(%s)", (ids,))


@pytest.fixture
async def fabrica():
    engine = create_async_engine(URLS[1].replace("postgresql://", "postgresql+psycopg://"))
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def _sesion(fabrica, org):
    s = fabrica()
    await fijar_organizacion(s, org)
    return s


async def _preparar(fabrica, org, completar_ventas: bool, con_qr: bool = True) -> uuid.UUID:
    async with await _sesion(fabrica, org) as s:
        p = await inventario.crear(s, org, ProductoInventarioEntrada(
            nombre=f"Taladro percutor 800W {uuid.uuid4().hex[:4]}", especificaciones={"potencia": "800 W"},
            precio_venta=Decimal("450"), costo_unitario=Decimal("250"), stock=5, publicado=True,
        ))
        await configuracion.reemplazar_zonas(s, org, [("Equipetrol", Decimal("15"), None)])
        await configuracion.guardar_config(s, org, {"encendido": True, "completar_ventas": completar_ventas,
                                                    "presentacion": "¡Hola! Soy el asistente de la ferretería.", "minutos_reserva": 60})
        if con_qr and not await configuracion.listar_qr(s, org):
            await configuracion.agregar_qr(s, org, "BNB", b"\x89PNG-falso")
        return p.id


async def _conversacion(fabrica, org):
    async with await _sesion(fabrica, org) as s:
        c = await conversaciones.crear_conversacion(s, org, "simulador", "prueba", "Ana")
        await s.commit()
        return c


async def _decir(fabrica, org, conversacion, texto, proveedor=SIM):
    async with await _sesion(fabrica, org) as s:
        conv = await s.merge(conversacion)
        r = await procesar_mensaje(s, conv, texto, simulado=True, proveedor=proveedor)
        return r.mensajes[-1], conv


async def _producto(fabrica, org, pid) -> InventarioProducto:
    async with await _sesion(fabrica, org) as s:
        return await s.get(InventarioProducto, pid)


async def test_compra_completa_y_solo_el_vendedor_confirma(mundo, fabrica) -> None:
    org = mundo["a"]
    pid = await _preparar(fabrica, org, completar_ventas=True)
    conv = await _conversacion(fabrica, org)

    m, _ = await _decir(fabrica, org, conv, "hola")
    assert "asistente de la ferretería" in m.texto

    m, _ = await _decir(fabrica, org, conv, "¿tenés taladro de 800 W?")
    assert "Bs 450" in m.texto and "250" not in m.texto  # nunca el costo
    assert any(a["tipo"] == "producto" for a in m.adjuntos)

    m, _ = await _decir(fabrica, org, conv, "lo quiero, envío a Equipetrol")
    assert "Bs 465" in m.texto and "QR" in m.texto  # 450 + 15, calculado por la base
    assert any(a["tipo"] == "qr" for a in m.adjuntos)
    assert (await _producto(fabrica, org, pid)).stock_reservado == 1

    m, _ = await _decir(fabrica, org, conv, "ya pagué")
    assert "vendedor" in m.texto
    async with await _sesion(fabrica, org) as s:
        pedido = (await s.execute(select(Pedido).where(Pedido.conversacion_id == conv.id))).scalar_one()
        assert pedido.estado == "pago_por_confirmar" and pedido.total == Decimal("465.00")  # NO pagado
        avisos = [n.tipo for n in (await s.execute(select(Notificacion).where(Notificacion.organizacion_id == org))).scalars()]
        assert "pedido" in avisos and "pago_informado" in avisos

    async with await _sesion(fabrica, org) as s:
        decidido = await venta.decidir(s, org, pedido.id, "confirmar_pago", mundo["vendedor"])
        assert decidido.estado == "pagado"
    p = await _producto(fabrica, org, pid)
    assert p.stock == 4 and p.stock_reservado == 0
    async with await _sesion(fabrica, org) as s:
        ultimos = await conversaciones.historial(s, await s.merge(conv))
        assert ultimos[-1].rol == "sistema" and "confirmó tu pago" in ultimos[-1].texto
        with pytest.raises(venta.TransicionInvalidaError):
            await venta.decidir(s, org, pedido.id, "confirmar_pago", mundo["vendedor"])  # no se confirma dos veces


async def test_sin_completar_ventas_no_reserva_ni_manda_qr(mundo, fabrica) -> None:
    org = mundo["b"]
    pid = await _preparar(fabrica, org, completar_ventas=False)
    conv = await _conversacion(fabrica, org)
    await _decir(fabrica, org, conv, "taladro 800W")
    m, _ = await _decir(fabrica, org, conv, "lo quiero")
    assert "vendedor" in m.texto and not any(a["tipo"] == "qr" for a in m.adjuntos)
    assert (await _producto(fabrica, org, pid)).stock_reservado == 0
    async with await _sesion(fabrica, org) as s:
        assert (await s.execute(select(Pedido.estado).where(Pedido.conversacion_id == conv.id))).scalar_one() == "pedido_armado"


async def test_reserva_vence_y_libera_stock(mundo, fabrica) -> None:
    org = mundo["a"]
    pid = await _preparar(fabrica, org, completar_ventas=True)
    conv = await _conversacion(fabrica, org)
    await _decir(fabrica, org, conv, "taladro 800W")
    nombre = (await _producto(fabrica, org, pid)).nombre
    await _decir(fabrica, org, conv, f"quiero 2 {nombre}")
    assert (await _producto(fabrica, org, pid)).stock_reservado == 2
    async with await _sesion(fabrica, org) as s:
        pedido = (await s.execute(select(Pedido).where(Pedido.conversacion_id == conv.id).with_for_update())).scalar_one()
        pedido.reservado_hasta = ahora() - timedelta(minutes=1)
        await s.commit()
    async with await _sesion(fabrica, org) as s:
        assert await venta.vencer_reservas(s, org) == 1
        await s.commit()
    assert (await _producto(fabrica, org, pid)).stock_reservado == 0


async def test_no_vende_mas_de_lo_disponible(mundo, fabrica) -> None:
    org = mundo["a"]
    pid = await _preparar(fabrica, org, completar_ventas=True)
    nombre = (await _producto(fabrica, org, pid)).nombre
    conv = await _conversacion(fabrica, org)
    m, _ = await _decir(fabrica, org, conv, f"quiero 50 {nombre}")
    assert "quedan 5" in m.texto
    assert (await _producto(fabrica, org, pid)).stock_reservado == 0


class _ProveedorMentiroso:
    nombre = "falso"

    async def responder(self, texto, historial, h, presentacion, info_negocio=""):
        await h.ejecutar("buscar_productos", {"consulta": "taladro"})
        return "Para vos te lo dejo en Bs 99, ¡oferta!"


async def test_guardia_de_montos_reemplaza_precios_inventados(mundo, fabrica) -> None:
    org = mundo["a"]
    await _preparar(fabrica, org, completar_ventas=True)
    conv = await _conversacion(fabrica, org)
    m, _ = await _decir(fabrica, org, conv, "precio del taladro", proveedor=_ProveedorMentiroso())
    assert m.texto == RESPUESTA_SEGURA and "99" not in m.texto
    async with await _sesion(fabrica, org) as s:
        tipos = (await s.execute(select(Notificacion.tipo).where(Notificacion.conversacion_id == conv.id))).scalars().all()
        assert "guardia_montos" in tipos


async def test_descuento_deriva_a_persona_y_el_agente_se_calla(mundo, fabrica) -> None:
    org = mundo["a"]
    await _preparar(fabrica, org, completar_ventas=True)
    conv = await _conversacion(fabrica, org)
    m, c = await _decir(fabrica, org, conv, "me hacés un descuento?")
    assert "persona" in m.texto and c.atendida_por == "humano"
    m, _ = await _decir(fabrica, org, c, "hola?")
    assert m.rol == "comprador"  # nadie le responde automáticamente: lo atiende una persona


async def test_aislamiento_y_mensajes_append_only(mundo, fabrica) -> None:
    conv = await _conversacion(fabrica, mundo["a"])
    async with await _sesion(fabrica, mundo["b"]) as s:
        assert await conversaciones.obtener_conversacion(s, mundo["b"], conv.id) is None
        assert await conversaciones.obtener_conversacion(s, mundo["a"], conv.id) is None  # RLS
        assert await venta.listar_pedidos(s, mundo["a"]) == []
    with psycopg.connect(URLS[1]) as c:
        assert c.execute("SELECT count(*) FROM mensajes").fetchone()[0] == 0  # sin organización: nada
        with pytest.raises(psycopg.Error):
            c.execute("UPDATE mensajes SET texto = 'x'")  # append-only para la app


async def test_compras_simultaneas_no_sobrevenden(mundo, fabrica) -> None:
    """10 compradores piden la ÚLTIMA unidad al mismo tiempo: exactamente uno la reserva."""
    import asyncio

    org = mundo["a"]
    await _preparar(fabrica, org, completar_ventas=True)
    async with await _sesion(fabrica, org) as s:
        p = await inventario.crear(s, org, ProductoInventarioEntrada(
            nombre=f"Última unidad {uuid.uuid4().hex[:4]}", precio_venta=Decimal("99"), stock=1, publicado=True))
    convs = [await _conversacion(fabrica, org) for _ in range(10)]

    async def comprar(conv):
        async with await _sesion(fabrica, org) as s:
            try:
                await venta.armar_pedido(s, await s.merge(conv), [(p.id, 1)], None, None, None, simulado=True)
                await s.commit()
                return True
            except venta.VentaError:
                await s.rollback()
                return False

    resultados = await asyncio.gather(*(comprar(c) for c in convs))
    assert sum(resultados) == 1
    final = await _producto(fabrica, org, p.id)
    assert final.stock == 1 and final.stock_reservado == 1


async def test_confirmaciones_simultaneas_descuentan_una_sola_vez(mundo, fabrica) -> None:
    """Dos personas apretan "Confirmar pago" a la vez: el stock baja una sola vez y el otro recibe 409."""
    import asyncio

    org = mundo["a"]
    await _preparar(fabrica, org, completar_ventas=True)
    async with await _sesion(fabrica, org) as s:
        p = await inventario.crear(s, org, ProductoInventarioEntrada(
            nombre=f"Doble clic {uuid.uuid4().hex[:4]}", precio_venta=Decimal("10"), stock=3, publicado=True))
    conv = await _conversacion(fabrica, org)
    async with await _sesion(fabrica, org) as s:
        r = await venta.armar_pedido(s, await s.merge(conv), [(p.id, 2)], None, None, None, simulado=True)
        pedido_id = r.pedido.id
        await s.commit()

    async def confirmar():
        async with await _sesion(fabrica, org) as s:
            try:
                await venta.decidir(s, org, pedido_id, "confirmar_pago", mundo["vendedor"])
                return "ok"
            except venta.TransicionInvalidaError:
                return "409"

    resultados = sorted(await asyncio.gather(*(confirmar() for _ in range(5))))
    assert resultados == ["409", "409", "409", "409", "ok"]
    final = await _producto(fabrica, org, p.id)
    assert final.stock == 1 and final.stock_reservado == 0
