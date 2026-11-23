"""Integración contra PostgreSQL REAL de las funciones de producto (docs/004-Backend/03):
historial de campañas aislado por organización, perfil del negocio, invitaciones
y reglas del equipo. Se saltea si no hay base (ver test_integracion_seguridad_db.py).
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.tests.test_integracion_seguridad_db import URLS, _disponible

psycopg = pytest.importorskip("psycopg")

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from app.core.database import fijar_organizacion  # noqa: E402
from app.core.security import PasswordInvalidaError  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402
from app.schemas.campanas import CampanaEdicion  # noqa: E402
from app.schemas.marketing import MarketingInput, MarketingMetadata, MarketingOutput  # noqa: E402
from app.schemas.organizacion import PerfilEntrada  # noqa: E402
from app.schemas.usuarios import InvitacionEntrada, MiembroCambio  # noqa: E402
from app.services import campanas as svc_campanas  # noqa: E402
from app.services import equipo  # noqa: E402
from app.services.organizacion import actualizar_perfil, contexto_para_ia  # noqa: E402

pytestmark = pytest.mark.skipif(not _disponible(), reason="Postgres de integración no disponible")


@pytest.fixture(scope="module")
def mundo():
    """Dos organizaciones; A con dos admins y un operativo; B con un admin."""
    org_a, org_b = uuid.uuid4(), uuid.uuid4()
    u = {k: uuid.uuid4() for k in ("admin_a", "admin2_a", "oper_a", "admin_b")}
    filas = [
        (u["admin_a"], org_a, "admin_principal"),
        (u["admin2_a"], org_a, "admin_principal"),
        (u["oper_a"], org_a, "usuario_operativo"),
        (u["admin_b"], org_b, "admin_principal"),
    ]
    with psycopg.connect(URLS[0], autocommit=True) as c:
        for org, nombre in ((org_a, "TEST-PROD Org A"), (org_b, "TEST-PROD Org B")):
            c.execute("INSERT INTO organizaciones (id, nombre) VALUES (%s, %s)", (org, nombre))
        for uid, org, rol in filas:
            c.execute(
                "INSERT INTO usuarios (id, organizacion_id, email, password_hash, nombre, rol)"
                " VALUES (%s, %s, %s, 'x', 'Test', %s)",
                (uid, org, f"test-prod-{uid.hex[:10]}@merchly.test", rol),
            )
    yield {"a": org_a, "b": org_b, **u}
    with psycopg.connect(URLS[0], autocommit=True) as c:
        orgs = [org_a, org_b]
        c.execute("DELETE FROM campanas WHERE organizacion_id = ANY(%s)", (orgs,))
        c.execute("DELETE FROM eventos_auditoria WHERE organizacion_id = ANY(%s) OR usuario_id IN (SELECT id FROM usuarios WHERE organizacion_id = ANY(%s))", (orgs, orgs))
        c.execute("DELETE FROM invitaciones WHERE organizacion_id = ANY(%s)", (orgs,))
        c.execute("DELETE FROM refresh_tokens WHERE usuario_id IN (SELECT id FROM usuarios WHERE organizacion_id = ANY(%s))", (orgs,))
        c.execute("DELETE FROM restablecimientos_password WHERE usuario_id IN (SELECT id FROM usuarios WHERE organizacion_id = ANY(%s))", (orgs,))
        c.execute("DELETE FROM usuarios WHERE organizacion_id = ANY(%s)", (orgs,))
        c.execute("DELETE FROM organizaciones WHERE id = ANY(%s)", (orgs,))


@pytest.fixture
async def fabrica():
    engine = create_async_engine(URLS[1].replace("postgresql://", "postgresql+psycopg://"))
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


async def _sesion(fabrica, org):
    s = fabrica()
    await fijar_organizacion(s, org)
    return s


def _salida():
    return MarketingOutput(
        productos_candidato_ids=[uuid.uuid4()],
        angulos_de_campana=["Ángulo"],
        copy_por_canal={"email": [{"titulo": "T", "cuerpo": "C"}]},
        publico_objetivo_sugerido="Público",
        metadata=MarketingMetadata(idioma_destino="es", tono="neutral", modelo="simulado"),
    )


async def _usuario(fabrica, org, uid) -> Usuario:
    async with await _sesion(fabrica, org) as s:
        return await s.get(Usuario, uid)


# ------------------------------------------------------------ campañas


async def test_campanas_aisladas_por_organizacion(mundo, fabrica) -> None:
    entrada = MarketingInput(productos_candidato_ids=[uuid.uuid4()], canales_objetivo=["email"], idioma_destino="es")
    async with await _sesion(fabrica, mundo["a"]) as s:
        campana = await svc_campanas.guardar_campana(s, mundo["a"], mundo["admin_a"], entrada, _salida(), ["Linterna"])
    async with await _sesion(fabrica, mundo["b"]) as s:  # B no la ve ni la toca
        assert await svc_campanas.obtener_campana(s, mundo["b"], campana.id) is None
        assert await svc_campanas.obtener_campana(s, mundo["a"], campana.id) is None  # ni pasando la org de A: RLS
        _, total = await svc_campanas.listar_campanas(s, mundo["b"], 1, 50)
        assert total == 0
        assert await svc_campanas.editar_campana(s, mundo["b"], campana.id, CampanaEdicion(titulo="hack")) is None
        assert await svc_campanas.eliminar_campana(s, mundo["b"], campana.id) is False
    async with await _sesion(fabrica, mundo["a"]) as s:  # A sí
        editada = await svc_campanas.editar_campana(s, mundo["a"], campana.id, CampanaEdicion(titulo="Nueva"))
        assert editada.titulo == "Nueva" and editada.editada is True
        assert editada.contenido["copy_por_canal"]["email"][0]["titulo"] == "T"
        assert await svc_campanas.eliminar_campana(s, mundo["a"], campana.id) is True
        assert await svc_campanas.obtener_campana(s, mundo["a"], campana.id) is None  # borrado lógico


def test_campanas_tienen_rls_forzado() -> None:
    with psycopg.connect(URLS[1]) as c:
        assert c.execute("SELECT count(*) FROM campanas").fetchone()[0] == 0  # sin organización: nada
        with pytest.raises(psycopg.Error):
            c.execute("DELETE FROM campanas")  # el rol de la app no puede borrar


# ------------------------------------------------------------ perfil


async def test_perfil_del_negocio_y_contexto_para_la_ia(mundo, fabrica) -> None:
    perfil = PerfilEntrada(nombre="Tienda Test", pais="bo", rubro="camping", presupuesto_mensual=3000, tipo_cambio=6.96)
    async with await _sesion(fabrica, mundo["a"]) as s:
        org = await actualizar_perfil(s, mundo["a"], perfil)
    assert org.onboarding_completo and org.pais == "BO" and org.moneda == "BOB"
    contexto = contexto_para_ia(org)
    assert contexto["Rubro del negocio"] == "camping" and "3000" in contexto["Presupuesto mensual"]


# ------------------------------------------------------------ equipo


async def test_invitacion_completa_y_token_de_un_solo_uso(mundo, fabrica) -> None:
    admin = await _usuario(fabrica, mundo["a"], mundo["admin_a"])
    email = f"invitado-{uuid.uuid4().hex[:8]}@merchly.test"
    async with await _sesion(fabrica, mundo["a"]) as s:
        invitacion, token = await equipo.invitar(s, admin, InvitacionEntrada(email=email.upper(), rol="responsable_negocio"))
    assert invitacion.email == email and len(token) == 14 and token.count("-") == 2
    with psycopg.connect(URLS[0]) as c:  # en la base no está el token, solo su hash
        assert c.execute("SELECT count(*) FROM invitaciones WHERE token_hash = %s", (token,)).fetchone()[0] == 0

    async with fabrica() as s:
        with pytest.raises(PasswordInvalidaError):
            await equipo.aceptar_invitacion(s, token, "Nuevo", "corta")
    async with fabrica() as s:  # escrito a mano: minúsculas y sin guiones también vale
        nuevo = await equipo.aceptar_invitacion(s, token.replace("-", "").lower(), "Nuevo Miembro", "una-password-larga-ok")
    assert nuevo.organizacion_id == mundo["a"] and nuevo.rol == "responsable_negocio"
    async with fabrica() as s:
        with pytest.raises(equipo.InvitacionInvalidaError):
            await equipo.aceptar_invitacion(s, token, "Otra vez", "una-password-larga-ok")


async def test_invitacion_vencida_o_revocada_no_sirve(mundo, fabrica) -> None:
    admin = await _usuario(fabrica, mundo["a"], mundo["admin_a"])
    async with await _sesion(fabrica, mundo["a"]) as s:
        inv1, token1 = await equipo.invitar(s, admin, InvitacionEntrada(email=f"v-{uuid.uuid4().hex[:8]}@x.co", rol="usuario_operativo"))
        inv2, token2 = await equipo.invitar(s, admin, InvitacionEntrada(email=f"r-{uuid.uuid4().hex[:8]}@x.co", rol="usuario_operativo"))
        assert await equipo.revocar_invitacion(s, mundo["a"], inv2.id)
    with psycopg.connect(URLS[0], autocommit=True) as c:
        c.execute("UPDATE invitaciones SET expira_en = %s WHERE id = %s", (datetime.now(timezone.utc) - timedelta(minutes=1), inv1.id))
    for token in (token1, token2):
        async with fabrica() as s:
            with pytest.raises(equipo.InvitacionInvalidaError):
                await equipo.aceptar_invitacion(s, token, "X", "una-password-larga-ok")


async def test_no_se_puede_invitar_un_email_que_ya_tiene_cuenta(mundo, fabrica) -> None:
    admin = await _usuario(fabrica, mundo["a"], mundo["admin_a"])
    with psycopg.connect(URLS[0]) as c:
        email_b = c.execute("SELECT email FROM usuarios WHERE id = %s", (mundo["admin_b"],)).fetchone()[0]
    async with await _sesion(fabrica, mundo["a"]) as s:
        with pytest.raises(equipo.ReglaEquipoError):
            await equipo.invitar(s, admin, InvitacionEntrada(email=email_b, rol="usuario_operativo"))


async def test_reglas_del_equipo(mundo, fabrica) -> None:
    admin_a = await _usuario(fabrica, mundo["a"], mundo["admin_a"])
    async with await _sesion(fabrica, mundo["a"]) as s:
        with pytest.raises(equipo.ReglaEquipoError):  # no a sí mismo
            await equipo.cambiar_miembro(s, admin_a, admin_a.id, MiembroCambio(rol="usuario_operativo"))
    async with await _sesion(fabrica, mundo["a"]) as s:  # miembro de otra organización: como si no existiera
        assert await equipo.cambiar_miembro(s, admin_a, mundo["admin_b"], MiembroCambio(activo=False)) is None
    async with await _sesion(fabrica, mundo["a"]) as s:  # desactivar cierra sesiones (token_version++)
        oper = await equipo.cambiar_miembro(s, admin_a, mundo["oper_a"], MiembroCambio(activo=False))
        assert oper.activo is False and oper.token_version == 1
    async with await _sesion(fabrica, mundo["a"]) as s:  # bajar al otro admin deja 1: permitido
        otro = await equipo.cambiar_miembro(s, admin_a, mundo["admin2_a"], MiembroCambio(rol="responsable_tecnico"))
        assert otro.rol == "responsable_tecnico"
    otro_admin = await _usuario(fabrica, mundo["a"], mundo["admin2_a"])
    otro_admin.rol = "admin_principal"  # simula a un admin intentando bajar al ÚLTIMO admin activo
    async with await _sesion(fabrica, mundo["a"]) as s:
        with pytest.raises(equipo.ReglaEquipoError):
            await equipo.cambiar_miembro(s, otro_admin, mundo["admin_a"], MiembroCambio(rol="usuario_operativo"))


# ------------------------------------------------------------ recuperar contraseña (DEC-036)


async def test_recuperar_password_de_punta_a_punta(mundo, fabrica, monkeypatch) -> None:
    import re

    from app.services import recuperar_password as rp

    enviados = []

    async def _capturar(email, cliente=None):
        enviados.append(email)

    monkeypatch.setattr(rp, "enviar_email", _capturar)
    with psycopg.connect(URLS[0]) as c:
        email = c.execute("SELECT email FROM usuarios WHERE id = %s", (mundo["admin2_a"],)).fetchone()[0]
        version_antes = c.execute("SELECT token_version FROM usuarios WHERE id = %s", (mundo["admin2_a"],)).fetchone()[0]

    async with fabrica() as s:
        await rp.solicitar_restablecimiento(s, "no-existe-" + email)  # sin rastro ni email
    assert enviados == []

    async with fabrica() as s:
        await rp.solicitar_restablecimiento(s, email.upper())
    token = re.search(r"/restablecer#(\S+)", enviados[-1].texto).group(1)
    with psycopg.connect(URLS[0]) as c:  # en la base no queda el token, solo su hash
        assert c.execute("SELECT count(*) FROM restablecimientos_password WHERE token_hash = %s", (token,)).fetchone()[0] == 0

    async with fabrica() as s:
        with pytest.raises(PasswordInvalidaError):
            await rp.restablecer_password(s, token, "corta")
    async with fabrica() as s:
        await rp.restablecer_password(s, token, "nueva-password-segura-123")
    with psycopg.connect(URLS[0]) as c:
        version = c.execute("SELECT token_version FROM usuarios WHERE id = %s", (mundo["admin2_a"],)).fetchone()[0]
    assert version == version_antes + 1  # se cerraron todas sus sesiones
    async with fabrica() as s:
        with pytest.raises(rp.TokenRestablecimientoInvalidoError):  # un solo uso
            await rp.restablecer_password(s, token, "otra-password-segura-123")


async def test_link_de_restablecimiento_vencido_o_reemplazado(mundo, fabrica, monkeypatch) -> None:
    import re

    from app.services import recuperar_password as rp

    enviados = []

    async def _capturar(email, cliente=None):
        enviados.append(email)

    monkeypatch.setattr(rp, "enviar_email", _capturar)
    with psycopg.connect(URLS[0]) as c:
        email = c.execute("SELECT email FROM usuarios WHERE id = %s", (mundo["admin_b"],)).fetchone()[0]
    async with fabrica() as s:
        await rp.solicitar_restablecimiento(s, email)
    primero = re.search(r"#(\S+)", enviados[-1].texto).group(1)
    async with fabrica() as s:
        await rp.solicitar_restablecimiento(s, email)  # pedir otro invalida el anterior
    segundo = re.search(r"#(\S+)", enviados[-1].texto).group(1)
    async with fabrica() as s:
        with pytest.raises(rp.TokenRestablecimientoInvalidoError):
            await rp.restablecer_password(s, primero, "nueva-password-segura-123")
    with psycopg.connect(URLS[0], autocommit=True) as c:
        c.execute("UPDATE restablecimientos_password SET expira_en = now() - interval '1 minute' WHERE usado_en IS NULL")
    async with fabrica() as s:
        with pytest.raises(rp.TokenRestablecimientoInvalidoError):
            await rp.restablecer_password(s, segundo, "nueva-password-segura-123")


# ------------------------------------------------------------ bitácora de auditoría (DEC-037)


async def test_bitacora_append_only_y_aislada(mundo, fabrica) -> None:
    from app.models.evento_auditoria import EventoAuditoria
    from app.services.auditoria import listar_eventos

    # Inserta con el rol de la app y SIN organización fijada (como un login): la política lo permite.
    async with fabrica() as s:
        s.add_all([
            EventoAuditoria(organizacion_id=mundo["a"], usuario_id=mundo["admin_a"], accion="login_ok", detalle={}),
            EventoAuditoria(organizacion_id=mundo["b"], usuario_id=mundo["admin_b"], accion="login_ok", detalle={}),
            EventoAuditoria(organizacion_id=None, accion="login_fallido", detalle={"email_hash": "x"}),
        ])
        await s.commit()

    async with await _sesion(fabrica, mundo["a"]) as s:
        eventos, total = await listar_eventos(s, mundo["a"], 1, 50)
        assert total >= 1 and {e.organizacion_id for e in eventos} == {mundo["a"]}
        otros, total_b = await listar_eventos(s, mundo["b"], 1, 50)  # aunque pida los de B: RLS
        assert total_b == 0 and otros == []

    with psycopg.connect(URLS[1]) as c, c.cursor() as cur:  # el rol de la app no puede alterar la bitácora
        cur.execute("SELECT set_config('app.organizacion_id', %s, true)", (str(mundo["a"]),))
        for sql in ("UPDATE eventos_auditoria SET accion = 'nada'", "DELETE FROM eventos_auditoria"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                cur.execute(sql)
            c.rollback()
            cur.execute("SELECT set_config('app.organizacion_id', %s, true)", (str(mundo["a"]),))
