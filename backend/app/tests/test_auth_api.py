"""Tests para POST /auth/login y GET /auth/me."""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db_session
from app.core.dependencias import obtener_usuario_autenticado
from app.core.security import crear_token
from app.main import app
from app.models.usuario import Usuario
from app.tests.conftest import usuario_falso, override_usuario_autenticado


@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    app.dependency_overrides.clear()


def _usuario_orm(activo: bool = True) -> Usuario:
    u = usuario_falso()
    u.activo = activo
    u.password_hash = "$2b$12$.RTiPHK/zlhoInsBodaO1.dtROCu0v3qF5I7FvDjvOofIsk861SNS"
    return u


def _db_con_usuario(usuario):
    def _get():
        session = AsyncMock()
        resultado = MagicMock()
        resultado.scalar_one_or_none.return_value = usuario
        session.execute = AsyncMock(return_value=resultado)
        session.get = AsyncMock(return_value=usuario)
        yield session
    return _get


def test_login_credenciales_invalidas_devuelve_401():
    app.dependency_overrides[get_db_session] = _db_con_usuario(None)
    client = TestClient(app)
    respuesta = client.post(
        "/auth/login", json={"email": "no@existe.com", "password": "mal"}
    )
    assert respuesta.status_code == 401


def test_login_usuario_inactivo_devuelve_401():
    app.dependency_overrides[get_db_session] = _db_con_usuario(
        _usuario_orm(activo=False)
    )
    client = TestClient(app)
    respuesta = client.post(
        "/auth/login",
        json={"email": "test@merchly.ai", "password": "cualquiera"},
    )
    assert respuesta.status_code == 401


def test_login_mismo_mensaje_para_usuario_inexistente_y_password_malo():
    """El backend no distingue 'no existe' de 'password incorrecto'."""
    app.dependency_overrides[get_db_session] = _db_con_usuario(None)
    client = TestClient(app)
    r1 = client.post(
        "/auth/login", json={"email": "x@x.com", "password": "mal"}
    )
    app.dependency_overrides[get_db_session] = _db_con_usuario(
        _usuario_orm(activo=True)
    )
    r2 = client.post(
        "/auth/login", json={"email": "test@merchly.ai", "password": "wrongpassword"}
    )
    assert r1.status_code == 401
    assert r2.status_code == 401
    assert r1.json()["detail"] == r2.json()["detail"]


def test_login_cuerpo_invalido_devuelve_422():
    client = TestClient(app)
    respuesta = client.post("/auth/login", json={"solo_email": "x@x.com"})
    assert respuesta.status_code == 422


def test_auth_me_sin_token_devuelve_403():
    client = TestClient(app)
    respuesta = client.get("/auth/me")
    assert respuesta.status_code == 403


def test_auth_me_token_valido_devuelve_usuario():
    usuario = _usuario_orm()
    app.dependency_overrides[get_db_session] = _db_con_usuario(usuario)
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado()
    client = TestClient(app)
    respuesta = client.get("/auth/me")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["rol"] == "admin_principal"
    assert "email" in cuerpo
    assert "password_hash" not in cuerpo


def test_auth_me_token_invalido_devuelve_403():
    client = TestClient(app)
    respuesta = client.get(
        "/auth/me", headers={"Authorization": "Bearer token.falso.aqui"}
    )
    assert respuesta.status_code == 401