"""Tests para AgenteMarketing (orquestación).

Usa una sesión de base de datos mockeada y proveedores falsos — no
requiere PostgreSQL real ni un proveedor de IA real.
"""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.marketing import CanalMarketing, MarketingInput
from app.services.agente_marketing import AgenteMarketing, ProductosInvalidosError
from app.services.proveedores.marketing_base import (
    ProveedorMarketing,
    ProveedorMarketingError,
    ResultadoProveedorMarketing,
)


def _producto(estado: str = "en_catalogo", fuentes_evidencia=None):
    return SimpleNamespace(
        id=uuid.uuid4(),
        nombre_producto="Producto de prueba",
        estado=estado,
        fuentes_evidencia=fuentes_evidencia or ["https://ejemplo.test"],
    )


def _db_session_con_productos(productos: list) -> AsyncMock:
    session = AsyncMock()
    resultado = MagicMock()
    resultado.scalars.return_value.all.return_value = productos
    session.execute = AsyncMock(return_value=resultado)
    return session


class _ProveedorFalsoExitoso(ProveedorMarketing):
    async def generar_campana(self, entrada, productos):
        return ResultadoProveedorMarketing(
            angulos_de_campana=["Ángulo de prueba"],
            copy_por_canal={
                canal: [] for canal in entrada.canales_objetivo
            },
            publico_objetivo_sugerido="Público de prueba",
            advertencias=[],
        )


class _ProveedorFalsoQueSiempreFalla(ProveedorMarketing):
    def __init__(self) -> None:
        self.llamadas = 0

    async def generar_campana(self, entrada, productos):
        self.llamadas += 1
        raise ProveedorMarketingError("fallo simulado")


async def test_ejecutar_genera_campana_para_producto_en_catalogo() -> None:
    producto = _producto(estado="en_catalogo")
    session = _db_session_con_productos([producto])
    agente = AgenteMarketing(proveedor=_ProveedorFalsoExitoso(), db_session=session)
    entrada = MarketingInput(
        productos_candidato_ids=[producto.id],
        canales_objetivo=[CanalMarketing.EMAIL],
        idioma_destino="es",
    )

    resultado = await agente.ejecutar(entrada)

    assert resultado.angulos_de_campana == ["Ángulo de prueba"]
    assert resultado.publico_objetivo_sugerido == "Público de prueba"


async def test_ejecutar_rechaza_producto_inexistente() -> None:
    session = _db_session_con_productos([])
    agente = AgenteMarketing(proveedor=_ProveedorFalsoExitoso(), db_session=session)
    entrada = MarketingInput(
        productos_candidato_ids=[uuid.uuid4()],
        canales_objetivo=[CanalMarketing.EMAIL],
        idioma_destino="es",
    )

    with pytest.raises(ProductosInvalidosError):
        await agente.ejecutar(entrada)


async def test_ejecutar_rechaza_producto_que_no_esta_en_catalogo() -> None:
    producto = _producto(estado="candidato")
    session = _db_session_con_productos([producto])
    agente = AgenteMarketing(proveedor=_ProveedorFalsoExitoso(), db_session=session)
    entrada = MarketingInput(
        productos_candidato_ids=[producto.id],
        canales_objetivo=[CanalMarketing.EMAIL],
        idioma_destino="es",
    )

    with pytest.raises(ProductosInvalidosError):
        await agente.ejecutar(entrada)


async def test_ejecutar_calcula_distribucion_de_presupuesto_uniforme() -> None:
    producto = _producto()
    session = _db_session_con_productos([producto])
    agente = AgenteMarketing(proveedor=_ProveedorFalsoExitoso(), db_session=session)
    entrada = MarketingInput(
        productos_candidato_ids=[producto.id],
        canales_objetivo=[CanalMarketing.EMAIL, CanalMarketing.REDES_SOCIALES],
        idioma_destino="es",
        presupuesto_mensual_referencia=1000,
    )

    resultado = await agente.ejecutar(entrada)

    assert resultado.distribucion_presupuesto_sugerida == {
        CanalMarketing.EMAIL: 0.5,
        CanalMarketing.REDES_SOCIALES: 0.5,
    }


async def test_ejecutar_sin_presupuesto_no_calcula_distribucion() -> None:
    producto = _producto()
    session = _db_session_con_productos([producto])
    agente = AgenteMarketing(proveedor=_ProveedorFalsoExitoso(), db_session=session)
    entrada = MarketingInput(
        productos_candidato_ids=[producto.id],
        canales_objetivo=[CanalMarketing.EMAIL],
        idioma_destino="es",
    )

    resultado = await agente.ejecutar(entrada)

    assert resultado.distribucion_presupuesto_sugerida is None


async def test_ejecutar_devuelve_respuesta_vacia_si_el_proveedor_falla(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("asyncio.sleep", AsyncMock())
    producto = _producto()
    session = _db_session_con_productos([producto])
    proveedor = _ProveedorFalsoQueSiempreFalla()
    agente = AgenteMarketing(proveedor=proveedor, db_session=session)
    entrada = MarketingInput(
        productos_candidato_ids=[producto.id],
        canales_objetivo=[CanalMarketing.EMAIL],
        idioma_destino="es",
    )

    resultado = await agente.ejecutar(entrada)

    assert resultado.angulos_de_campana == []
    assert any("agotar los reintentos" in a for a in resultado.advertencias)
    # Contrato, sección 8: máximo 2 reintentos -> 3 llamadas totales.
    assert proveedor.llamadas == 3


async def test_no_persiste_nada_en_la_sesion() -> None:
    """Contrato, sección 3: este agente no persiste resultados."""
    producto = _producto()
    session = _db_session_con_productos([producto])
    agente = AgenteMarketing(proveedor=_ProveedorFalsoExitoso(), db_session=session)
    entrada = MarketingInput(
        productos_candidato_ids=[producto.id],
        canales_objetivo=[CanalMarketing.EMAIL],
        idioma_destino="es",
    )

    await agente.ejecutar(entrada)

    session.add.assert_not_called()
    session.commit.assert_not_called()
