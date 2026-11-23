"""Tests de la bitácora de auditoría (docs/013-Seguridad/06) sin base real."""

from fastapi.testclient import TestClient

from app.core.dependencias import obtener_usuario_autenticado
from app.main import app
from app.services.auditoria import _limpiar_detalle, hash_corto, registrar_evento
from app.tests.conftest import override_usuario_autenticado


def test_detalle_nunca_guarda_secretos() -> None:
    limpio = _limpiar_detalle({
        "password": "x", "token": "y", "codigo_invitacion": "z", "Authorization": "Bearer a",
        "enlace": "https://...#token", "rol": "admin_principal", "texto_largo": "a" * 500,
    })
    assert set(limpio) == {"rol", "texto_largo"} and len(limpio["texto_largo"]) == 200


def test_hash_corto_no_revela_el_email() -> None:
    h = hash_corto(" Ana@Tienda.com ")
    assert h == hash_corto("ana@tienda.com") and "ana" not in h and len(h) == 16


async def test_accion_desconocida_no_se_registra(eventos_auditoria) -> None:
    await registrar_evento("borrar_todo")
    assert eventos_auditoria == []


async def test_un_fallo_al_registrar_no_corta_la_accion(monkeypatch) -> None:
    from app.services import auditoria

    async def _explota(evento):
        raise RuntimeError("base caída")

    monkeypatch.setattr(auditoria, "_guardar", _explota)
    await registrar_evento("login_ok")  # no lanza


def test_endpoint_de_auditoria_solo_para_admin() -> None:
    assert TestClient(app).get("/auditoria").status_code == 401
    for rol in ("usuario_operativo", "responsable_tecnico", "responsable_negocio"):
        app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado(rol)
        assert TestClient(app).get("/auditoria").status_code == 403, rol
    app.dependency_overrides.clear()
