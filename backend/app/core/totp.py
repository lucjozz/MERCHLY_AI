"""TOTP (RFC 6238) para la verificación en dos pasos. Sin dependencias externas.

Compatible con Google Authenticator, Microsoft Authenticator, Authy, 1Password:
SHA-1, 6 dígitos, pasos de 30 segundos. Se acepta ±1 paso por desfasaje del
reloj del celular, y nunca el mismo paso dos veces (anti-repetición).
"""

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

PASO_SEGUNDOS = 30
DIGITOS = 6
EMISOR = "MERCHLY AI"


def generar_secreto() -> str:
    """160 bits aleatorios en base32 (lo que se escanea con el celular)."""
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _codigo(secreto: str, paso: int) -> str:
    clave = base64.b32decode(secreto + "=" * (-len(secreto) % 8))
    digest = hmac.new(clave, struct.pack(">Q", paso), hashlib.sha1).digest()
    desplazamiento = digest[-1] & 0x0F
    numero = struct.unpack(">I", digest[desplazamiento:desplazamiento + 4])[0] & 0x7FFFFFFF
    return str(numero % 10**DIGITOS).zfill(DIGITOS)


def paso_actual(ahora: float | None = None) -> int:
    return int((time.time() if ahora is None else ahora) // PASO_SEGUNDOS)


def codigo_actual(secreto: str, ahora: float | None = None) -> str:
    return _codigo(secreto, paso_actual(ahora))


def verificar(secreto: str, codigo: str, ultimo_paso: int | None, ahora: float | None = None) -> int | None:
    """Devuelve el paso usado si el código es válido y no se usó antes; si no, None."""
    codigo = (codigo or "").replace(" ", "")
    if len(codigo) != DIGITOS or not codigo.isdigit():
        return None
    actual = paso_actual(ahora)
    for paso in (actual - 1, actual, actual + 1):
        if ultimo_paso is not None and paso <= ultimo_paso:
            continue  # anti-repetición: un código ya usado no sirve otra vez
        if hmac.compare_digest(_codigo(secreto, paso), codigo):
            return paso
    return None


def uri(secreto: str, email: str) -> str:
    etiqueta = quote(f"{EMISOR}:{email}")
    return f"otpauth://totp/{etiqueta}?secret={secreto}&issuer={quote(EMISOR)}&algorithm=SHA1&digits={DIGITOS}&period={PASO_SEGUNDOS}"


# ------------------------------------------------------------------ códigos de respaldo

ALFABETO = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"  # sin 0/O/1/I/L


def generar_codigos_respaldo(cantidad: int = 10) -> list[str]:
    return ["-".join("".join(secrets.choice(ALFABETO) for _ in range(4)) for _ in range(2)) for _ in range(cantidad)]


def hash_respaldo(codigo: str) -> str:
    normal = (codigo or "").upper().replace("-", "").replace(" ", "")
    return hashlib.sha256(f"merchly-respaldo:{normal}".encode()).hexdigest()
