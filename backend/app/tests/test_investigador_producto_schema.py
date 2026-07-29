"""Tests for InvestigacionInput validations (contrato, sección 2)."""

import pytest
from pydantic import ValidationError

from app.schemas.investigador_producto import InvestigacionInput


def test_acepta_entrada_valida() -> None:
    entrada = InvestigacionInput(categoria="audifonos", mercado_objetivo="bo")
    assert entrada.mercado_objetivo == "BO"
    assert entrada.cantidad_resultados == 10


def test_rechaza_categoria_vacia() -> None:
    with pytest.raises(ValidationError):
        InvestigacionInput(categoria="", mercado_objetivo="BO")


def test_rechaza_categoria_prohibida() -> None:
    with pytest.raises(ValidationError):
        InvestigacionInput(categoria="armas", mercado_objetivo="BO")


def test_rechaza_mercado_objetivo_invalido() -> None:
    with pytest.raises(ValidationError):
        InvestigacionInput(categoria="audifonos", mercado_objetivo="Bolivia")


def test_trunca_cantidad_resultados_a_50() -> None:
    entrada = InvestigacionInput(
        categoria="audifonos", mercado_objetivo="BO", cantidad_resultados=999
    )
    assert entrada.cantidad_resultados == 50
