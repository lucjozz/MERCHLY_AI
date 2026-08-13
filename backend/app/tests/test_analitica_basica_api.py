"""Tests for POST /agentes/analitica-basica."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db_session
from app.main import app


@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    app.dependency_overrides.clear()


def _override_db_session_vacia():
    session = AsyncMock()
    resultado = MagicMock()
    resultado.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=resultado)

    def _get():
        yield session

    return _get


def test_analitica_basica_devuelve_200_con_reporte_vacio() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session_vacia()

    client = TestClient(app)
    respuesta = client.post("/agentes/analitica-basica", json={})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["resumen_catalogo"]["total_productos_candidatos"] == 0
    assert cuerpo["tasa_conversion_catalogo"]["tasa_candidato_a_en_catalogo"] == 0.0


def test_analitica_basica_rechaza_rango_de_fechas_invalido() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session_vacia()

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/analitica-basica",
        json={"fecha_desde": "2026-08-05", "fecha_hasta": "2026-08-01"},
    )

    assert respuesta.status_code == 422


def test_analitica_basica_rechaza_mercado_objetivo_invalido() -> None:
    app.dependency_overrides[get_db_session] = _override_db_session_vacia()

    client = TestClient(app)
    respuesta = client.post(
        "/agentes/analitica-basica", json={"mercado_objetivo": "Bolivia"}
    )

    assert respuesta.status_code == 422
