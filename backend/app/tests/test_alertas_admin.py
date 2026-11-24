"""Aviso de login del admin desde una IP nueva, contra la base real (docs/013-Seguridad/09, sección 9)."""

import uuid

import pytest

from app.tests.test_integracion_seguridad_db import URLS, _disponible

psycopg = pytest.importorskip("psycopg")
pytestmark = pytest.mark.skipif(not _disponible(), reason="Postgres de integración no disponible")


async def test_avisa_solo_si_la_ip_es_nueva(monkeypatch) -> None:
    from app.services import alertas_admin
    from app.services import email as servicio_email

    enviados = []

    async def email_falso(e, cliente=None):
        enviados.append(e)

    monkeypatch.setattr(servicio_email, "enviar_email", email_falso)
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    engine = create_async_engine(URLS[1].replace("postgresql://", "postgresql+psycopg://"))
    f = async_sessionmaker(engine, expire_on_commit=False)
    org, uid = uuid.uuid4(), uuid.uuid4()
    with psycopg.connect(URLS[0], autocommit=True) as c:
        c.execute("INSERT INTO organizaciones (id, nombre) VALUES (%s, 'TEST-ALERTA')", (org,))
        c.execute("INSERT INTO usuarios (id, organizacion_id, email, password_hash, nombre, rol) VALUES (%s, %s, %s, 'x', 'Admin', 'admin_principal')",
                  (uid, org, f"test-alerta-{uid.hex[:8]}@merchly.test"))

        def login(ip):
            c.execute("INSERT INTO eventos_auditoria (id, organizacion_id, usuario_id, accion, ip, detalle, creado_en)"
                      " VALUES (%s, %s, %s, 'login_ok', %s, '{}', now())", (uuid.uuid4(), org, uid, ip))

        try:
            login("200.1.1.1")
            assert await alertas_admin.avisar_si_ip_nueva(uid, org, "a@b.co", "200.1.1.1", None, f) is False  # primer login
            login("200.1.1.1")
            assert await alertas_admin.avisar_si_ip_nueva(uid, org, "a@b.co", "200.1.1.1", None, f) is False  # IP conocida
            login("45.9.9.9")
            assert await alertas_admin.avisar_si_ip_nueva(uid, org, "a@b.co", "45.9.9.9", "Firefox", f) is True  # nueva
            assert len(enviados) == 1 and "45.9.9.9" in enviados[0].texto
            avisos = c.execute("SELECT titulo FROM notificaciones WHERE organizacion_id = %s", (org,)).fetchall()
            assert len(avisos) == 1 and "conexión nueva" in avisos[0][0]
        finally:
            await engine.dispose()
            for tabla in ("notificaciones", "eventos_auditoria"):
                c.execute(f"DELETE FROM {tabla} WHERE organizacion_id = %s", (org,))  # noqa: S608
            c.execute("DELETE FROM usuarios WHERE id = %s", (uid,))
            c.execute("DELETE FROM organizaciones WHERE id = %s", (org,))
