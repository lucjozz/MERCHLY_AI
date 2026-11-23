"""Suite de regresión de seguridad (docs/013-Seguridad/04).

Cubre: validación estricta de JWT, refresh tokens, contraseñas, rate
limiting, headers, CORS, tope de body, errores sin filtración, docs
ocultos, paginación sin 500 y la matriz rol x endpoint.
"""

import base64
import hashlib
import json
import time
import uuid

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.core.dependencias import obtener_usuario_autenticado
from app.core.security import (
    PasswordInvalidaError,
    crear_access_token,
    decodificar_access_token,
    generar_refresh_token,
    hashear_password,
    hashear_refresh_token,
    necesita_rehash,
    verificar_password,
)
from app.main import app
from app.services.limites import LimitesLogin, consumir_cuota, jti_revocado, revocar_jti
from app.tests.conftest import ORG_TEST, RedisFalso, override_usuario_autenticado

S = get_settings()


@pytest.fixture(autouse=True)
def _reset_overrides():
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------- JWT


def _claims_base(**cambios) -> dict:
    ahora = int(time.time())
    base = {
        "sub": str(uuid.uuid4()),
        "org": str(ORG_TEST),
        "rol": "admin_principal",
        "ver": 0,
        "typ": "access",
        "iss": S.jwt_issuer,
        "aud": S.jwt_audience,
        "iat": ahora,
        "exp": ahora + 600,
        "jti": "abc123",
    }
    base.update(cambios)
    return base


def _firmar(claims: dict, clave: str = S.jwt_secret_key, alg: str = "HS256") -> str:
    return jwt.encode(claims, clave, algorithm=alg)


def test_token_valido_se_acepta() -> None:
    token, _ = crear_access_token(uuid.uuid4(), ORG_TEST, "admin_principal", 0)
    claims = decodificar_access_token(token)
    assert claims is not None and claims.organizacion_id == ORG_TEST


def test_token_vencido_se_rechaza() -> None:
    ahora = int(time.time())
    assert decodificar_access_token(_firmar(_claims_base(iat=ahora - 1000, exp=ahora - 100))) is None


def test_token_firmado_con_otra_clave_se_rechaza() -> None:
    assert decodificar_access_token(_firmar(_claims_base(), clave="otra-clave-de-32-caracteres-xxxxxx")) is None


def test_token_alg_none_se_rechaza() -> None:
    h = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(json.dumps(_claims_base()).encode()).rstrip(b"=").decode()
    assert decodificar_access_token(f"{h}.{p}.") is None


def test_token_con_otro_algoritmo_hs512_se_rechaza() -> None:
    assert decodificar_access_token(_firmar(_claims_base(), alg="HS512")) is None


@pytest.mark.parametrize("faltante", ["exp", "iat", "sub", "jti", "iss", "aud", "org", "rol", "typ", "ver"])
def test_token_sin_claim_obligatorio_se_rechaza(faltante: str) -> None:
    claims = _claims_base()
    del claims[faltante]
    assert decodificar_access_token(_firmar(claims)) is None


@pytest.mark.parametrize(
    "cambio",
    [{"iss": "otro"}, {"aud": "otra-api"}, {"typ": "refresh"}, {"sub": "no-es-uuid"}, {"org": "1 OR 1=1"}],
)
def test_token_con_claims_invalidos_se_rechaza(cambio: dict) -> None:
    assert decodificar_access_token(_firmar(_claims_base(**cambio))) is None


def test_token_firmado_con_secreto_por_defecto_se_rechaza_si_hay_secreto_propio() -> None:
    if S.jwt_secret_key == "cambiar-en-produccion":
        pytest.skip("los tests corren con el secreto por defecto")
    assert decodificar_access_token(_firmar(_claims_base(), clave="cambiar-en-produccion")) is None


