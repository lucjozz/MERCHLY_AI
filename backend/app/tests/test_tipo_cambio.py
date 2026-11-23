"""Tests del tipo de cambio del BCB (DEC-035) sin red: httpx.MockTransport + Redis falso."""

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.tipo_cambio import (
    CLAVE_ULTIMO,
    TipoCambioNoDisponibleError,
    obtener_tipo_cambio,
)
from app.tests.conftest import RedisFalso


class RedisTexto(RedisFalso):
    """Redis falso que guarda strings (el tipo de cambio se cachea como JSON)."""

    async def set(self, clave, valor, ex=None, nx=False):
        self.datos[clave] = valor
        return True


def _cliente(respuesta: httpx.Response | Exception, contador: list | None = None) -> httpx.AsyncClient:
    def manejar(request: httpx.Request) -> httpx.Response:
        if contador is not None:
            contador.append(request.url)
        if isinstance(respuesta, Exception):
            raise respuesta
        return respuesta

    return httpx.AsyncClient(transport=httpx.MockTransport(manejar))


BCB_OK = {"tc_oficial": {"valor": 11.75, "fecha": "2026-11-23", "regimen": "flexible"}}


async def test_lee_el_valor_oficial_y_lo_cachea() -> None:
    redis, llamadas = RedisTexto(), []
    tc = await obtener_tipo_cambio(redis, _cliente(httpx.Response(200, json=BCB_OK), llamadas))
    assert tc.valor == 11.75 and tc.fecha == "2026-11-23" and not tc.desactualizado
    otra = await obtener_tipo_cambio(redis, _cliente(httpx.Response(200, json=BCB_OK), llamadas))
    assert otra.valor == 11.75 and len(llamadas) == 1  # la segunda vez sale de la caché


async def test_si_la_fuente_falla_usa_el_ultimo_valor_marcado_desactualizado() -> None:
    redis = RedisTexto()
    await obtener_tipo_cambio(redis, _cliente(httpx.Response(200, json=BCB_OK)))
    redis.datos.pop("tipo_cambio:usd_bob")  # venció la caché
    tc = await obtener_tipo_cambio(redis, _cliente(httpx.ConnectError("caído")))
    assert tc.valor == 11.75 and tc.desactualizado is True


async def test_sin_fuente_ni_ultimo_valor_es_no_disponible() -> None:
    with pytest.raises(TipoCambioNoDisponibleError):
        await obtener_tipo_cambio(RedisTexto(), _cliente(httpx.Response(500)))


@pytest.mark.parametrize("valor", [0, -5, 50_000, "abc", None])
async def test_rechaza_valores_absurdos(valor) -> None:
    redis = RedisTexto()
    with pytest.raises(TipoCambioNoDisponibleError):
        await obtener_tipo_cambio(redis, _cliente(httpx.Response(200, json={"tc_oficial": {"valor": valor}})))
    assert CLAVE_ULTIMO not in redis.datos  # un dato roto nunca queda guardado


def test_endpoint_exige_sesion() -> None:
    assert TestClient(app).get("/tipo-cambio").status_code == 401
