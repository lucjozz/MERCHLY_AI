"""Integración contra PostgreSQL REAL: aislamiento multi-tenant (RLS), IDOR,
privilegios mínimos del rol de la app y concurrencia de decisiones.

docs/013-Seguridad/04, secciones 2 y 6. Requiere el Postgres del compose
corriendo (127.0.0.1:5432) y ya migrado. Toma las contraseñas del .env de
la raíz del repo (o de TEST_DATABASE_ADMIN_URL / TEST_DATABASE_APP_URL).
Si no hay base disponible, se saltea (los tests unitarios no la necesitan).

Correr desde backend/:  pytest app/tests/test_integracion_seguridad_db.py -v
"""

import asyncio
import os
import uuid
from pathlib import Path

import pytest

psycopg = pytest.importorskip("psycopg")

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402

from app.core.database import fijar_organizacion  # noqa: E402
from app.schemas.decisiones import DecisionInput  # noqa: E402
from app.services.consulta_productos_candidatos import (  # noqa: E402
    eliminar_producto_candidato,
    listar_productos_candidatos,
    obtener_producto_candidato_por_id,
)
from app.services.registrar_decision import (  # noqa: E402
    EntidadNoEncontradaError,
    TransicionInvalidaError,
    obtener_decision_por_id,
    registrar_decision,
)


def _urls() -> tuple[str, str] | None:
    admin = os.environ.get("TEST_DATABASE_ADMIN_URL")
    app_url = os.environ.get("TEST_DATABASE_APP_URL")
    if admin and app_url:
        return admin, app_url
    env = Path(__file__).resolve().parents[3] / ".env"
    if not env.exists():
        return None
    valores = dict(
        linea.split("=", 1) for linea in env.read_text(encoding="utf-8").splitlines()
        if "=" in linea and not linea.lstrip().startswith("#")
    )
    if not valores.get("POSTGRES_PASSWORD") or not valores.get("DB_APP_PASSWORD"):
        return None
    return (
        f"postgresql://merchly:{valores['POSTGRES_PASSWORD']}@127.0.0.1:5432/merchly",
        f"postgresql://merchly_app:{valores['DB_APP_PASSWORD']}@127.0.0.1:5432/merchly",
    )


URLS = _urls()


def _disponible() -> bool:
    if URLS is None:
        return False
    try:
        with psycopg.connect(URLS[1], connect_timeout=2):
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _disponible(), reason="Postgres de integración no disponible")


@pytest.fixture(scope="module")
def datos():
    """Crea 2 organizaciones con 1 producto y 1 decisión cada una (como dueño)."""
    org_a, org_b = uuid.uuid4(), uuid.uuid4()
    prod = {org_a: uuid.uuid4(), org_b: uuid.uuid4()}
    prod_concurrencia = uuid.uuid4()
    dec = {org_a: uuid.uuid4(), org_b: uuid.uuid4()}
    with psycopg.connect(URLS[0], autocommit=True) as c:
        for org, nombre in ((org_a, "TEST-RLS Org A"), (org_b, "TEST-RLS Org B")):
            c.execute("INSERT INTO organizaciones (id, nombre) VALUES (%s, %s)", (org, nombre))
            c.execute(
                "INSERT INTO productos_candidatos (id, organizacion_id, nombre_producto, categoria,"
                " mercado_objetivo, nivel_demanda_estimado, nivel_competencia_estimado,"
                " fuentes_evidencia, riesgos_identificados, estado, investigacion_id)"
                " VALUES (%s, %s, %s, 'test-rls', 'BO', 'alto', 'bajo', '[]', '[]', 'candidato', %s)",
                (prod[org], org, f"Producto de {nombre}", uuid.uuid4()),
            )
            c.execute(
                "INSERT INTO decision_records (id, organizacion_id, decision_type, entity_type,"
                " entity_id, action, user_id, reason) VALUES (%s, %s, 'test', 'test', %s,"
                " 'request_review', 'test', 'test')",
                (dec[org], org, prod[org]),
            )
        c.execute(
            "INSERT INTO productos_candidatos (id, organizacion_id, nombre_producto, categoria,"
            " mercado_objetivo, nivel_demanda_estimado, nivel_competencia_estimado,"
            " fuentes_evidencia, riesgos_identificados, estado, investigacion_id)"
            " VALUES (%s, %s, 'Concurrencia', 'test-rls', 'BO', 'alto', 'bajo', '[]', '[]',"
            " 'candidato', %s)",
            (prod_concurrencia, org_a, uuid.uuid4()),
        )
    yield {"a": org_a, "b": org_b, "prod": prod, "dec": dec, "prod_conc": prod_concurrencia}
    with psycopg.connect(URLS[0], autocommit=True) as c:
        orgs = (org_a, org_b)
        for tabla in ("decision_evidence", "decision_context", "decision_outcomes", "decision_records", "productos_candidatos"):
            c.execute(f"DELETE FROM {tabla} WHERE organizacion_id = ANY(%s)", (list(orgs),))
        c.execute("DELETE FROM organizaciones WHERE id = ANY(%s)", (list(orgs),))


