"""Límite general de pedidos por minuto (docs/013-Seguridad/09, sección 8).

Cierra TODAS las ventanas de entrada, no solo el login:
* Con sesión válida: por usuario (lecturas y escrituras por separado).
* Sin sesión: por IP (login, refresh, recuperar contraseña, invitaciones...).
* ``/auth/refresh`` tiene su propio tope por IP (un token inventado nunca se
  acierta, pero así no se puede usar para cargar la base).

Ventana fija de 60 s en Redis. Fail-open: si Redis no responde se deja pasar
y se registra (el login y los pagos ya son fail-closed por su cuenta).
Los límites son holgados para una persona y bajos para un script.
"""

import hashlib
import logging
import time

from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import get_settings
from app.core.security import decodificar_access_token

logger = logging.getLogger(__name__)

ESCRITURA = {"POST", "PUT", "PATCH", "DELETE"}
EXENTAS = ("/health",)
VENTANA = 60


def _ip(scope: Scope) -> str:
    headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
    if get_settings().confiar_proxy:
        if headers.get("cf-connecting-ip"):
            return headers["cf-connecting-ip"].strip()
        if headers.get("x-forwarded-for"):
            return headers["x-forwarded-for"].split(",")[0].strip()
    cliente = scope.get("client")
    return cliente[0] if cliente else "desconocida"


def _usuario(scope: Scope) -> str | None:
    for clave, valor in scope.get("headers", []):
        if clave.lower() == b"authorization":
            texto = valor.decode("latin-1")
            if texto[:7].lower() == "bearer ":
                claims = decodificar_access_token(texto[7:].strip())
                return str(claims.usuario_id) if claims else None
    return None


def topes(metodo: str, ruta: str, con_sesion: bool) -> tuple[str, int]:
    s = get_settings()
    if ruta == "/auth/refresh":
        return "refresh", s.limite_refresh_por_minuto
    if not con_sesion:
        return "anonimo", s.limite_anonimo_por_minuto
    if metodo in ESCRITURA:
        return "escritura", s.limite_escrituras_por_minuto
    return "lectura", s.limite_lecturas_por_minuto


class LimiteDePeticionesMiddleware:
    def __init__(self, app: ASGIApp, obtener_redis) -> None:
        self.app = app
        self.obtener_redis = obtener_redis  # función: así los tests pueden poner un Redis falso

    async def _rechazar(self, send: Send, espera: int) -> None:
        cuerpo = b'{"detail":"Demasiados pedidos seguidos. Esper\xc3\xa1 un momento y prob\xc3\xa1 de nuevo."}'
        await send({
            "type": "http.response.start", "status": 429,
            "headers": [(b"content-type", b"application/json"), (b"retry-after", str(espera).encode()),
                        (b"content-length", str(len(cuerpo)).encode())],
        })
        await send({"type": "http.response.body", "body": cuerpo})

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ruta = scope.get("path", "")
        if scope["type"] != "http" or not get_settings().limites_activos or ruta.startswith(EXENTAS):
            await self.app(scope, receive, send)
            return
        usuario = _usuario(scope)
        tipo, tope = topes(scope.get("method", "GET"), ruta, usuario is not None)
        sujeto = f"u:{usuario}" if usuario and tipo != "refresh" else f"ip:{_ip(scope)}"
        ventana = int(time.time() // VENTANA)
        clave = f"limite:{tipo}:{hashlib.sha256(sujeto.encode()).hexdigest()[:24]}:{ventana}"
        try:
            redis: Redis = self.obtener_redis()
            usados = await redis.incr(clave)
            if usados == 1:
                await redis.expire(clave, VENTANA + 5)
        except (RedisError, OSError):
            logger.warning("Redis no disponible: límite general no aplicado (fail-open)")
            await self.app(scope, receive, send)
            return
        if usados > tope:
            await self._rechazar(send, VENTANA - int(time.time()) % VENTANA)
            return
        await self.app(scope, receive, send)
