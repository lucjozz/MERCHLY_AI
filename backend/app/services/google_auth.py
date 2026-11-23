"""Verificación de ID tokens de Google (docs/013-Seguridad/04, sección 3.1).

Se verifica: firma RS256 contra las claves públicas de Google (JWKS,
cacheadas), audiencia = nuestro GOOGLE_CLIENT_ID, emisor de Google,
vencimiento y email verificado. Sin FastAPI.
"""

import asyncio
from dataclasses import dataclass

import jwt
from jwt import PyJWKClient

GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("accounts.google.com", "https://accounts.google.com")

_cliente_jwks = PyJWKClient(GOOGLE_JWKS_URL, cache_keys=True, lifespan=3600, timeout=5)


class GoogleTokenInvalidoError(Exception):
    pass


@dataclass(frozen=True)
class IdentidadGoogle:
    sub: str
    email: str
    nombre: str


def _verificar_sync(id_token: str, client_id: str) -> IdentidadGoogle:
    try:
        clave = _cliente_jwks.get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token,
            clave.key,
            algorithms=["RS256"],
            audience=client_id,
            leeway=10,
            options={"require": ["exp", "iat", "iss", "aud", "sub", "email"]},
        )
    except jwt.PyJWTError as error:
        raise GoogleTokenInvalidoError(str(error)) from error

    if claims.get("iss") not in GOOGLE_ISSUERS:
        raise GoogleTokenInvalidoError("emisor inválido")
    if claims.get("email_verified") is not True:
        raise GoogleTokenInvalidoError("email no verificado")
    sub = str(claims["sub"])
    email = str(claims["email"])
    if not sub or len(sub) > 255 or len(email) > 255:
        raise GoogleTokenInvalidoError("claims fuera de rango")
    return IdentidadGoogle(sub=sub, email=email, nombre=str(claims.get("name", ""))[:120])


async def verificar_id_token_google(id_token: str, client_id: str) -> IdentidadGoogle:
    """Verifica el ID token (la descarga de claves es bloqueante: va a un hilo)."""
    return await asyncio.to_thread(_verificar_sync, id_token, client_id)
