"""Seguridad de los webhooks de Meta (WhatsApp, Instagram, Facebook). Fase B, lista y probada.

Cuando se conecte WhatsApp, el endpoint público ``POST /webhooks/meta`` va a:
1. Verificar la firma ``X-Hub-Signature-256`` (HMAC-SHA256 del cuerpo CRUDO con
   el App Secret). Sin firma válida → 401 y no se lee nada.
2. Descartar mensajes repetidos (Meta reintenta): idempotencia por id de mensaje.
3. Descartar mensajes demasiado viejos (24 h): un atacante que capture un
   webhook firmado no puede re-enviarlo días después.
4. Guardar los tokens de cada negocio CIFRADOS (``app/core/cifrado.py``), atados
   a la organización y al canal: un token copiado a otra fila no se descifra.

La verificación de la suscripción (``GET`` con ``hub.challenge``) compara el
token en tiempo constante.
"""

import hashlib
import hmac
import time
import uuid

from redis.asyncio import Redis

from app.core.cifrado import cifrar, descifrar

VENTANA_IDEMPOTENCIA = 7 * 24 * 3600
ANTIGUEDAD_MAXIMA = 24 * 3600


def firma_valida(cuerpo: bytes, cabecera: str | None, secreto_app: str | None) -> bool:
    """``cabecera`` = "sha256=<hex>". Falla cerrado si falta algo."""
    if not cabecera or not secreto_app or not cabecera.startswith("sha256="):
        return False
    esperada = hmac.new(secreto_app.encode(), cuerpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperada, cabecera.removeprefix("sha256="))


def responder_suscripcion(modo: str | None, token: str | None, desafio: str | None, token_esperado: str | None) -> str | None:
    """El ``hub.challenge`` si Meta presentó el token correcto; si no, None (→ 403)."""
    if modo != "subscribe" or not token or not token_esperado or not desafio:
        return None
    if not hmac.compare_digest(token.encode(), token_esperado.encode()):
        return None
    return desafio[:200]


async def es_nuevo(redis: Redis, canal: str, id_mensaje: str) -> bool:
    """True la primera vez que llega ese mensaje; False en los reintentos."""
    clave = "webhook:visto:" + hashlib.sha256(f"{canal}:{id_mensaje}".encode()).hexdigest()
    return bool(await redis.set(clave, "1", ex=VENTANA_IDEMPOTENCIA, nx=True))


def es_reciente(marca_unix: int | str | None, ahora: float | None = None) -> bool:
    try:
        marca = int(marca_unix)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    ahora = time.time() if ahora is None else ahora
    return -300 <= ahora - marca <= ANTIGUEDAD_MAXIMA  # 5 min de tolerancia por relojes adelantados


def _contexto(organizacion_id: uuid.UUID, canal: str) -> str:
    return f"canal:{organizacion_id}:{canal}"


def cifrar_token(organizacion_id: uuid.UUID, canal: str, token: str) -> str:
    return cifrar(token, _contexto(organizacion_id, canal))


def descifrar_token(organizacion_id: uuid.UUID, canal: str, valor: str) -> str:
    return descifrar(valor, _contexto(organizacion_id, canal))
