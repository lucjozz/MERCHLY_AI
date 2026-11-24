"""Tests for the /health endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """The /health endpoint should respond 200 with status 'ok'."""
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body
    # Público: sin nombre del servicio, versión ni entorno (pistas para un atacante).
    assert not {"service", "version", "environment"} & set(body)
