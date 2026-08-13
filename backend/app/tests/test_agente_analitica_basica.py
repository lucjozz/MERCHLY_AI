"""Tests para AgenteAnaliticaBasica (orquestación).

Usa una sesión de base de datos mockeada — no requiere PostgreSQL real.
Las "filas" se simulan con SimpleNamespace, exponiendo solo los atributos
que el servicio realmente lee.
"""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.analitica_basica import AgruparPor, AnaliticaInput
from app.services.agente_analitica_basica import AgenteAnaliticaBasica, AnaliticaBasicaError


def _fila(categoria: str, estado: str, investigacion_id: uuid.UUID) -> SimpleNamespace:
    return SimpleNamespace(
        categoria=categoria,
        estado=estado,
        nivel_demanda_estimado="alto",
        nivel_competencia_estimado="medio",
        investigacion_id=investigacion_id,
    )


def _db_session_con_filas(filas: list) -> AsyncMock:
    session = AsyncMock()
    resultado = MagicMock()
    resultado.scalars.return_value.all.return_value = filas
    session.execute = AsyncMock(return_value=resultado)
    return session


async def test_reporte_vacio_no_es_un_error() -> None:
    session = _db_session_con_filas([])
    agente = AgenteAnaliticaBasica(db_session=session)

    reporte = await agente.ejecutar(AnaliticaInput())

    assert reporte.resumen_catalogo.total_productos_candidatos == 0
    assert reporte.resumen_catalogo.grupos == []
    assert reporte.tasa_conversion_catalogo.tasa_candidato_a_en_catalogo == 0.0


async def test_agrupa_correctamente_por_categoria() -> None:
    inv1, inv2 = uuid.uuid4(), uuid.uuid4()
    filas = [
        _fila("audifonos", "candidato", inv1),
        _fila("audifonos", "candidato", inv1),
        _fila("mochilas", "en_catalogo", inv2),
    ]
    session = _db_session_con_filas(filas)
    agente = AgenteAnaliticaBasica(db_session=session)

    reporte = await agente.ejecutar(AnaliticaInput(agrupar_por=AgruparPor.CATEGORIA))

    assert reporte.resumen_catalogo.total_productos_candidatos == 3
    grupos = {g.clave: g.cantidad for g in reporte.resumen_catalogo.grupos}
    assert grupos == {"audifonos": 2, "mochilas": 1}


async def test_calcula_tasa_de_conversion() -> None:
    inv = uuid.uuid4()
    filas = [
        _fila("audifonos", "candidato", inv),
        _fila("audifonos", "en_catalogo", inv),
        _fila("audifonos", "en_catalogo", inv),
        _fila("audifonos", "descartado", inv),
    ]
    session = _db_session_con_filas(filas)
    agente = AgenteAnaliticaBasica(db_session=session)

    reporte = await agente.ejecutar(AnaliticaInput())

    tasa = reporte.tasa_conversion_catalogo
    assert tasa.candidato == 1
    assert tasa.en_catalogo == 2
    assert tasa.descartado == 1
    assert tasa.tasa_candidato_a_en_catalogo == 0.5


async def test_resume_actividad_del_investigador() -> None:
    inv1, inv2 = uuid.uuid4(), uuid.uuid4()
    filas = [
        _fila("audifonos", "candidato", inv1),
        _fila("audifonos", "candidato", inv1),
        _fila("mochilas", "candidato", inv2),
    ]
    session = _db_session_con_filas(filas)
    agente = AgenteAnaliticaBasica(db_session=session)

    reporte = await agente.ejecutar(AnaliticaInput())

    actividad = reporte.actividad_agente_investigador
    assert actividad.total_investigaciones == 2
    assert actividad.promedio_productos_por_investigacion == 1.5
    assert "audifonos" in actividad.categorias_mas_investigadas


async def test_no_escribe_nada_en_la_sesion() -> None:
    """El agente es de solo lectura (contrato, sección 4): nunca debe
    llamarse add/commit/delete sobre la sesión."""
    session = _db_session_con_filas([])
    agente = AgenteAnaliticaBasica(db_session=session)

    await agente.ejecutar(AnaliticaInput())

    session.add.assert_not_called()
    session.commit.assert_not_called()
    session.delete.assert_not_called()


async def test_falla_tras_agotar_el_reintento(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock()
    session.execute.side_effect = RuntimeError("timeout de conexión")
    agente = AgenteAnaliticaBasica(db_session=session)

    with pytest.raises(AnaliticaBasicaError):
        await agente.ejecutar(AnaliticaInput())

    # Contrato, sección 8: "máximo 1 reintento" -> 2 llamadas totales
    # (intento original + 1 reintento).
    assert session.execute.call_count == 2