def _app_conn():
    return psycopg.connect(URLS[1])


def _fijar(cur, org):
    cur.execute("SELECT set_config('app.organizacion_id', %s, true)", (str(org),))


# ------------------------------------------------------------ RLS en crudo


def test_rol_app_no_es_superusuario_ni_saltea_rls() -> None:
    with _app_conn() as c:
        fila = c.execute(
            "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user"
        ).fetchone()
        assert fila == (False, False)


def test_sin_organizacion_fijada_no_se_ve_nada(datos) -> None:
    with _app_conn() as c:
        assert c.execute("SELECT count(*) FROM productos_candidatos").fetchone()[0] == 0
        assert c.execute("SELECT count(*) FROM decision_records").fetchone()[0] == 0


def test_cada_org_ve_solo_lo_suyo_aun_sin_filtro_en_la_consulta(datos) -> None:
    for propia, ajena in (("a", "b"), ("b", "a")):
        with _app_conn() as c, c.cursor() as cur:
            _fijar(cur, datos[propia])
            cur.execute("SELECT DISTINCT organizacion_id FROM productos_candidatos")
            assert {r[0] for r in cur.fetchall()} == {datos[propia]}
            cur.execute(
                "SELECT count(*) FROM productos_candidatos WHERE id = %s",
                (datos["prod"][datos[ajena]],),
            )
            assert cur.fetchone()[0] == 0
            cur.execute("SELECT count(*) FROM decision_records WHERE id = %s", (datos["dec"][datos[ajena]],))
            assert cur.fetchone()[0] == 0


def test_org_a_no_puede_modificar_datos_de_b(datos) -> None:
    with _app_conn() as c, c.cursor() as cur:
        _fijar(cur, datos["a"])
        cur.execute(
            "UPDATE productos_candidatos SET estado = 'descartado' WHERE id = %s",
            (datos["prod"][datos["b"]],),
        )
        assert cur.rowcount == 0


def test_org_a_no_puede_insertar_filas_a_nombre_de_b(datos) -> None:
    with _app_conn() as c, c.cursor() as cur:
        _fijar(cur, datos["a"])
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute(
                "INSERT INTO decision_records (id, organizacion_id, decision_type, entity_type,"
                " entity_id, action, user_id, reason) VALUES (%s, %s, 'x','x', %s, 'approve','x','x')",
                (uuid.uuid4(), datos["b"], uuid.uuid4()),
            )


def test_org_a_no_puede_mover_su_fila_a_b(datos) -> None:
    with _app_conn() as c, c.cursor() as cur:
        _fijar(cur, datos["a"])
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute(
                "UPDATE productos_candidatos SET organizacion_id = %s WHERE id = %s",
                (datos["b"], datos["prod"][datos["a"]]),
            )


