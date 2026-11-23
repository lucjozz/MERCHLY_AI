"""Tests de /auth (docs/013-Seguridad/01 y 04): login, rate limiting,
refresh, logout, /me. Base y Redis reemplazados por dobles en memoria."""

import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db_session
from app.core.redis import get_redis_client
from app.core.security import crear_access_token, hashear_password
from app.main import app
from app.tests.conftest import ORG_TEST, RedisCaido, RedisFalso, usuario_falso

PASSWORD = "una-password-larga-de-prueba"
HASH = hashear_password(PASSWORD)


@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def redis_falso() -> RedisFalso:
    r = RedisFalso()
    app.dependency_overrides[get_redis_client] = lambda: r
    return r


def _usuario(activo: bool = True):
    u = usuario_falso()
    u.password_hash = HASH
    u.activo = activo
    u.eliminado_en = None
    return u


def _db(usuario):
    """Sesión falsa: execute -> busca usuario; get -> usuario u organización."""
    organizacion = SimpleNamespace(id=ORG_TEST, nombre="Org Test", activo=True)

    def _get():
        session = AsyncMock()
        session.add = MagicMock()
        session.in_transaction = MagicMock(return_value=False)
        resultado = MagicMock()
        resultado.scalar_one_or_none.return_value = usuario
        session.execute = AsyncMock(return_value=resultado)

        async def _get_por_id(modelo, _id):
            return usuario if modelo.__name__ == "Usuario" else organizacion

        session.get = AsyncMock(side_effect=_get_por_id)
        yield session

    app.dependency_overrides[get_db_session] = _get


def _login(email: str = "test@merchly.ai", password: str = PASSWORD):
    return TestClient(app).post("/auth/login", json={"email": email, "password": password})


def test_login_ok_devuelve_par_de_tokens(redis_falso) -> None:
    _db(_usuario())
    r = _login()
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["access_token"] and cuerpo["refresh_token"]
    assert cuerpo["expira_en"] == 15 * 60
    assert r.headers["cache-control"] == "no-store"


def test_login_normaliza_email_a_minusculas(redis_falso) -> None:
    _db(_usuario())
    assert _login(email="  TEST@Merchly.AI ").status_code == 200


def test_login_credenciales_invalidas_devuelve_401(redis_falso) -> None:
    _db(None)
    r = _login()
    assert r.status_code == 401
    assert r.json()["detail"] == "Email o contraseña incorrectos."


def test_login_mismo_mensaje_para_inexistente_inactivo_y_password_malo(redis_falso) -> None:
    _db(None)
    inexistente = _login().json()
    _db(_usuario(activo=False))
    inactivo = _login().json()
    _db(_usuario())
    malo = _login(password="otra-password-incorrecta").json()
    assert inexistente == inactivo == malo


def test_login_tarda_parecido_si_el_usuario_no_existe(redis_falso) -> None:
    """Anti-enumeración: sin usuario igual se corre bcrypt (hash señuelo)."""
    _db(None)
    t0 = time.perf_counter()
    _login()
    t_inexistente = time.perf_counter() - t0
    _db(_usuario())
    t0 = time.perf_counter()
    _login(password="otra-password-incorrecta")
    t_existente = time.perf_counter() - t0
    assert t_inexistente > t_existente * 0.5


def test_login_bloquea_tras_5_fallos_con_429_y_retry_after(redis_falso) -> None:
    _db(_usuario())
    for _ in range(5):
        assert _login(password="mala-mala-mala").status_code == 401
    r = _login(password="mala-mala-mala")
    assert r.status_code == 429
    assert int(r.headers["retry-after"]) > 0
    # Bloqueado incluso con la contraseña correcta.
    assert _login().status_code == 429


def test_login_correcto_limpia_contador(redis_falso) -> None:
    _db(_usuario())
    for _ in range(4):
        _login(password="mala-mala-mala")
    assert _login().status_code == 200
    for _ in range(4):
        assert _login(password="mala-mala-mala").status_code == 401


def test_login_con_redis_caido_es_fail_closed_503() -> None:
    app.dependency_overrides[get_redis_client] = lambda: RedisCaido()
    _db(_usuario())
    assert _login().status_code == 503


