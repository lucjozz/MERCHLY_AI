"""Tests for ProveedorInvestigacionSimulado."""

import pytest

from app.schemas.investigador_producto import InvestigacionInput
from app.services.proveedores.simulado import ProveedorInvestigacionSimulado


@pytest.mark.asyncio
async def test_devuelve_la_cantidad_solicitada() -> None:
    entrada = InvestigacionInput(
        categoria="audifonos", mercado_objetivo="BO", cantidad_resultados=5
    )
    proveedor = ProveedorInvestigacionSimulado()

    resultados = await proveedor.investigar(entrada)

    assert len(resultados) == 5
    assert all(r.categoria == "audifonos" for r in resultados)


@pytest.mark.asyncio
async def test_respeta_marcas_excluidas() -> None:
    entrada = InvestigacionInput(
        categoria="candidato 2",
        mercado_objetivo="BO",
        cantidad_resultados=5,
        excluir_marcas=["candidato 2"],
    )
    proveedor = ProveedorInvestigacionSimulado()

    resultados = await proveedor.investigar(entrada)

    assert all("candidato 2" not in r.nombre_producto.lower() for r in resultados)