def test_la_organizacion_no_se_filtra_entre_transacciones(datos) -> None:
    """set_config(..., true) = SET LOCAL: al terminar la transacción se pierde.
    Así una conexión reusada del pool no hereda la organización anterior."""
    with _app_conn() as c:
        with c.cursor() as cur:
            _fijar(cur, datos["a"])
            cur.execute("SELECT count(*) FROM productos_candidatos")
            assert cur.fetchone()[0] >= 1
        c.commit()
        assert c.execute("SELECT count(*) FROM productos_candidatos").fetchone()[0] == 0


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM productos_candidatos",
        "DELETE FROM decision_records",
        "UPDATE decision_records SET reason = 'editado'",
        "DELETE FROM usuarios",
        "TRUNCATE productos_candidatos",
        "ALTER TABLE productos_candidatos DISABLE ROW LEVEL SECURITY",
        "DROP POLICY aislamiento_organizacion ON productos_candidatos",
        "CREATE TABLE intrusa (id int)",
        "SET row_security = off; SELECT count(*) FROM productos_candidatos",
    ],
)
def test_rol_app_tiene_privilegios_minimos(datos, sql: str) -> None:
    """Decisiones append-only, sin DELETE, sin DDL, sin desactivar RLS."""
    with _app_conn() as c, c.cursor() as cur:
        _fijar(cur, datos["a"])
        with pytest.raises(psycopg.Error):
            cur.execute(sql)
            if cur.description:  # SET row_security=off no da error: no debe saltear RLS
                assert cur.fetchone()[0] <= 2
                raise psycopg.Error("row_security=off no saltea RLS (ok)")


# ------------------------------------------------------------ servicios reales (IDOR)


@pytest.fixture
async def sesion_app():
    engine = create_async_engine(URLS[1].replace("postgresql://", "postgresql+psycopg://"))
    fabrica = async_sessionmaker(engine, expire_on_commit=False)
    yield fabrica
    await engine.dispose()


async def test_servicios_listan_solo_la_org_del_usuario(datos, sesion_app) -> None:
    async with sesion_app() as s:
        await fijar_organizacion(s, datos["a"])
        productos, total = await listar_productos_candidatos(s, datos["a"], categoria="test-rls")
        assert total == len(productos) >= 1
        assert {p.organizacion_id for p in productos} == {datos["a"]}


async def test_idor_leer_producto_de_otra_org_da_none(datos, sesion_app) -> None:
    async with sesion_app() as s:
        await fijar_organizacion(s, datos["a"])
        assert await obtener_producto_candidato_por_id(s, datos["a"], datos["prod"][datos["b"]]) is None
        # Incluso si el código pasara la org equivocada, RLS lo frena:
        assert await obtener_producto_candidato_por_id(s, datos["b"], datos["prod"][datos["b"]]) is None


async def test_idor_leer_decision_de_otra_org_da_none(datos, sesion_app) -> None:
    async with sesion_app() as s:
        await fijar_organizacion(s, datos["a"])
        assert await obtener_decision_por_id(s, datos["a"], datos["dec"][datos["b"]]) is None
        assert await obtener_decision_por_id(s, datos["a"], datos["dec"][datos["a"]]) is not None


async def test_idor_borrar_producto_de_otra_org_no_borra(datos, sesion_app) -> None:
    async with sesion_app() as s:
        await fijar_organizacion(s, datos["a"])
        assert await eliminar_producto_candidato(s, datos["a"], datos["prod"][datos["b"]]) is False
    with psycopg.connect(URLS[0]) as c:
        fila = c.execute(
            "SELECT eliminado_en FROM productos_candidatos WHERE id = %s", (datos["prod"][datos["b"]],)
        ).fetchone()
        assert fila == (None,)


async def test_idor_decidir_sobre_producto_de_otra_org_da_404(datos, sesion_app) -> None:
    entrada = DecisionInput(
        decision_type="product_selection",
        entity_type="product_candidate",
        entity_id=datos["prod"][datos["b"]],
        action="approve",
        reason="intento cruzado",
    )
    async with sesion_app() as s:
        await fijar_organizacion(s, datos["a"])
        with pytest.raises(EntidadNoEncontradaError):
            await registrar_decision(s, entrada, uuid.uuid4(), datos["a"])


