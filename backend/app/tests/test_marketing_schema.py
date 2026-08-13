"""Tests para MarketingInput (contrato, sección 2)."""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.marketing import CanalMarketing, MarketingInput, TonoMarketing


def _ids(n: int) -> list[uuid.UUID]:
    return [uuid.uuid4() for _ in range(n)]


def test_acepta_entrada_valida() -> None:
    entrada = MarketingInput(
        productos_candidato_ids=_ids(1),
        canales_objetivo=[CanalMarketing.EMAIL],
        idioma_destino="ES",
    )
    assert entrada.idioma_destino == "es"
    assert entrada.tono == TonoMarketing.NEUTRAL


def test_rechaza_lista_vacia_de_productos() -> None:
    with pytest.raises(ValidationError):
        MarketingInput(
            productos_candidato_ids=[],
            canales_objetivo=[CanalMarketing.EMAIL],
            idioma_destino="es",
        )


def test_rechaza_mas_de_10_productos() -> None:
    with pytest.raises(ValidationError):
        MarketingInput(
            productos_candidato_ids=_ids(11),
            canales_objetivo=[CanalMarketing.EMAIL],
            idioma_destino="es",
        )


def test_rechaza_canales_vacios() -> None:
    with pytest.raises(ValidationError):
        MarketingInput(
            productos_candidato_ids=_ids(1), canales_objetivo=[], idioma_destino="es"
        )


def test_rechaza_canales_duplicados() -> None:
    with pytest.raises(ValidationError):
        MarketingInput(
            productos_candidato_ids=_ids(1),
            canales_objetivo=[CanalMarketing.EMAIL, CanalMarketing.EMAIL],
            idioma_destino="es",
        )


def test_rechaza_idioma_invalido() -> None:
    with pytest.raises(ValidationError):
        MarketingInput(
            productos_candidato_ids=_ids(1),
            canales_objetivo=[CanalMarketing.EMAIL],
            idioma_destino="espanol",
        )


def test_rechaza_presupuesto_no_positivo() -> None:
    with pytest.raises(ValidationError):
        MarketingInput(
            productos_candidato_ids=_ids(1),
            canales_objetivo=[CanalMarketing.EMAIL],
            idioma_destino="es",
            presupuesto_mensual_referencia=0,
        )