def test_login_password_enorme_devuelve_422_sin_eco(redis_falso) -> None:
    r = _login(password="A" * 129)
    assert r.status_code == 422
    assert "AAAA" not in r.text


def test_login_422_no_devuelve_la_password() -> None:
    r = TestClient(app).post("/auth/login", json={"password": "SECRETO-QUE-NO-DEBE-VOLVER"})
    assert r.status_code == 422
    assert "SECRETO-QUE-NO-DEBE-VOLVER" not in r.text


def test_login_campo_extra_devuelve_422(redis_falso) -> None:
    r = TestClient(app).post(
        "/auth/login", json={"email": "a@b.c", "password": "x", "rol": "admin_principal"}
    )
    assert r.status_code == 422


def test_login_inyeccion_sql_devuelve_401(redis_falso) -> None:
    _db(None)
    assert _login(email="' OR '1'='1' --", password="' OR '1'='1").status_code == 401


def test_auth_me_sin_token_devuelve_401() -> None:
    r = TestClient(app).get("/auth/me")
    assert r.status_code == 401
    assert r.headers["www-authenticate"] == "Bearer"


def test_auth_me_token_valido_devuelve_usuario_sin_hash(redis_falso) -> None:
    u = _usuario()
    _db(u)
    token, _ = crear_access_token(u.id, u.organizacion_id, u.rol, 0)
    r = TestClient(app).get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["email"] == u.email
    assert cuerpo["organizacion_nombre"] == "Org Test"
    assert "password_hash" not in cuerpo and "token_version" not in cuerpo


def test_auth_me_token_invalido_devuelve_401(redis_falso) -> None:
    r = TestClient(app).get("/auth/me", headers={"Authorization": "Bearer basura.basura.basura"})
    assert r.status_code == 401


def test_token_de_version_vieja_devuelve_401(redis_falso) -> None:
    """Tras cerrar todas las sesiones (token_version++), el token viejo no sirve."""
    u = _usuario()
    token, _ = crear_access_token(u.id, u.organizacion_id, u.rol, 0)
    u.token_version = 1
    _db(u)
    r = TestClient(app).get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_usuario_desactivado_pierde_acceso_en_la_siguiente_request(redis_falso) -> None:
    u = _usuario()
    token, _ = crear_access_token(u.id, u.organizacion_id, u.rol, 0)
    u.activo = False
    _db(u)
    r = TestClient(app).get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_logout_revoca_el_access_token(redis_falso) -> None:
    u = _usuario()
    _db(u)
    token, _ = crear_access_token(u.id, u.organizacion_id, u.rol, 0)
    h = {"Authorization": f"Bearer {token}"}
    client = TestClient(app)
    assert client.get("/auth/me", headers=h).status_code == 200
    assert client.post("/auth/logout", headers=h, json={}).status_code == 204
    assert client.get("/auth/me", headers=h).status_code == 401


def test_google_sin_client_id_devuelve_503(redis_falso, monkeypatch) -> None:
    from app.core.config import get_settings

    # Independiente de lo que tenga el .env local.
    monkeypatch.setattr(get_settings(), "google_client_id", None)
    r = TestClient(app).post("/auth/google", json={"id_token": "x" * 30})
    assert r.status_code == 503


def test_refresh_invalido_devuelve_401() -> None:
    resultado = MagicMock()
    resultado.scalar_one_or_none.return_value = None

    def _get():
        session = AsyncMock()
        session.execute = AsyncMock(return_value=resultado)
        yield session

    app.dependency_overrides[get_db_session] = _get
    r = TestClient(app).post("/auth/refresh", json={"refresh_token": "x" * 40})
    assert r.status_code == 401


def test_login_registra_eventos_sin_datos_sensibles(redis_falso, eventos_auditoria) -> None:
    _db(_usuario())
    _login()
    _login(password="otra-password-incorrecta")
    acciones = [e.accion for e in eventos_auditoria]
    assert acciones == ["login_ok", "login_fallido"]
    fallido = eventos_auditoria[1]
    assert fallido.usuario_id is None and "email_hash" in fallido.detalle
    assert "test@merchly.ai" not in str(fallido.detalle) and PASSWORD not in str([e.detalle for e in eventos_auditoria])

