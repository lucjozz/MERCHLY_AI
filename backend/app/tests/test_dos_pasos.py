"""Verificación en dos pasos (docs/013-Seguridad/09): TOTP, cifrado, login con desafío y re-verificación."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core import totp
from app.core.cifrado import CifradoInvalidoError, cifrar, descifrar
from app.core.database import get_db_session
from app.core.redis import get_redis_client
from app.main import app
from app.services import dos_pasos
from app.tests.conftest import RedisFalso
from app.tests.test_auth_api import HASH, PASSWORD, _db, _usuario

# RFC 6238, apéndice B (secreto ASCII "12345678901234567890"), recortado a 6 dígitos.
SECRETO_RFC = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"


@pytest.mark.parametrize("instante, esperado", [(59, "287082"), (1111111109, "081804"), (1234567890, "005924"), (2000000000, "279037")])
def test_vectores_rfc_6238(instante, esperado) -> None:
    assert totp.codigo_actual(SECRETO_RFC, instante) == esperado


def test_ventana_y_anti_repeticion() -> None:
    s = totp.generar_secreto()
    ahora = 1_800_000_000
    codigo = totp.codigo_actual(s, ahora)
    paso = totp.verificar(s, codigo, None, ahora)
    assert paso == totp.paso_actual(ahora)
    assert totp.verificar(s, codigo, paso, ahora) is None  # el mismo código no sirve dos veces
    assert totp.verificar(s, totp.codigo_actual(s, ahora - 30), None, ahora) is not None  # reloj 30 s atrasado
    assert totp.verificar(s, totp.codigo_actual(s, ahora - 90), None, ahora) is None  # muy viejo
    for malo in ("", "12345", "1234567", "abcdef", "12 34 5"):
        assert totp.verificar(s, malo, None, ahora) is None


def test_uri_para_el_celular() -> None:
    u = totp.uri("ABC", "ana@tienda.bo")
    assert u.startswith("otpauth://totp/MERCHLY%20AI%3Aana%40tienda.bo?secret=ABC") and "issuer=MERCHLY%20AI" in u


def test_codigos_de_respaldo() -> None:
    codigos = totp.generar_codigos_respaldo()
    assert len(codigos) == 10 and len(set(codigos)) == 10
    assert all(len(c) == 9 and c[4] == "-" for c in codigos)
    assert totp.hash_respaldo(codigos[0]) == totp.hash_respaldo(codigos[0].lower().replace("-", " "))


def test_cifrado_atado_al_dueno() -> None:
    valor = cifrar("JBSWY3DPEHPK3PXP", "totp:a")
    assert valor.startswith("v1:") and "JBSWY3DP" not in valor
    assert descifrar(valor, "totp:a") == "JBSWY3DPEHPK3PXP"
    with pytest.raises(CifradoInvalidoError):
        descifrar(valor, "totp:b")  # copiado a otro usuario: no se descifra
    roto = valor[:-4] + ("AAAA" if not valor.endswith("AAAA") else "BBBB")
    with pytest.raises(CifradoInvalidoError):
        descifrar(roto, "totp:a")  # alterado
    assert cifrar("x", "c") != cifrar("x", "c")  # nonce aleatorio


async def test_desafio_de_un_solo_uso_y_con_tope_de_intentos() -> None:
    redis = RedisFalso()
    uid = uuid.uuid4()
    token = await dos_pasos.crear_desafio(redis, uid)
    for _ in range(dos_pasos.DESAFIO_MAX_INTENTOS):
        assert await dos_pasos.usuario_del_desafio(redis, token) == uid
    assert await dos_pasos.usuario_del_desafio(redis, token) is None  # 6.º intento: el desafío se borra
    otro = await dos_pasos.crear_desafio(redis, uid)
    await dos_pasos.consumir_desafio(redis, otro)
    assert await dos_pasos.usuario_del_desafio(redis, otro) is None
    assert await dos_pasos.usuario_del_desafio(redis, "inventado" * 4) is None


def test_login_con_dos_pasos_no_entrega_sesion() -> None:
    """Contraseña correcta + 2FA activada → solo un desafío, nunca los tokens."""
    usuario = _usuario()
    usuario.password_hash = HASH
    usuario.totp_activado = True
    _db(usuario)
    app.dependency_overrides[get_redis_client] = lambda: RedisFalso()
    try:
        r = TestClient(app).post("/auth/login", json={"email": "test@merchly.ai", "password": PASSWORD})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["requiere_2fa"] is True and len(cuerpo["desafio"]) > 30
    assert "access_token" not in cuerpo and "refresh_token" not in cuerpo


def test_verificar_con_desafio_inventado_es_401() -> None:
    app.dependency_overrides[get_redis_client] = lambda: RedisFalso()
    app.dependency_overrides[get_db_session] = lambda: None
    try:
        r = TestClient(app).post("/auth/2fa/verificar", json={"desafio": "x" * 40, "codigo": "123456"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 401


# ------------------------------------------------------------ contra la base real

from app.tests.test_integracion_seguridad_db import URLS, _disponible  # noqa: E402

psycopg = pytest.importorskip("psycopg")


@pytest.mark.skipif(not _disponible(), reason="Postgres de integración no disponible")
async def test_alta_uso_y_baja_contra_la_base_real() -> None:
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.core.database import fijar_organizacion
    from app.core.security import hashear_password
    from app.models.usuario import Usuario

    org, uid = uuid.uuid4(), uuid.uuid4()
    with psycopg.connect(URLS[0], autocommit=True) as c:
        c.execute("INSERT INTO organizaciones (id, nombre) VALUES (%s, 'TEST-2FA')", (org,))
        c.execute(
            "INSERT INTO usuarios (id, organizacion_id, email, password_hash, nombre, rol) VALUES (%s, %s, %s, %s, 'Ana', 'admin_principal')",
            (uid, org, f"test-2fa-{uid.hex[:8]}@merchly.test", hashear_password("una-clave-larga-123")),
        )
    engine = create_async_engine(URLS[1].replace("postgresql://", "postgresql+psycopg://"))
    fabrica = async_sessionmaker(engine, expire_on_commit=False)
    redis = RedisFalso()
    try:
        async with fabrica() as s:
            await fijar_organizacion(s, org)
            inicio = await dos_pasos.iniciar(s, uid)
            assert inicio["qr"].startswith("data:image/svg+xml") and inicio["secreto"] in inicio["uri"]
            with pytest.raises(dos_pasos.CodigoInvalidoError):
                await dos_pasos.activar(s, uid, "000000")
            respaldo = await dos_pasos.activar(s, uid, totp.codigo_actual(inicio["secreto"], totp.time.time() - 30))
            assert len(respaldo) == 10

        with psycopg.connect(URLS[0]) as c:  # en la base no hay nada legible
            secreto_db, codigos_db, activado = c.execute(
                "SELECT totp_secreto, codigos_respaldo::text, totp_activado FROM usuarios WHERE id = %s", (uid,)
            ).fetchone()
        assert activado and inicio["secreto"] not in secreto_db and respaldo[0] not in codigos_db

        async with fabrica() as s:
            await fijar_organizacion(s, org)
            codigo = totp.codigo_actual(inicio["secreto"])
            assert await dos_pasos.verificar_codigo(s, uid, codigo) is True
            assert await dos_pasos.verificar_codigo(s, uid, codigo) is False  # anti-repetición
            assert await dos_pasos.verificar_codigo(s, uid, respaldo[0]) is True
            assert await dos_pasos.verificar_codigo(s, uid, respaldo[0]) is False  # respaldo de un solo uso
            assert await dos_pasos.reautenticar(redis, s, uid, None, "una-clave-larga-123") is False  # con 2FA, la contraseña no alcanza
            assert await dos_pasos.reautenticar(redis, s, uid, respaldo[1], None) is True
            assert await dos_pasos.reautenticado(redis, uid) is True
            with pytest.raises(dos_pasos.CodigoInvalidoError):
                await dos_pasos.desactivar(s, uid, "999999")
            await dos_pasos.desactivar(s, uid, respaldo[2])
            usuario = await s.get(Usuario, uid)
            assert usuario.totp_activado is False and usuario.totp_secreto is None and usuario.codigos_respaldo == []
            redis2 = RedisFalso()
            assert await dos_pasos.reautenticar(redis2, s, uid, None, "mala") is False
            assert await dos_pasos.reautenticar(redis2, s, uid, None, "una-clave-larga-123") is True
    finally:
        await engine.dispose()
        with psycopg.connect(URLS[0], autocommit=True) as c:
            c.execute("DELETE FROM usuarios WHERE id = %s", (uid,))
            c.execute("DELETE FROM organizaciones WHERE id = %s", (org,))



def test_confirmar_un_pago_real_exige_reverificacion(monkeypatch) -> None:
    """Sin haber confirmado que sos vos hace menos de 10 minutos, un pago REAL no se confirma."""
    from types import SimpleNamespace

    from app.api import atencion as api_atencion
    from app.core.dependencias import obtener_usuario_autenticado
    from app.tests.conftest import override_usuario_autenticado

    async def pedido_real(*_a, **_k):
        return SimpleNamespace(simulado=False)

    monkeypatch.setattr(api_atencion.venta, "obtener_pedido", pedido_real)
    app.dependency_overrides[obtener_usuario_autenticado] = override_usuario_autenticado("admin_principal")
    app.dependency_overrides[get_redis_client] = lambda: RedisFalso()
    try:
        r = TestClient(app).post(f"/atencion/pedidos/{uuid.uuid4()}/confirmar-pago")
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 403 and r.json()["detail"] == api_atencion.REAUTENTICACION_REQUERIDA
