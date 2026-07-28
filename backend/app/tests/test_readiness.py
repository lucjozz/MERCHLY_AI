"""Tests for the /health/ready endpoint.

Uses FastAPI dependency overrides so these tests do not require a real
PostgreSQL or Redis instance running — they verify the endpoint's own
logic (aggregating dependency statuses), not the infrastructure itself.
End-to-end verification against real containers happens via
``docker compose up -d`` locally.
"""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db_session
from app.core.redis import get_redis_client
from app.main import app


@pytest.fixture(autouse=True)
def _reset_overrides():
    """Ensure dependency overrides never leak between tests."""
    yield
    app.dependency_overrides.clear()


def test_readiness_ok_when_dependencies_are_healthy() -> None:
    """Returns status 'ok' when both DB and Redis respond successfully."""
    mock_session = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True

    def override_db():
        yield mock_session

    def override_redis():
        yield mock_redis

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_redis_client] = override_redis

    client = TestClient(app)
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["redis"] == "ok"


def test_readiness_degraded_when_database_fails() -> None:
    """Returns status 'degraded' (not a 5xx) when the DB check raises."""
    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("connection refused")
    mock_redis = AsyncMock()
    mock_redis.ping.return_value = True

    def override_db():
        yield mock_session

    def override_redis():
        yield mock_redis

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_redis_client] = override_redis

    client = TestClient(app)
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "error"
    assert body["redis"] == "ok"


def test_readiness_degraded_when_redis_fails() -> None:
    """Returns status 'degraded' (not a 5xx) when the Redis check raises."""
    mock_session = AsyncMock()
    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = Exception("connection refused")

    def override_db():
        yield mock_session

    def override_redis():
        yield mock_redis

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_redis_client] = override_redis

    client = TestClient(app)
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "ok"
    assert body["redis"] == "error"
