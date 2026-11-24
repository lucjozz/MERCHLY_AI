"""Integración contra PostgreSQL REAL del inventario (docs/007-Agentes/08).

Aislamiento por organización (RLS), catálogo público sin privados, reservas y fotos.
Se saltea si no hay base (ver test_integracion_seguridad_db.py).
"""

import uuid
from decimal import Decimal

import pytest

from app.tests.test_integracion_seguridad_db import URLS, _disponible

psycopg = pytest.importorskip("psycopg")

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from app.core.database import fijar_organizacion  # noqa: E402
from app.schemas.inventario import ProductoInventarioEdicion, ProductoInventarioEntrada  # noqa: E402
from app.services import inventario  # noqa: E402

pytestmark = pytest.mark.skipif(not _disponible(), reason="Postgres de integración no disponible")


@pytest.fixture(scope="module")
def orgs():
    a, b = uuid.uuid4(), uuid.uuid4()
    with psycopg.connect(URLS[0], autocommit=True) as c:
        for org, nombre in ((a, "TEST-INV Org A"), (b, "TEST-INV Org B")):
            c.execute("INSERT INTO organizaciones (id, nombre) VALUES (%s, %s)", (org, nombre))
    yield {"a": a, "b": b}
    with psycopg.connect(URLS[0], autocommit=True) as c:
        ids = [a, b]
        c.execute("DELETE FROM inventario_fotos WHERE organizacion_id = ANY(%s)", (ids,))
        c.execute("DELETE FROM inventario_productos WHERE organizacion_id = ANY(%s)", (ids,))
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


def _taladro(**extra) -> ProductoInventarioEntrada:
    return ProductoInventarioEntrada(
        nombre="Taladro percutor 800W", especificaciones={"potencia": "800 W"}, precio_venta=Decimal("450"),
        costo_unitario=Decimal("250"), gastos_unitarios=Decimal("40"), proveedor="Proveedor secreto SRL",
        notas_internas="no decir que es importado", stock=5, **extra,
    )


async def test_dos_catalogos_y_aislamiento(orgs, fabrica) -> None:
    async with await _sesion(fabrica, orgs["a"]) as s:
        publicado = await inventario.crear(s, orgs["a"], _taladro(publicado=True))
        oculto = await inventario.crear(s, orgs["a"], ProductoInventarioEntrada(nombre="Prototipo", stock=1))
        assert publicado.margen_unitario == Decimal("160.00") and publicado.disponibles == 5

        _, total, resumen = await inventario.listar_inventario(s, orgs["a"], 1, 50)
        assert total == 2 and resumen.unidades == 6 and resumen.publicados == 1
        assert resumen.valor_a_costo == Decimal("1450.00")  # 5 × (250 + 40)

        publico = await inventario.catalogo_publico(s, orgs["a"])
        assert [p.id for p in publico] == [publicado.id]  # el no publicado no está
        serializado = publico[0].model_dump_json()
        for privado in ("250", "Proveedor secreto", "no decir", "costo", "gastos"):
            assert privado not in serializado

        assert [p.nombre for p in await inventario.catalogo_publico(s, orgs["a"], buscar="taladro")] == [publicado.nombre]

    async with await _sesion(fabrica, orgs["b"]) as s:  # B no ve ni toca nada de A
        assert await inventario.catalogo_publico(s, orgs["b"]) == []
        assert await inventario.obtener(s, orgs["b"], publicado.id) is None
        assert await inventario.obtener(s, orgs["a"], publicado.id) is None  # ni pasando la org de A: RLS
        assert await inventario.editar(s, orgs["b"], publicado.id, ProductoInventarioEdicion(precio_venta=1)) is None
        assert await inventario.eliminar(s, orgs["b"], oculto.id) is False
        assert await inventario.agregar_foto(s, orgs["b"], publicado.id, b"x") is None


async def test_edicion_registra_cambios_y_respeta_reservas(orgs, fabrica) -> None:
    async with await _sesion(fabrica, orgs["a"]) as s:
        p = await inventario.crear(s, orgs["a"], _taladro())
        vista, cambios = await inventario.editar(
            s, orgs["a"], p.id, ProductoInventarioEdicion(precio_venta=Decimal("480"), stock=3, descripcion="Nuevo")
        )
        assert vista.precio_venta == Decimal("480.00") and vista.stock == 3
        assert cambios["precio_venta_antes"] == "450.00" and cambios["precio_venta_ahora"] == "480"
        assert "descripcion" in cambios["otros_campos"] and "Nuevo" not in str(cambios)  # sin textos en la bitácora

    with psycopg.connect(URLS[0], autocommit=True) as c:  # simula una reserva de un pedido (007-09)
        c.execute("UPDATE inventario_productos SET stock_reservado = 2 WHERE id = %s", (p.id,))
    async with await _sesion(fabrica, orgs["a"]) as s:
        assert (await inventario.catalogo_publico(s, orgs["a"], buscar="__nada__")) == []
        with pytest.raises(inventario.StockMenorQueReservadoError):
            await inventario.editar(s, orgs["a"], p.id, ProductoInventarioEdicion(stock=1))
    async with await _sesion(fabrica, orgs["a"]) as s:
        assert (await inventario.obtener_vista(s, orgs["a"], await inventario.obtener(s, orgs["a"], p.id))).disponibles == 1
        assert await inventario.eliminar(s, orgs["a"], p.id) is True
        assert await inventario.obtener(s, orgs["a"], p.id) is None  # borrado lógico


async def test_fotos_tope_y_borrado(orgs, fabrica) -> None:
    async with await _sesion(fabrica, orgs["a"]) as s:
        p = await inventario.crear(s, orgs["a"], ProductoInventarioEntrada(nombre="Con fotos"))
        fotos = [await inventario.agregar_foto(s, orgs["a"], p.id, b"webp") for _ in range(inventario.MAX_FOTOS_POR_PRODUCTO)]
        with pytest.raises(inventario.DemasiadasFotosError):
            await inventario.agregar_foto(s, orgs["a"], p.id, b"webp")
    async with await _sesion(fabrica, orgs["b"]) as s:
        assert await inventario.obtener_foto(s, orgs["b"], fotos[0].id) is None
        assert await inventario.borrar_foto(s, orgs["b"], p.id, fotos[0].id) is False
    async with await _sesion(fabrica, orgs["a"]) as s:
        assert (await inventario.obtener_foto(s, orgs["a"], fotos[0].id)).contenido == b"webp" and fotos[0].tamano == 4
        assert await inventario.borrar_foto(s, orgs["a"], p.id, fotos[0].id) is True
        assert len((await inventario.obtener_vista(s, orgs["a"], await inventario.obtener(s, orgs["a"], p.id))).foto_ids) == 5


def test_tablas_de_inventario_con_rls_forzado() -> None:
    with psycopg.connect(URLS[1]) as c:
        assert c.execute("SELECT count(*) FROM inventario_productos").fetchone()[0] == 0  # sin organización: nada
        assert c.execute("SELECT count(*) FROM inventario_fotos").fetchone()[0] == 0
        with pytest.raises(psycopg.Error):
            c.execute("DELETE FROM inventario_productos")  # el rol de la app no puede borrar productos