def test_endpoint_con_token_mal_firmado_devuelve_401_no_500() -> None:
    token = _firmar(_claims_base(sub="no-es-uuid"), clave="x" * 40)
    r = TestClient(app).get("/productos-candidatos", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


async def test_denylist_de_jti() -> None:
    r = RedisFalso()

    assert not await jti_revocado(r, "j1")
    await revocar_jti(r, "j1", 100)
    assert await jti_revocado(r, "j1")


# ---------------------------------------------------------------- arranque


def test_arranque_rechaza_secreto_debil() -> None:
    assert Settings(jwt_secret_key="cambiar-en-produccion").problemas_de_seguridad()
    assert Settings(jwt_secret_key="corto").problemas_de_seguridad()
    assert not Settings(jwt_secret_key="x" * 64).problemas_de_seguridad()


def test_arranque_rechaza_docs_en_produccion() -> None:
    assert Settings(jwt_secret_key="x" * 64, environment="production", exponer_docs=True).problemas_de_seguridad()


def test_cors_nunca_acepta_comodin() -> None:
    assert Settings(cors_origenes="*, https://app.merchly.ai").lista_cors_origenes == ["https://app.merchly.ai"]


# ---------------------------------------------------------------- contraseñas


def test_politica_password() -> None:
    with pytest.raises(PasswordInvalidaError):
        hashear_password("corta")
    with pytest.raises(PasswordInvalidaError):
        hashear_password("ñ" * 40)  # 80 bytes > 72
    h = hashear_password("una-password-valida")
    assert h.startswith("$2b$12$")
    assert verificar_password("una-password-valida", h)
    assert not verificar_password("otra", h)


def test_password_de_mas_de_72_bytes_nunca_coincide() -> None:
    base = "a" * 72
    h = hashear_password("a" * 20)
    assert not verificar_password(base + "extra", h)


def test_verificar_sin_hash_devuelve_false() -> None:
    assert verificar_password("lo-que-sea", None) is False


def test_necesita_rehash_con_costo_menor() -> None:
    import bcrypt

    viejo = bcrypt.hashpw(b"x", bcrypt.gensalt(10)).decode()
    assert necesita_rehash(viejo)
    assert not necesita_rehash(hashear_password("una-password-valida"))


def test_refresh_token_se_guarda_hasheado() -> None:
    token, h = generar_refresh_token()
    assert h == hashlib.sha256(token.encode()).hexdigest() == hashear_refresh_token(token)
    assert token not in h and len(token) >= 60


# ---------------------------------------------------------------- límites


async def test_limites_login_por_email_ip_y_por_ip() -> None:
    r = RedisFalso()
    lim = LimitesLogin(r, max_email_ip=3, max_ip=5, ventana=900)

    for _ in range(3):
        await lim.registrar_fallo("a@b.c", "1.1.1.1")
    assert await lim.segundos_bloqueado("a@b.c", "1.1.1.1") > 0
    assert await lim.segundos_bloqueado("otro@b.c", "1.1.1.1") == 0  # IP aún con margen
    for _ in range(2):
        await lim.registrar_fallo("otro@b.c", "1.1.1.1")
    assert await lim.segundos_bloqueado("tercero@b.c", "1.1.1.1") > 0  # IP bloqueada
    assert await lim.segundos_bloqueado("a@b.c", "2.2.2.2") == 0
    # Las claves no guardan el email ni la IP en claro.
    assert all("a@b.c" not in k and "1.1.1.1" not in k for k in r.datos)


async def test_cuota_por_organizacion() -> None:
    r = RedisFalso()

    for _ in range(3):
        assert await consumir_cuota(r, "investigador", "org-a", 3, 3600) == 0
    assert await consumir_cuota(r, "investigador", "org-a", 3, 3600) > 0
    assert await consumir_cuota(r, "investigador", "org-b", 3, 3600) == 0


# ---------------------------------------------------------------- HTTP


def test_headers_de_seguridad_y_request_id() -> None:
    r = TestClient(app).get("/health")
    for h, v in [
        ("x-content-type-options", "nosniff"),
        ("x-frame-options", "DENY"),
        ("referrer-policy", "strict-origin-when-cross-origin"),
        ("cache-control", "no-store"),
    ]:
        assert r.headers.get(h) == v
    assert "permissions-policy" in r.headers
    assert len(r.headers["x-request-id"]) == 32


def test_docs_ocultos_por_defecto() -> None:
    client = TestClient(app)
    for ruta in ("/docs", "/redoc", "/openapi.json"):
        assert client.get(ruta).status_code == 404


def test_cors_rechaza_origen_ajeno_y_acepta_el_propio() -> None:
    client = TestClient(app)
    ajeno = client.options(
        "/auth/login",
        headers={"Origin": "https://malicioso.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in ajeno.headers
    propio = client.options(
        "/auth/login",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert propio.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert propio.headers.get("access-control-allow-credentials") is None


def test_body_demasiado_grande_devuelve_413() -> None:
    r = TestClient(app).post(
        "/auth/login", content=b"{" + b" " * (S.max_body_bytes + 10) + b"}",
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 413


def test_error_interno_no_filtra_detalles() -> None:
    from app.core.database import get_db_session

    def _sesion_que_explota():
        class _Boom:
            async def scalar(self, *a, **k):
                raise RuntimeError("postgresql://merchly:SECRETO@db/merchly tabla usuarios")

            async def execute(self, *a, **k):
                raise RuntimeError("SECRETO")

            def in_transaction(self):
                return False

        yield _Boom()

    app.dependency_overrides[get_db_session] = _sesion_que_explota
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado()
    r = TestClient(app, raise_server_exceptions=False).get("/productos-candidatos")
    assert r.status_code == 500
    assert "SECRETO" not in r.text and "postgresql" not in r.text
    assert r.json()["request_id"]


@pytest.mark.parametrize(
    "query", ["tamano_pagina=1000", "tamano_pagina=0", "pagina=0", "pagina=-5", "mercado_objetivo=XXX"]
)
def test_paginacion_invalida_devuelve_422_no_500(query: str) -> None:
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado()
    r = TestClient(app).get(f"/productos-candidatos?{query}")
    assert r.status_code == 422


# ---------------------------------------------------------------- matriz rol x endpoint

_ID = str(uuid.uuid4())
_DECISION = {
    "decision_type": "product_selection",
    "entity_type": "product_candidate",
    "entity_id": _ID,
    "action": "approve",
    "reason": "x",
}
# (método, ruta, body, roles que NO pueden -> 403)
MATRIZ = [
    ("post", "/agentes/investigador-producto", {"categoria": "x", "mercado_objetivo": "BO"}, {"usuario_operativo"}),
    ("post", "/agentes/marketing", {"productos_candidato_ids": [_ID], "canales_objetivo": ["email"], "idioma_destino": "es"}, {"usuario_operativo"}),
    ("post", "/decisiones", _DECISION, {"usuario_operativo"}),
    ("delete", f"/productos-candidatos/{_ID}", None, {"usuario_operativo", "responsable_tecnico"}),
    ("patch", f"/campanas/{_ID}", {"titulo": "x"}, {"usuario_operativo"}),
    ("delete", f"/campanas/{_ID}", None, {"usuario_operativo"}),
    ("put", "/organizacion/perfil", {"nombre": "Mi tienda", "pais": "BO", "rubro": "ropa"},
     {"usuario_operativo", "responsable_tecnico", "responsable_negocio"}),
    ("get", "/usuarios", None, {"usuario_operativo", "responsable_tecnico", "responsable_negocio"}),
    ("post", "/usuarios/invitaciones", {"email": "a@b.co", "rol": "usuario_operativo"},
     {"usuario_operativo", "responsable_tecnico", "responsable_negocio"}),
    ("patch", f"/usuarios/{_ID}", {"rol": "admin_principal"},
     {"usuario_operativo", "responsable_tecnico", "responsable_negocio"}),
]
ROLES = ["admin_principal", "responsable_tecnico", "responsable_negocio", "usuario_operativo"]


@pytest.mark.parametrize("metodo, ruta, body, prohibidos", MATRIZ)
@pytest.mark.parametrize("rol", ROLES)
def test_matriz_rol_x_endpoint(metodo, ruta, body, prohibidos, rol) -> None:
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado(rol)
    client = TestClient(app, raise_server_exceptions=False)
    r = client.request(metodo, ruta, json=body) if body is not None else client.request(metodo, ruta)
    if rol in prohibidos:
        assert r.status_code == 403, (rol, ruta)
    else:
        assert r.status_code != 403, (rol, ruta)


@pytest.mark.parametrize(
    "metodo, ruta",
    [
        ("get", "/productos-candidatos"),
        ("get", f"/productos-candidatos/{_ID}"),
        ("delete", f"/productos-candidatos/{_ID}"),
        ("get", f"/decisiones/{_ID}"),
        ("post", "/decisiones"),
        ("post", "/agentes/investigador-producto"),
        ("post", "/agentes/marketing"),
        ("post", "/agentes/analitica-basica"),
        ("get", "/auth/me"),
        ("post", "/auth/logout"),
        ("post", "/auth/cerrar-todas-las-sesiones"),
        ("get", "/campanas"),
        ("get", f"/campanas/{_ID}"),
        ("patch", f"/campanas/{_ID}"),
        ("delete", f"/campanas/{_ID}"),
        ("get", "/organizacion"),
        ("put", "/organizacion/perfil"),
        ("get", "/organizacion/uso"),
        ("get", "/usuarios"),
        ("patch", f"/usuarios/{_ID}"),
        ("get", "/usuarios/invitaciones"),
        ("post", "/usuarios/invitaciones"),
        ("delete", f"/usuarios/invitaciones/{_ID}"),
        ("get", "/tipo-cambio"),
    ],
)
def test_todo_exige_autenticacion(metodo: str, ruta: str) -> None:
    r = TestClient(app).request(metodo, ruta, json={})
    assert r.status_code == 401, ruta


def test_rutas_publicas_son_solo_las_esperadas() -> None:
    """Si alguien agrega un endpoint sin auth, este test lo detecta."""
    publicas_esperadas = {
        "/health", "/health/ready", "/auth/login", "/auth/refresh", "/auth/google", "/auth/aceptar-invitacion"
    }
    publicas = set()
    rutas = []
    for item in app.routes:
        original = getattr(item, "original_router", None)
        rutas.extend(original.routes if original is not None else [item])
    assert len(rutas) >= 15  # sanity: se recorrieron los routers reales
    for ruta in rutas:
        dependencias = getattr(ruta, "dependant", None)
        if dependencias is None:
            continue
        nombres = set()

        def _recorrer(d):
            for sub in d.dependencies:
                nombres.add(getattr(sub.call, "__name__", ""))
                _recorrer(sub)

        _recorrer(dependencias)
        if not nombres & {"obtener_claims", "obtener_usuario_autenticado", "_verificar"}:
            publicas.add(ruta.path)
    assert publicas == publicas_esperadas
