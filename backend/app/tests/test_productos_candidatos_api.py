"""Tests for GET /productos-candidatos and GET /productos-candidatos/{id}."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db_session
from app.main import app


@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    app.dependency_overrides.clear()


def _producto_fake(**overrides):
    from datetime import datetime, timezone

    base = dict(
        id=uuid.uuid4(),
        nombre_producto="Producto de prueba",
        categoria="audifonos",
        mercado_objetivo="BO",
        precio_estimado_proveedor=10.0,
        precio_sugerido_venta=25.0,
        nivel_demanda_estimado="alto",
        nivel_competencia_estimado="bajo",
        fuentes_evidencia=["https://ejemplo.test"],
        riesgos_identificados=[],
        estado="candidato",
        investigacion_id=uuid.uuid4(),
        creado_en=datetime.now(timezone.utc),
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _override_listado(productos: list, total: int):
    def _get():
        session = AsyncMock()

        resultado_count = MagicMock()
        resultado_total = AsyncMock(return_value=total)
        resultado_pagina = MagicMock()
        resultado_pagina.scalars.return_value.all.return_value = productos

        session.scalar = AsyncMock(return_value=total)
        session.execute = AsyncMock(return_value=resultado_pagina)
        yield session

    app.dependency_overrides[get_db_session] = _get


def test_listar_productos_devuelve_200_con_pagina() -> None:
    producto = _producto_fake()
    _override_listado([producto], total=1)

    client = TestClient(app)
    respuesta = client.get("/productos-candidatos")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["total"] == 1
    assert len(cuerpo["productos"]) == 1
    assert cuerpo["pagina"] == 1


def test_listar_productos_filtra_por_estado_invalido_devuelve_422() -> None:
    _override_listado([], total=0)

    client = TestClient(app)
    respuesta = client.get("/productos-candidatos", params={"estado": "no_existe"})

    assert respuesta.status_code == 422


def test_obtener_producto_devuelve_200_si_existe() -> None:
    producto = _producto_fake()

    def _get():
        session = AsyncMock()
        resultado = MagicMock()
        resultado.scalar_one_or_none.return_value = producto
        session.execute = AsyncMock(return_value=resultado)
        yield session

    app.dependency_overrides[get_db_session] = _get

    client = TestClient(app)
    respuesta = client.get(f"/productos-candidatos/{producto.id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == str(producto.id)


def test_obtener_producto_devuelve_404_si_no_existe() -> None:
    def _get():
        session = AsyncMock()
        resultado = MagicMock()
        resultado.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=resultado)
        yield session

    app.dependency_overrides[get_db_session] = _get

    client = TestClient(app)
    respuesta = client.get(f"/productos-candidatos/{uuid.uuid4()}")

    assert respuesta.status_code == 404