async def test_decision_y_estado_final_inmutable_con_rls_real(datos, sesion_app) -> None:
    producto = datos["prod"][datos["a"]]

    def _entrada(accion: str) -> DecisionInput:
        return DecisionInput(
            decision_type="product_selection", entity_type="product_candidate",
            entity_id=producto, action=accion, reason="test",
        )

    async with sesion_app() as s:
        await fijar_organizacion(s, datos["a"])
        salida = await registrar_decision(s, _entrada("approve"), uuid.uuid4(), datos["a"])
        assert salida.estado_resultante == "en_catalogo"
    async with sesion_app() as s:
        await fijar_organizacion(s, datos["a"])
        with pytest.raises(TransicionInvalidaError):
            await registrar_decision(s, _entrada("discard"), uuid.uuid4(), datos["a"])


async def test_decisiones_simultaneas_solo_una_gana(datos, sesion_app) -> None:
    """Doble clic / dos pestañas: FOR UPDATE serializa y la segunda da 409."""
    entrada_aprobar = DecisionInput(
        decision_type="product_selection", entity_type="product_candidate",
        entity_id=datos["prod_conc"], action="approve", reason="pestaña 1",
    )
    entrada_descartar = DecisionInput(
        **{**entrada_aprobar.model_dump(), "action": "discard", "reason": "pestaña 2"}
    )

    async def _decidir(entrada):
        async with sesion_app() as s:
            await fijar_organizacion(s, datos["a"])
            try:
                return await registrar_decision(s, entrada, uuid.uuid4(), datos["a"])
            except TransicionInvalidaError as error:
                return error

    resultados = await asyncio.gather(_decidir(entrada_aprobar), _decidir(entrada_descartar))
    exitos = [r for r in resultados if not isinstance(r, Exception)]
    conflictos = [r for r in resultados if isinstance(r, TransicionInvalidaError)]
    assert len(exitos) == 1 and len(conflictos) == 1
    with psycopg.connect(URLS[0]) as c:
        n = c.execute(
            "SELECT count(*) FROM decision_records WHERE entity_id = %s", (datos["prod_conc"],)
        ).fetchone()[0]
        assert n == 1


# ------------------------------------------------------------ refresh tokens


@pytest.fixture
def usuario_a(datos):
    usuario_id = uuid.uuid4()
    with psycopg.connect(URLS[0], autocommit=True) as c:
        c.execute(
            "INSERT INTO usuarios (id, organizacion_id, email, password_hash, nombre, rol)"
            " VALUES (%s, %s, %s, 'x', 'Test RLS', 'admin_principal')",
            (usuario_id, datos["a"], f"test-rls-{usuario_id.hex[:8]}@merchly.test"),
        )
    yield usuario_id
    with psycopg.connect(URLS[0], autocommit=True) as c:
        c.execute("DELETE FROM refresh_tokens WHERE usuario_id = %s", (usuario_id,))
        c.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))


async def _sesion_inicial(fabrica, usuario_id):
    from app.models.usuario import Usuario
    from app.services.autenticacion import emitir_sesion

    async with fabrica() as s:
        usuario = await s.get(Usuario, usuario_id)
        return await emitir_sesion(s, usuario)


async def test_refresh_rota_y_el_nuevo_funciona(usuario_a, sesion_app) -> None:
    from app.services.autenticacion import rotar_refresh

    inicial = await _sesion_inicial(sesion_app, usuario_a)
    async with sesion_app() as s:
        nueva = await rotar_refresh(s, inicial.refresh_token)
    assert nueva.refresh_token != inicial.refresh_token
    async with sesion_app() as s:
        assert (await rotar_refresh(s, nueva.refresh_token)).access_token


async def test_refresh_paralelo_dentro_de_la_gracia_no_cierra_sesion(usuario_a, sesion_app) -> None:
    from app.services.autenticacion import rotar_refresh

    inicial = await _sesion_inicial(sesion_app, usuario_a)
    async with sesion_app() as s:
        await rotar_refresh(s, inicial.refresh_token)
    async with sesion_app() as s:  # segundo request con el mismo token, al instante
        assert (await rotar_refresh(s, inicial.refresh_token)).access_token


