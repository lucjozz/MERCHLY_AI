"""Tests for ProveedorInvestigacionGemini.

Usa un cliente ``genai.Client`` mockeado — no llama a la API real de
Gemini (no hay acceso de red a Google desde este entorno, y no debemos
depender de una API externa para que los tests pasen). Verifican la
lógica del proveedor: construcción del mensaje, manejo de errores y
truncado de resultados.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.investigador_producto import (
    InvestigacionInput,
    NivelEstimado,
    ProductoCandidatoOutput,
)
from app.services.proveedores.base import ProveedorInvestigacionError
from app.services.proveedores.gemini import ProveedorInvestigacionGemini


def _producto_falso(numero: int) -> ProductoCandidatoOutput:
    return ProductoCandidatoOutput(
        nombre_producto=f"Producto {numero}",
        categoria="audifonos",
        nivel_demanda_estimado=NivelEstimado.ALTO,
        nivel_competencia_estimado=NivelEstimado.MEDIO,
        fuentes_evidencia=["https://ejemplo.test"],
        riesgos_identificados=[],
    )


def _cliente_falso(productos: list[ProductoCandidatoOutput]) -> MagicMock:
    respuesta = MagicMock()
    respuesta.parsed = productos

    cliente = MagicMock()
    cliente.aio.models.generate_content = AsyncMock(return_value=respuesta)
    return cliente


async def test_investigar_devuelve_productos_parseados() -> None:
    productos_esperados = [_producto_falso(1), _producto_falso(2)]
    cliente = _cliente_falso(productos_esperados)
    proveedor = ProveedorInvestigacionGemini(cliente=cliente, modelo="gemini-test")

    entrada = InvestigacionInput(
        categoria="audifonos", mercado_objetivo="BO", cantidad_resultados=2
    )
    resultado = await proveedor.investigar(entrada)

    assert resultado == productos_esperados
    cliente.aio.models.generate_content.assert_awaited_once()


async def test_investigar_trunca_a_cantidad_resultados() -> None:
    productos_de_sobra = [_producto_falso(i) for i in range(10)]
    cliente = _cliente_falso(productos_de_sobra)
    proveedor = ProveedorInvestigacionGemini(cliente=cliente, modelo="gemini-test")

    entrada = InvestigacionInput(
        categoria="audifonos", mercado_objetivo="BO", cantidad_resultados=3
    )
    resultado = await proveedor.investigar(entrada)

    assert len(resultado) == 3


async def test_investigar_convierte_fallo_de_red_en_error_del_dominio() -> None:
    cliente = MagicMock()
    cliente.aio.models.generate_content = AsyncMock(
        side_effect=RuntimeError("timeout de red")
    )
    proveedor = ProveedorInvestigacionGemini(cliente=cliente, modelo="gemini-test")

    entrada = InvestigacionInput(categoria="audifonos", mercado_objetivo="BO")

    with pytest.raises(ProveedorInvestigacionError):
        await proveedor.investigar(entrada)


async def test_investigar_falla_si_la_respuesta_no_cumple_el_schema() -> None:
    cliente = _cliente_falso(productos=None)
    proveedor = ProveedorInvestigacionGemini(cliente=cliente, modelo="gemini-test")

    entrada = InvestigacionInput(categoria="audifonos", mercado_objetivo="BO")

    with pytest.raises(ProveedorInvestigacionError):
        await proveedor.investigar(entrada)


def test_falla_al_construir_sin_api_key_ni_cliente(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.core import config

    config.get_settings.cache_clear()
    monkeypatch.setenv("GEMINI_API_KEY", "")

    with pytest.raises(ProveedorInvestigacionError):
        ProveedorInvestigacionGemini()

    config.get_settings.cache_clear()
