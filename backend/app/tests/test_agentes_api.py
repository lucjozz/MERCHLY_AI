"""Tests for POST /agentes/investigador-producto."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db_session
from app.core.dependencias import obtener_usuario_autenticado
from app.main import app
from app.tests.conftest import override_usuario_autenticado


@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    app.dependency_overrides.clear()


def _override_db_session():
    session = AsyncMock()
    session.add = MagicMock()

    def _get():
        yield session

    return _get


def test_investigar_producto_devuelve_200_con_productos() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session()
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado()

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/investigador-producto",
        json={
            "categoria": "audifonos bluetooth",
            "mercado_objetivo": "BO",
            "cantidad_resultados": 3,
        },
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["productos"]) == 3
    assert cuerpo["metadata"]["confianza"] == "normal"


def test_investigar_producto_rechaza_categoria_prohibida() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session()
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado()

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/investigador-producto",
        json={"categoria": "armas", "mercado_objetivo": "BO"},
    )

    assert respuesta.status_code == 422


def test_investigar_producto_rechaza_mercado_objetivo_invalido() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session()
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado()

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/investigador-producto",
        json={"categoria": "audifonos", "mercado_objetivo": "Bolivia"},
    )

    assert respuesta.status_code == 422


def test_investigar_producto_sin_token_devuelve_403() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session()

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/investigador-producto",
        json={"categoria": "audifonos", "mercado_objetivo": "BO"},
    )

    assert respuesta.status_code == 403


def test_investigar_producto_con_rol_insuficiente_devuelve_403() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session()
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado(
        rol="usuario_operativo"
    )

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/investigador-producto",
        json={"categoria": "audifonos", "mercado_objetivo": "BO"},
    )

    assert respuesta.status_code == 403