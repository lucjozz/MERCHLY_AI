"""Tests del servicio de decisiones humanas y su máquina de estados
(docs/013-Seguridad/04, sección 6.1). Sesión mockeada; el aislamiento real
entre organizaciones se prueba en test_integracion_seguridad_db.py."""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.decisiones import DecisionInput
from app.services.registrar_decision import (
    EntidadNoEncontradaError,
    TransicionInvalidaError,
    registrar_decision,
)
from app.tests.conftest import ORG_TEST


def _resultado(valor) -> MagicMock:
    r = MagicMock()
    r.scalar_one_or_none.return_value = valor
    return r


def _decision_completa(entrada: DecisionInput, user_id: uuid.UUID):
    from app.models.decisiones import DecisionRecord

    decision = DecisionRecord(
        id=uuid.uuid4(),
        organizacion_id=ORG_TEST,
        decision_type=entrada.decision_type,
        entity_type=entrada.entity_type,
        entity_id=entrada.entity_id,
        action=entrada.action.value,
        user_id=str(user_id),
        reason=entrada.reason,
    )
    decision.creado_en = MagicMock()
    decision.contexto = None
    decision.evidencias = []
    return decision


def _entrada(accion: str, entity_id: uuid.UUID, entity_type: str = "product_candidate") -> DecisionInput:
    return DecisionInput(
        decision_type="product_selection",
        entity_type=entity_type,
        entity_id=entity_id,
        action=accion,
        reason="Motivo de prueba.",
    )


def _sesion(producto, entrada, user_id) -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock(
        side_effect=[_resultado(producto), _resultado(_decision_completa(entrada, user_id))]
    )
    return session


@pytest.mark.parametrize(
    "estado_inicial, accion, estado_final",
    [
        ("candidato", "approve", "en_catalogo"),
        ("candidato", "discard", "descartado"),
        ("candidato", "request_review", "en_revision"),
        ("en_revision", "approve", "en_catalogo"),
        ("en_revision", "discard", "descartado"),
    ],
)
async def test_transiciones_validas(estado_inicial, accion, estado_final) -> None:
    producto = SimpleNamespace(id=uuid.uuid4(), estado=estado_inicial)
    user_id = uuid.uuid4()
    entrada = _entrada(accion, producto.id)
    session = _sesion(producto, entrada, user_id)

    salida = await registrar_decision(session, entrada, user_id, ORG_TEST)

    assert producto.estado == estado_final
    assert salida.estado_resultante == estado_final
    session.commit.assert_awaited_once()
    # La decisión se guarda en la organización del usuario, no en otra.
    decision_guardada = session.add.call_args_list[0].args[0]
    assert decision_guardada.organizacion_id == ORG_TEST
    assert decision_guardada.user_id == str(user_id)


@pytest.mark.parametrize(
    "estado_inicial, accion",
    [
        ("en_catalogo", "approve"),
        ("en_catalogo", "discard"),
        ("en_catalogo", "request_review"),
        ("descartado", "approve"),
        ("descartado", "discard"),
        ("descartado", "request_review"),
        ("en_revision", "request_review"),
    ],
)
async def test_transiciones_invalidas_no_registran_nada(estado_inicial, accion) -> None:
    producto = SimpleNamespace(id=uuid.uuid4(), estado=estado_inicial)
    entrada = _entrada(accion, producto.id)
    session = _sesion(producto, entrada, uuid.uuid4())

    with pytest.raises(TransicionInvalidaError):
        await registrar_decision(session, entrada, uuid.uuid4(), ORG_TEST)

    assert producto.estado == estado_inicial
    session.add.assert_not_called()
    session.commit.assert_not_awaited()


async def test_producto_inexistente_o_de_otra_organizacion() -> None:
    entrada = _entrada("approve", uuid.uuid4())
    session = _sesion(None, entrada, uuid.uuid4())

    with pytest.raises(EntidadNoEncontradaError):
        await registrar_decision(session, entrada, uuid.uuid4(), ORG_TEST)
    session.add.assert_not_called()


async def test_entity_type_distinto_no_toca_productos() -> None:
    user_id = uuid.uuid4()
    entrada = _entrada("approve", uuid.uuid4(), entity_type="campaign")
    session = AsyncMock()
    session.add = MagicMock()
    session.execute = AsyncMock(return_value=_resultado(_decision_completa(entrada, user_id)))

    salida = await registrar_decision(session, entrada, user_id, ORG_TEST)

    assert salida.estado_resultante is None
    session.commit.assert_awaited_once()
