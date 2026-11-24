"""Límite general de pedidos por minuto (docs/013-Seguridad/09, sección 8)."""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.redis import get_redis_client
from app.core.security import crear_access_token
from app.main import app
from app.tests.conftest import ORG_TEST, RedisCaido, RedisFalso, usuario_falso


def _cliente(redis) -> TestClient:
    app.dependency_overrides[get_redis_client] = lambda: redis
    return TestClient(app, raise_server_exceptions=False)


def test_sin_sesion_se_limita_por_ip(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "limite_anonimo_por_minuto", 3)
    c = _cliente(RedisFalso())
    codigos = [c.post("/auth/olvide-password", json={"email": "a@b.co"}).status_code for _ in range(5)]
    assert codigos[:3] != [429] * 3 and codigos[3:] == [429, 429]
    r = c.post("/auth/olvide-password", json={"email": "a@b.co"})
    assert r.status_code == 429 and int(r.headers["retry-after"]) <= 60


def test_refresh_tiene_su_propio_tope(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "limite_refresh_por_minuto", 2)
    c = _cliente(RedisFalso())
    codigos = [c.post("/auth/refresh", json={"refresh_token": "x" * 40}).status_code for _ in range(4)]
    assert codigos[-1] == 429


def test_con_sesion_se_limita_por_usuario_y_no_por_ip(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "limite_lecturas_por_minuto", 2)
    c = _cliente(RedisFalso())
    u1, u2 = usuario_falso(), usuario_falso()
    t1 = crear_access_token(u1.id, ORG_TEST, "admin_principal", 0)[0]
    t2 = crear_access_token(u2.id, ORG_TEST, "admin_principal", 0)[0]
    for _ in range(2):
        c.get("/temporadas", headers={"Authorization": f"Bearer {t1}"})
    assert c.get("/temporadas", headers={"Authorization": f"Bearer {t1}"}).status_code == 429
    # Otro usuario desde la misma IP (todos llegan por el BFF) no se ve afectado.
    assert c.get("/temporadas", headers={"Authorization": f"Bearer {t2}"}).status_code != 429


def test_health_no_se_limita(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "limite_anonimo_por_minuto", 1)
    c = _cliente(RedisFalso())
    assert all(c.get("/health").status_code == 200 for _ in range(5))


def test_sin_redis_deja_pasar(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "limite_anonimo_por_minuto", 1)
    c = _cliente(RedisCaido())
    assert c.get("/temporadas").status_code == 401  # pasó el límite (fail-open) y lo frenó la autenticación
