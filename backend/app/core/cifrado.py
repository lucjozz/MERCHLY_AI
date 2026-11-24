"""Cifrado de secretos guardados en la base (docs/013-Seguridad/04, sección 9).

AES-256-GCM. Se usa para lo que NO se puede guardar como hash porque hay que
volver a leerlo: la clave TOTP de la verificación en dos pasos y, en la Fase B,
los tokens de los canales (WhatsApp, Instagram, Facebook).

* Clave: ``CIFRADO_CLAVE`` (32 bytes en base64). En producción es obligatoria
  (el arranque falla sin ella). En local, si falta, se deriva del JWT con HKDF
  y un contexto propio, para no reutilizar la misma clave en dos usos.
* ``contexto`` (AAD): ata el texto cifrado a su dueño (p. ej. el id del
  usuario). Un valor copiado a otra fila no se puede descifrar.
* Formato: ``v1:<base64(nonce || cifrado)>``; el prefijo permite rotar el esquema.
"""

import base64
import os
from functools import lru_cache

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.core.config import get_settings

PREFIJO = "v1:"


class CifradoInvalidoError(Exception):
    pass


@lru_cache
def _clave() -> bytes:
    settings = get_settings()
    if settings.cifrado_clave:
        clave = base64.b64decode(settings.cifrado_clave)
        if len(clave) != 32:
            raise CifradoInvalidoError("CIFRADO_CLAVE tiene que tener 32 bytes (en base64).")
        return clave
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"merchly:cifrado:v1").derive(
        settings.jwt_secret_key.encode()
    )


def cifrar(texto: str, contexto: str) -> str:
    nonce = os.urandom(12)
    datos = AESGCM(_clave()).encrypt(nonce, texto.encode(), contexto.encode())
    return PREFIJO + base64.b64encode(nonce + datos).decode()


def descifrar(valor: str, contexto: str) -> str:
    if not valor.startswith(PREFIJO):
        raise CifradoInvalidoError("Formato desconocido.")
    try:
        crudo = base64.b64decode(valor[len(PREFIJO):])
        return AESGCM(_clave()).decrypt(crudo[:12], crudo[12:], contexto.encode()).decode()
    except (InvalidTag, ValueError) as error:
        raise CifradoInvalidoError("No se pudo descifrar.") from error
