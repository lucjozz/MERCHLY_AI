"""Middlewares ASGI de seguridad (docs/013-Seguridad/04, secciones 5 y 8).

Son ASGI "puros" (no BaseHTTPMiddleware): más rápidos y sin problemas con
respuestas en streaming.
"""

import json
import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

HEADERS_SEGURIDAD: tuple[tuple[bytes, bytes], ...] = (
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=(), payment=(), usb=()"),
    (b"cross-origin-opener-policy", b"same-origin"),
    (b"cross-origin-resource-policy", b"same-site"),
    # Toda respuesta de la API es privada del usuario: nunca se cachea.
    (b"cache-control", b"no-store"),
    (b"content-security-policy", b"default-src 'none'; frame-ancestors 'none'"),
)
HSTS = (b"strict-transport-security", b"max-age=31536000; includeSubDomains")
RUTAS_DOCS = ("/docs", "/redoc")


class HeadersDeSeguridadMiddleware:
    """Agrega headers de seguridad y un ``X-Request-ID`` a cada respuesta."""

    def __init__(self, app: ASGIApp, hsts: bool = False) -> None:
        self.app = app
        self.hsts = hsts

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = request_id
        es_docs = scope.get("path", "").startswith(RUTAS_DOCS)

        async def _send(message: Message) -> None:
            if message["type"] == "http.response.start":
                existentes = {k.lower() for k, _ in message.get("headers", [])}
                headers = list(message.get("headers", []))
                for clave, valor in HEADERS_SEGURIDAD:
                    # /docs (solo si EXPONER_DOCS) necesita cargar su JS/CSS.
                    if es_docs and clave == b"content-security-policy":
                        continue
                    if clave not in existentes:
                        headers.append((clave, valor))
                if self.hsts:
                    headers.append(HSTS)
                headers.append((b"x-request-id", request_id.encode()))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, _send)


class LimiteDeBodyMiddleware:
    """Rechaza con 413 los bodies de más de ``max_bytes`` (también chunked)."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def _rechazar(self, send: Send) -> None:
        cuerpo = json.dumps({"detail": "El cuerpo de la solicitud es demasiado grande."}).encode()
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(cuerpo)).encode())],
            }
        )
        await send({"type": "http.response.body", "body": cuerpo})

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        for clave, valor in scope.get("headers", []):
            if clave == b"content-length":
                try:
                    if int(valor) > self.max_bytes:
                        await self._rechazar(send)
                        return
                except ValueError:
                    await self._rechazar(send)
                    return

        recibidos = 0
        respuesta_iniciada = False

        async def _receive() -> Message:
            nonlocal recibidos
            mensaje = await receive()
            if mensaje["type"] == "http.request":
                recibidos += len(mensaje.get("body", b""))
                if recibidos > self.max_bytes:
                    raise _BodyDemasiadoGrande()
            return mensaje

        async def _send(message: Message) -> None:
            nonlocal respuesta_iniciada
            if message["type"] == "http.response.start":
                respuesta_iniciada = True
            await send(message)

        try:
            await self.app(scope, _receive, _send)
        except _BodyDemasiadoGrande:
            if not respuesta_iniciada:
                await self._rechazar(send)


class _BodyDemasiadoGrande(Exception):
    pass
