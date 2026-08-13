"""Tests for POST /agentes/marketing."""

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


def _override_db_session(productos: list):
    def _get():
        session = AsyncMock()
        resultado = MagicMock()
        resultado.scalars.return_value.all.return_value = productos
        session.execute = AsyncMock(return_value=resultado)
        yield session

    return _get


def test_marketing_devuelve_200_para_producto_en_catalogo() -> None:
    producto_id = uuid.uuid4()
    producto = SimpleNamespace(
        id=producto_id,
        nombre_producto="Producto de prueba",
        estado="en_catalogo",
        fuentes_evidencia=["https://ejemplo.test"],
    )
    app.dependency_overrides[get_db_session] = _override_db_session([producto])

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/marketing",
        json={
            "productos_candidato_ids": [str(producto_id)],
            "canales_objetivo": ["email"],
            "idioma_destino": "es",
        },
    )

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["angulos_de_campana"]) > 0


def test_marketing_rechaza_producto_inexistente_con_422() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session([])

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/marketing",
        json={
            "productos_candidato_ids": [str(uuid.uuid4())],
            "canales_objetivo": ["email"],
            "idioma_destino": "es",
        },
    )

    assert respuesta.status_code == 422


def test_marketing_rechaza_canales_vacios_con_422() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session([])

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/marketing",
        json={
            "productos_candidato_ids": [str(uuid.uuid4())],
            "canales_objetivo": [],
            "idioma_destino": "es",
        },
    )

    assert respuesta.status_code == 422
