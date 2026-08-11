"""Tests para AnaliticaInput (contrato, sección 2)."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.analitica_basica import AgruparPor, AnaliticaInput


def test_acepta_entrada_vacia_con_defaults() -> None:
    entrada = AnaliticaInput()
    assert entrada.fecha_desde < entrada.fecha_hasta
    assert entrada.agrupar_por == AgruparPor.CATEGORIA
    assert entrada.categoria is None
    assert entrada.mercado_objetivo is None


def test_normaliza_mercado_objetivo_a_mayusculas() -> None:
    entrada = AnaliticaInput(mercado_objetivo="bo")
    assert entrada.mercado_objetivo == "BO"


def test_rechaza_mercado_objetivo_invalido() -> None:
    with pytest.raises(ValidationError):
        AnaliticaInput(mercado_objetivo="Bolivia")


def test_rechaza_fecha_desde_posterior_a_fecha_hasta() -> None:
    with pytest.raises(ValidationError):
        AnaliticaInput(
            fecha_desde=date.today(),
            fecha_hasta=date.today() - timedelta(days=1),
        )


def test_rechaza_rango_mayor_a_365_dias() -> None:
    with pytest.raises(ValidationError):
        AnaliticaInput(
            fecha_desde=date.today() - timedelta(days=400),
            fecha_hasta=date.today(),
        )


def test_rechaza_agrupar_por_invalido() -> None:
    with pytest.raises(ValidationError):
        AnaliticaInput(agrupar_por="precio")