async def test_refresh_reusado_fuera_de_la_gracia_revoca_toda_la_familia(usuario_a, sesion_app) -> None:
    from app.core.security import hashear_refresh_token
    from app.services.autenticacion import RefreshInvalidoError, rotar_refresh

    inicial = await _sesion_inicial(sesion_app, usuario_a)
    async with sesion_app() as s:
        nueva = await rotar_refresh(s, inicial.refresh_token)
    with psycopg.connect(URLS[0], autocommit=True) as c:  # simula que pasó 1 minuto
        c.execute(
            "UPDATE refresh_tokens SET rotado_en = now() - interval '60 seconds' WHERE token_hash = %s",
            (hashear_refresh_token(inicial.refresh_token),),
        )
    async with sesion_app() as s:  # el "ladrón" usa el token viejo
        with pytest.raises(RefreshInvalidoError):
            await rotar_refresh(s, inicial.refresh_token)
    async with sesion_app() as s:  # y el legítimo también queda afuera
        with pytest.raises(RefreshInvalidoError):
            await rotar_refresh(s, nueva.refresh_token)


async def test_logout_revoca_el_refresh(usuario_a, sesion_app) -> None:
    from app.services.autenticacion import RefreshInvalidoError, revocar_refresh, rotar_refresh

    inicial = await _sesion_inicial(sesion_app, usuario_a)
    async with sesion_app() as s:
        await revocar_refresh(s, inicial.refresh_token, usuario_a)
    async with sesion_app() as s:
        with pytest.raises(RefreshInvalidoError):
            await rotar_refresh(s, inicial.refresh_token)


# ------------------------------------------------------------ login con Google


async def test_google_auto_registro_crea_organizacion_y_admin(sesion_app) -> None:
    from app.services.autenticacion import usuario_desde_google

    sub = f"google-test-{uuid.uuid4().hex}"
    email = f"Nuevo.{uuid.uuid4().hex[:6]}@Gmail.com"
    try:
        async with sesion_app() as s:
            nuevo = await usuario_desde_google(s, sub, email, "Ana Pérez")
        assert nuevo is not None and nuevo.rol == "admin_principal"
        assert nuevo.email == email.lower() and nuevo.password_hash is None
        async with sesion_app() as s:  # segundo login: mismo usuario, sin duplicar
            otra_vez = await usuario_desde_google(s, sub, email, "Ana Pérez")
        assert otra_vez.id == nuevo.id and otra_vez.organizacion_id == nuevo.organizacion_id
        with psycopg.connect(URLS[0]) as c:
            nombre = c.execute(
                "SELECT nombre FROM organizaciones WHERE id = %s", (nuevo.organizacion_id,)
            ).fetchone()[0]
        assert nombre == "Negocio de Ana Pérez"
    finally:
        with psycopg.connect(URLS[0], autocommit=True) as c:
            fila = c.execute("SELECT id, organizacion_id FROM usuarios WHERE google_sub = %s", (sub,)).fetchone()
            if fila:
                c.execute("DELETE FROM usuarios WHERE id = %s", (fila[0],))
                c.execute("DELETE FROM organizaciones WHERE id = %s", (fila[1],))


async def test_google_no_secuestra_email_vinculado_a_otra_cuenta(usuario_a, sesion_app) -> None:
    """Un email ya vinculado a OTRA cuenta de Google no se puede tomar con otro sub."""
    from app.services.autenticacion import usuario_desde_google

    with psycopg.connect(URLS[0], autocommit=True) as c:
        email = c.execute(
            "UPDATE usuarios SET google_sub = %s WHERE id = %s RETURNING email",
            (f"sub-original-{uuid.uuid4().hex}", usuario_a),
        ).fetchone()[0]
    async with sesion_app() as s:
        assert await usuario_desde_google(s, f"sub-atacante-{uuid.uuid4().hex}", email, "X") is None
