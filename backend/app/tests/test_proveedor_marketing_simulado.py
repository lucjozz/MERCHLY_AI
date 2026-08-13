"""Tests para ProveedorMarketingSimulado."""

import uuid

import pytest

from app.schemas.marketing import CanalMarketing, MarketingInput
from app.services.proveedores.marketing_simulado import ProveedorMarketingSimulado


def _producto(nombre: str, fuentes_evidencia: list[str] | None = None):
    from types import SimpleNamespace

    return SimpleNamespace(
        id=uuid.uuid4(),
        nombre_producto=nombre,
        fuentes_evidencia=fuentes_evidencia or [],
    )


async def test_genera_copy_para_cada_canal_solicitado() -> None:
    productos = [_producto("Audífonos X", ["https://ejemplo.test"])]
    entrada = MarketingInput(
        productos_candidato_ids=[productos[0].id],
        canales_objetivo=[CanalMarketing.EMAIL, CanalMarketing.REDES_SOCIALES],
        idioma_destino="es",
    )
    proveedor = ProveedorMarketingSimulado()

    resultado = await proveedor.generar_campana(entrada, productos)

    assert set(resultado.copy_por_canal.keys()) == {
        CanalMarketing.EMAIL,
        CanalMarketing.REDES_SOCIALES,
    }
    assert len(resultado.copy_por_canal[CanalMarketing.EMAIL]) == 1


async def test_advierte_productos_sin_evidencia() -> None:
    productos = [_producto("Sin evidencia", fuentes_evidencia=[])]
    entrada = MarketingInput(
        productos_candidato_ids=[productos[0].id],
        canales_objetivo=[CanalMarketing.EMAIL],
        idioma_destino="es",
    )
    proveedor = ProveedorMarketingSimulado()

    resultado = await proveedor.generar_campana(entrada, productos)

    assert any("Sin evidencia" in a for a in resultado.advertencias)
