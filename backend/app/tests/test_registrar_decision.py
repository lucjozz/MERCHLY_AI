"""Tests para el servicio de orquestación de decisiones humanas.

Usa una sesión de base de datos mockeada, siguiendo el mismo patrón que
``test_agente_investigador_producto.py`` — no requiere PostgreSQL real.
"""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.decisiones import DecisionInput
from app.services.registrar_decision import registrar_decision


def _mock_resultado_decision_completa(decision_id: uuid.UUID, entrada: DecisionInput):
    """Simula lo que devolvería `_obtener_decision_orm_por_id` (el select
    con eager-load) para el ID de la decisión recién creada."""
    from app.models.decisiones import DecisionRecord

    decision = DecisionRecord(
        id=decision_id,
        decision_type=entrada.decision_type,
        entity_type=entrada.entity_type,
        entity_id=entrada.entity_id,
        action=entrada.action.value,
        user_id=entrada.user_id,
        reason=entrada.reason,
    )
    decision.creado_en = MagicMock()  # datetime real no importa para estos asserts
    decision.contexto = None
    decision.evidencias = []
    return decision


@pytest.fixture
def db_session_mock() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    return session


async def test_registrar_decision_aprobar_cambia_estado_a_en_catalogo(
    db_session_mock: AsyncMock,
) -> None:
    producto_id = uuid.uuid4()
    producto = SimpleNamespace(id=producto_id, estado="candidato")
    db_session_mock.get = AsyncMock(return_value=producto)

    entrada = DecisionInput(
        decision_type="product_selection",
        entity_type="product_candidate",
        entity_id=producto_id,
        action="approve",
        user_id="lucas",
        reason="Buen margen.",
    )

    resultado_select = MagicMock()
    resultado_select.scalar_one_or_none.return_value = _mock_resultado_decision_completa(
        uuid.uuid4(), entrada
    )
    db_session_mock.execute = AsyncMock(return_value=resultado_select)

    await registrar_decision(db_session=db_session_mock, entrada=entrada)

    assert producto.estado == "en_catalogo"
    db_session_mock.commit.assert_awaited_once()


async def test_registrar_decision_descartar_cambia_estado_a_descartado(
    db_session_mock: AsyncMock,
) -> None:
    producto_id = uuid.uuid4()
    producto = SimpleNamespace(id=producto_id, estado="candidato")
    db_session_mock.get = AsyncMock(return_value=producto)

    entrada = DecisionInput(
        decision_type="product_selection",
        entity_type="product_candidate",
        entity_id=producto_id,
        action="discard",
        user_id="lucas",
        reason="Margen insuficiente.",
    )

    resultado_select = MagicMock()
    resultado_select.scalar_one_or_none.return_value = _mock_resultado_decision_completa(
        uuid.uuid4(), entrada
    )
    db_session_mock.execute = AsyncMock(return_value=resultado_select)

    await registrar_decision(db_session=db_session_mock, entrada=entrada)

    assert producto.estado == "descartado"


async def test_registrar_decision_request_review_no_cambia_estado(
    db_session_mock: AsyncMock,
) -> None:
    producto_id = uuid.uuid4()
    producto = SimpleNamespace(id=producto_id, estado="candidato")
    db_session_mock.get = AsyncMock(return_value=producto)

    entrada = DecisionInput(
        decision_type="product_selection",
        entity_type="product_candidate",
        entity_id=producto_id,
        action="request_review",
        user_id="lucas",
        reason="Necesita más datos.",
    )

    resultado_select = MagicMock()
    resultado_select.scalar_one_or_none.return_value = _mock_resultado_decision_completa(
        uuid.uuid4(), entrada
    )
    db_session_mock.execute = AsyncMock(return_value=resultado_select)

    await registrar_decision(db_session=db_session_mock, entrada=entrada)

    assert producto.estado == "candidato"


async def test_registrar_decision_producto_inexistente_lanza_value_error(
    db_session_mock: AsyncMock,
) -> None:
    db_session_mock.get = AsyncMock(return_value=None)

    entrada = DecisionInput(
        decision_type="product_selection",
        entity_type="product_candidate",
        entity_id=uuid.uuid4(),
        action="approve",
        user_id="lucas",
        reason="N/A",
    )

    with pytest.raises(ValueError):
        await registrar_decision(db_session=db_session_mock, entrada=entrada)

    db_session_mock.add.assert_not_called()
    db_session_mock.commit.assert_not_awaited()


async def test_registrar_decision_entity_type_distinto_no_toca_productos(
    db_session_mock: AsyncMock,
) -> None:
    """Si entity_type no es 'product_candidate', no debe consultarse
    ni modificarse ningún producto."""
    db_session_mock.get = AsyncMock()

    entrada = DecisionInput(
        decision_type="campaign_selection",
        entity_type="marketing_campaign",
        entity_id=uuid.uuid4(),
        action="approve",
        user_id="lucas",
        reason="N/A",
    )

    resultado_select = MagicMock()
    resultado_select.scalar_one_or_none.return_value = _mock_resultado_decision_completa(
        uuid.uuid4(), entrada
    )
    db_session_mock.execute = AsyncMock(return_value=resultado_select)

    await registrar_decision(db_session=db_session_mock, entrada=entrada)

    db_session_mock.get.assert_not_called()
