"""Retención de datos (ops/retencion/limpiar.py) contra la base real: borra lo viejo y no toca lo nuevo."""

import importlib.util
import pathlib
import uuid

import pytest

from app.tests.test_integracion_seguridad_db import URLS, _disponible

psycopg = pytest.importorskip("psycopg")
pytestmark = pytest.mark.skipif(not _disponible(), reason="Postgres de integración no disponible")

_RUTA = pathlib.Path(__file__).resolve().parents[3] / "ops" / "retencion" / "limpiar.py"
_spec = importlib.util.spec_from_file_location("limpiar", _RUTA)
limpiar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(limpiar)


def test_retencion_borra_y_anonimiza_solo_lo_viejo() -> None:
    org = uuid.uuid4()
    conv_vieja, conv_nueva = uuid.uuid4(), uuid.uuid4()
    with psycopg.connect(URLS[0], autocommit=True) as c:
        c.execute("INSERT INTO organizaciones (id, nombre) VALUES (%s, 'TEST-RETENCION')", (org,))
        for conv, hace in ((conv_vieja, "13 months"), (conv_nueva, "1 day")):
            c.execute(
                "INSERT INTO conversaciones (id, organizacion_id, canal, contacto, nombre_contacto, ultimo_mensaje_en, creado_en)"
                f" VALUES (%s, %s, 'whatsapp', '+59170000000', 'Ana', now() - interval '{hace}', now() - interval '{hace}')",  # noqa: S608
                (conv, org),
            )
            c.execute(
                "INSERT INTO mensajes (id, organizacion_id, conversacion_id, rol, texto, creado_en)"
                f" VALUES (%s, %s, %s, 'comprador', 'hola', now() - interval '{hace}')",  # noqa: S608
                (uuid.uuid4(), org, conv),
            )
            c.execute(
                "INSERT INTO pedidos (id, organizacion_id, conversacion_id, estado, items, subtotal, total, nombre_comprador, direccion, creado_en)"
                f" VALUES (%s, %s, %s, 'pagado', '[]', 10, 10, 'Ana', 'Calle 1', now() - interval '{hace}')",  # noqa: S608
                (uuid.uuid4(), org, conv),
            )
            c.execute(
                f"INSERT INTO notificaciones (id, organizacion_id, tipo, titulo, creado_en) VALUES (%s, %s, 'x', 'x', now() - interval '{hace}')",  # noqa: S608
                (uuid.uuid4(), org),
            )
        c.execute(limpiar.script_aplicar())
        mensajes = c.execute("SELECT conversacion_id FROM mensajes WHERE organizacion_id = %s", (org,)).fetchall()
        assert [m[0] for m in mensajes] == [conv_nueva]
        convs = dict(c.execute("SELECT id, contacto FROM conversaciones WHERE organizacion_id = %s", (org,)).fetchall())
        assert convs[conv_vieja] == "anonimizado" and convs[conv_nueva] == "+59170000000"
        pedidos = c.execute(
            "SELECT conversacion_id, nombre_comprador, total FROM pedidos WHERE organizacion_id = %s ORDER BY creado_en", (org,)
        ).fetchall()
        assert pedidos[0][1] is None and pedidos[0][2] == 10  # viejo: sin datos personales, con el monto
        assert pedidos[1][1] == "Ana"  # nuevo: intacto
        assert c.execute("SELECT count(*) FROM notificaciones WHERE organizacion_id = %s", (org,)).fetchone()[0] == 1
        for tabla in ("notificaciones", "pedidos", "mensajes", "conversaciones"):
            c.execute(f"DELETE FROM {tabla} WHERE organizacion_id = %s", (org,))  # noqa: S608
        c.execute("DELETE FROM organizaciones WHERE id = %s", (org,))
