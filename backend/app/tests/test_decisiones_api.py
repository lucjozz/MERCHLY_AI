"""Tests for POST /decisiones and GET /decisiones/{id}."""

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


def _override_db_session_para_crear(producto, decision_devuelta) -> None:
    def _get():
        session = AsyncMock()
        session.get = AsyncMock(return_value=producto)
        session.add = MagicMock()

        resultado_select = MagicMock()
        resultado_select.scalar_one_or_none.return_value = decision_devuelta
        session.execute = AsyncMock(return_value=resultado_select)
        yield session

    app.dependency_overrides[get_db_session] = _get


def _decision_orm_fake(decision_id, entity_id, contexto=None, evidencias=None):
    from datetime import datetime, timezone

    from app.models.decisiones import DecisionRecord

    decision = DecisionRecord(
        id=decision_id,
        decision_type="product_selection",
        entity_type="product_candidate",
        entity_id=entity_id,
        action="approve",
        user_id="lucas",
        reason="Buen margen.",
    )
    decision.creado_en = datetime.now(timezone.utc)
    decision.contexto = contexto
    decision.evidencias = evidencias or []
    return decision


def test_crear_decision_devuelve_201_y_estado_actualizado() -> None:
    producto_id = uuid.uuid4()
    producto = SimpleNamespace(id=producto_id, estado="candidato")
    decision_id = uuid.uuid4()
    _override_db_session_para_crear(
        producto, _decision_orm_fake(decision_id, producto_id)
    )

    client = TestClient(app)
    respuesta = client.post(
        "/decisiones",
        json={
            "decision_type": "product_selection",
            "entity_type": "product_candidate",
            "entity_id": str(producto_id),
            "action": "approve",
            "user_id": "lucas",
            "reason": "Buen margen.",
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["action"] == "approve"
    assert producto.estado == "en_catalogo"


def test_crear_decision_incluye_evidencias_en_la_respuesta() -> None:
    """Regresión directa del bug de DEC-030: la evidencia enviada debe
    volver en la respuesta, no perderse."""
    producto_id = uuid.uuid4()
    producto = SimpleNamespace(id=producto_id, estado="candidato")
    decision_id = uuid.uuid4()

    from app.models.decisiones import DecisionContext, DecisionEvidence

    contexto = DecisionContext(
        id=uuid.uuid4(), decision_id=decision_id, context_data={"margen": 0.4}
    )
    evidencia = DecisionEvidence(
        id=uuid.uuid4(),
        decision_id=decision_id,
        source_type="market_research",
        source_url="https://ejemplo.test",
        source_title="Informe",
        evidence="Demanda alta.",
    )
    _override_db_session_para_crear(
        producto,
        _decision_orm_fake(decision_id, producto_id, contexto=contexto, evidencias=[evidencia]),
    )

    client = TestClient(app)
    respuesta = client.post(
        "/decisiones",
        json={
            "decision_type": "product_selection",
            "entity_type": "product_candidate",
            "entity_id": str(producto_id),
            "action": "approve",
            "user_id": "lucas",
            "reason": "Buen margen.",
            "context_data": {"margen": 0.4},
            "evidencias": [
                {
                    "source_type": "market_research",
                    "source_url": "https://ejemplo.test",
                    "source_title": "Informe",
                    "evidence": "Demanda alta.",
                }
            ],
        },
    )

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["context_data"] == {"margen": 0.4}
    assert len(cuerpo["evidencias"]) == 1
    assert cuerpo["evidencias"][0]["evidence"] == "Demanda alta."


def test_crear_decision_producto_inexistente_devuelve_404() -> None:
    _override_db_session_para_crear(None, None)

    client = TestClient(app)
    respuesta = client.post(
        "/decisiones",
        json={
            "decision_type": "product_selection",
            "entity_type": "product_candidate",
            "entity_id": str(uuid.uuid4()),
            "action": "approve",
            "user_id": "lucas",
            "reason": "N/A",
        },
    )

    assert respuesta.status_code == 404


def test_crear_decision_accion_invalida_devuelve_422() -> None:
    client = TestClient(app)
    respuesta = client.post(
        "/decisiones",
        json={
            "decision_type": "product_selection",
            "entity_type": "product_candidate",
            "entity_id": str(uuid.uuid4()),
            "action": "no_existe",
            "user_id": "lucas",
            "reason": "N/A",
        },
    )

    assert respuesta.status_code == 422


def test_obtener_decision_devuelve_200_si_existe() -> None:
    decision_id = uuid.uuid4()
    entity_id = uuid.uuid4()

    def _get():
        session = AsyncMock()
        resultado_select = MagicMock()
        resultado_select.scalar_one_or_none.return_value = _decision_orm_fake(
            decision_id, entity_id
        )
        session.execute = AsyncMock(return_value=resultado_select)
        yield session

    app.dependency_overrides[get_db_session] = _get

    client = TestClient(app)
    respuesta = client.get(f"/decisiones/{decision_id}")

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == str(decision_id)


def test_obtener_decision_devuelve_404_si_no_existe() -> None:
    def _get():
        session = AsyncMock()
        resultado_select = MagicMock()
        resultado_select.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=resultado_select)
        yield session

    app.dependency_overrides[get_db_session] = _get

    client = TestClient(app)
    respuesta = client.get(f"/decisiones/{uuid.uuid4()}")

    assert respuesta.status_code == 404
