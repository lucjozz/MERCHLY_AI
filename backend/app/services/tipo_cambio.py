"""Tipo de cambio oficial USD/BOB del Banco Central de Bolivia (DEC-035). Sin FastAPI.

El BCB no tiene una API oficial; se usa un servicio que republica sus cifras
públicas (configurable con TIPO_CAMBIO_URL). Defensas:
* URL fija de configuración (nunca viene del usuario: sin SSRF).
* Timeout corto y tope de tamaño de respuesta.
* El valor se valida (número razonable) antes de usarse.
* Caché en Redis de 1 hora + último valor conocido sin vencimiento: si la
  fuente falla, se sigue mostrando el último valor marcado como desactualizado.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

import httpx
from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

CLAVE_CACHE = "tipo_cambio:usd_bob"
CLAVE_ULTIMO = "tipo_cambio:usd_bob:ultimo"
TTL_CACHE_SEGUNDOS = 3600
MAX_BYTES_RESPUESTA = 64 * 1024
RANGO_VALIDO = (1.0, 1000.0)  # Bs por dólar; fuera de esto es un dato roto


@dataclass
class TipoCambio:
    valor: float
    fecha: str | None
    fuente: str
    actualizado: str
    desactualizado: bool = False


class TipoCambioNoDisponibleError(Exception):
    pass


def _interpretar(datos: dict) -> TipoCambio:
    """Lee la respuesta del servicio (formato `tc_oficial` del BCB republicado)."""
    oficial = datos.get("tc_oficial") or datos
    valor = float(oficial.get("valor") or oficial.get("venta"))
    if not (RANGO_VALIDO[0] <= valor <= RANGO_VALIDO[1]):
        raise ValueError(f"valor fuera de rango: {valor}")
    fecha = oficial.get("fecha")
    return TipoCambio(
        valor=round(valor, 4),
        fecha=str(fecha)[:10] if fecha else None,
        fuente="Banco Central de Bolivia",
        actualizado=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


async def _consultar_fuente(cliente: httpx.AsyncClient | None = None) -> TipoCambio:
    url = get_settings().tipo_cambio_url
    propio = cliente is None
    cliente = cliente or httpx.AsyncClient(timeout=5.0, follow_redirects=False)
    try:
        respuesta = await cliente.get(url, headers={"User-Agent": "MERCHLY-AI/1.0 (tipo de cambio)"})
        respuesta.raise_for_status()
        if len(respuesta.content) > MAX_BYTES_RESPUESTA:
            raise ValueError("respuesta demasiado grande")
        return _interpretar(respuesta.json())
    finally:
        if propio:
            await cliente.aclose()


async def obtener_tipo_cambio(redis: Redis, cliente: httpx.AsyncClient | None = None) -> TipoCambio:
    """Valor vigente (caché de 1 h). Si la fuente falla, el último conocido."""
    try:
        cacheado = await redis.get(CLAVE_CACHE)
        if cacheado:
            return TipoCambio(**json.loads(cacheado))
    except Exception:  # noqa: BLE001 - sin Redis se consulta la fuente igual
        logger.warning("Redis no disponible para el tipo de cambio")

    try:
        tc = await _consultar_fuente(cliente)
    except Exception as error:  # noqa: BLE001
        logger.warning("No se pudo consultar el tipo de cambio: %s", type(error).__name__)
        try:
            ultimo = await redis.get(CLAVE_ULTIMO)
        except Exception:  # noqa: BLE001
            ultimo = None
        if ultimo:
            tc = TipoCambio(**json.loads(ultimo))
            tc.desactualizado = True
            return tc
        raise TipoCambioNoDisponibleError() from error

    try:
        serializado = json.dumps(asdict(tc))
        await redis.set(CLAVE_CACHE, serializado, ex=TTL_CACHE_SEGUNDOS)
        await redis.set(CLAVE_ULTIMO, serializado)
    except Exception:  # noqa: BLE001
        logger.warning("No se pudo cachear el tipo de cambio (Redis no disponible)")
    return tc
