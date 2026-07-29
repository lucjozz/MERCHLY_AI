"""Tests for AgenteInvestigadorProducto (orquestación).

Usa un proveedor falso y una sesión de base de datos mockeada — no
requiere PostgreSQL real. Verifica el comportamiento descrito en el
contrato técnico del agente, no la infraestructura.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.investigador_producto import (
    InvestigacionInput,
    NivelEstimado,
    ProductoCandidatoOutput,
)
from app.services.agente_investigador_producto import AgenteInvestigadorProducto
from app.services.proveedores.base import ProveedorInvestigacion, ProveedorInvestigacionError


class _ProveedorFalsoExitoso(ProveedorInvestigacion):
    """Devuelve un resultado fijo, sin fallar nunca."""

    async def investigar(self, entrada):
        return [
            ProductoCandidatoOutput(
                nombre_producto="Producto de prueba",
                categoria=entrada.categoria,
                nivel_demanda_estimado=NivelEstimado.ALTO,
                nivel_competencia_estimado=NivelEstimado.BAJO,
                fuentes_evidencia=["https://ejemplo.test"],
                riesgos_identificados=[],
            )
            for _ in range(entrada.cantidad_resultados)
        ]


class _ProveedorFalsoQueSiempreFalla(ProveedorInvestigacion):
    """Levanta ProveedorInvestigacionError en cada intento."""

    def __init__(self) -> None:
        self.llamadas = 0

    async def investigar(self, entrada):
        self.llamadas += 1
        raise ProveedorInvestigacionError("fallo simulado")


@pytest.fixture
def db_session_mock() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    return session


async def test_ejecutar_persiste_y_devuelve_productos(db_session_mock: AsyncMock) -> None:
    entrada = InvestigacionInput(
        categoria="audifonos", mercado_objetivo="BO", cantidad_resultados=3
    )
    agente = AgenteInvestigadorProducto(
        proveedor=_ProveedorFalsoExitoso(), db_session=db_session_mock
    )

    resultado = await agente.ejecutar(entrada)

    assert len(resultado.productos) == 3
    assert resultado.metadata.confianza == "normal"
    assert resultado.metadata.total_productos_devueltos == 3
    # 3 productos -> 3 llamadas a add(), y un solo commit al final.
    assert db_session_mock.add.call_count == 3
    db_session_mock.commit.assert_awaited_once()


async def test_ejecutar_agrupa_productos_bajo_el_mismo_investigacion_id(
    db_session_mock: AsyncMock,
) -> None:
    entrada = InvestigacionInput(
        categoria="audifonos", mercado_objetivo="BO", cantidad_resultados=2
    )
    agente = AgenteInvestigadorProducto(
        proveedor=_ProveedorFalsoExitoso(), db_session=db_session_mock
    )

    resultado = await agente.ejecutar(entrada)

    filas_persistidas = [llamada.args[0] for llamada in db_session_mock.add.call_args_list]
    investigacion_ids = {fila.investigacion_id for fila in filas_persistidas}

    assert len(investigacion_ids) == 1
    assert investigacion_ids.pop() == resultado.metadata.investigacion_id


async def test_ejecutar_no_persiste_si_el_proveedor_falla(db_session_mock: AsyncMock) -> None:
    proveedor = _ProveedorFalsoQueSiempreFalla()
    agente = AgenteInvestigadorProducto(proveedor=proveedor, db_session=db_session_mock)
    entrada = InvestigacionInput(categoria="audifonos", mercado_objetivo="BO")

    resultado = await agente.ejecutar(entrada)

    assert resultado.productos == []
    assert resultado.metadata.confianza == "baja"
    db_session_mock.add.assert_not_called()
    db_session_mock.commit.assert_not_awaited()


async def test_ejecutar_reintenta_hasta_el_maximo_definido_en_el_contrato(
    db_session_mock: AsyncMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Evita esperar los 5 segundos reales entre reintentos durante el test.
    monkeypatch.setattr("asyncio.sleep", AsyncMock())

    proveedor = _ProveedorFalsoQueSiempreFalla()
    agente = AgenteInvestigadorProducto(proveedor=proveedor, db_session=db_session_mock)
    entrada = InvestigacionInput(categoria="audifonos", mercado_objetivo="BO")

    await agente.ejecutar(entrada)

    # Contrato, sección 8: "máximo 2 reintentos" -> 3 llamadas totales
    # (intento original + 2 reintentos).
    assert proveedor.llamadas == 3
