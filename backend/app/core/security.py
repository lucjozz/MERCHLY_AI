"""Utilidades de seguridad: contraseñas, access tokens (JWT) y refresh tokens.

Ver docs/013-Seguridad/04-Endurecimiento-para-Lanzamiento.md, sección 3.
"""

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings

ALGORITMO = "HS256"
LEEWAY_SEGUNDOS = 10
COSTO_BCRYPT = 12
PASSWORD_MIN_CARACTERES = 12
PASSWORD_MAX_BYTES = 72  # bcrypt ignora lo que sigue: lo rechazamos.
CLAIMS_OBLIGATORIOS = ("exp", "iat", "sub", "jti", "iss", "aud", "org", "rol", "typ", "ver")

# Hash señuelo: cuando el email no existe se verifica igual contra este
# hash, para que la respuesta tarde lo mismo y no permita enumerar emails.
_HASH_SENUELO = bcrypt.hashpw(b"senuelo-merchly-no-es-una-password", bcrypt.gensalt(COSTO_BCRYPT))


class PasswordInvalidaError(ValueError):
    """La contraseña no cumple la política (013-04, sección 3.2)."""


def validar_politica_password(password: str) -> None:
    """Valida la política de contraseñas al crearlas o cambiarlas.

    Raises:
        PasswordInvalidaError: si es muy corta o supera 72 bytes.
    """
    if len(password) < PASSWORD_MIN_CARACTERES:
        raise PasswordInvalidaError(
            f"La contraseña debe tener al menos {PASSWORD_MIN_CARACTERES} caracteres."
        )
    if len(password.encode("utf-8")) > PASSWORD_MAX_BYTES:
        raise PasswordInvalidaError("La contraseña es demasiado larga (máximo 72 bytes).")


def hashear_password(password: str) -> str:
    """Valida la política y devuelve el hash bcrypt (costo 12)."""
    validar_politica_password(password)
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(COSTO_BCRYPT)).decode("utf-8")


def verificar_password(password: str, password_hash: str | None) -> bool:
    """Compara una contraseña contra su hash en tiempo ~constante.

    Si ``password_hash`` es None (usuario inexistente o solo-Google) se
    verifica contra el hash señuelo y se devuelve False.
    """
    datos = password.encode("utf-8")
    if len(datos) > PASSWORD_MAX_BYTES:
        datos = datos[:PASSWORD_MAX_BYTES]
        password_hash = None  # nunca puede coincidir: no se aceptan > 72 bytes
    if password_hash is None:
        bcrypt.checkpw(datos, _HASH_SENUELO)
        return False
    try:
        return bcrypt.checkpw(datos, password_hash.encode("utf-8"))
    except ValueError:
        return False


def necesita_rehash(password_hash: str) -> bool:
    """True si el hash se generó con un costo menor al actual."""
    try:
        return int(password_hash.split("$")[2]) < COSTO_BCRYPT
    except (IndexError, ValueError):
        return True


@dataclass(frozen=True)
class ClaimsAcceso:
    """Claims ya validados de un access token."""

    usuario_id: uuid.UUID
    organizacion_id: uuid.UUID
    rol: str
    jti: str
    exp: int
    version: int


def crear_access_token(
    usuario_id: uuid.UUID, organizacion_id: uuid.UUID, rol: str, token_version: int
) -> tuple[str, int]:
    """Genera un access token corto.

    Returns:
        tuple[str, int]: el token y su duración en segundos.
    """
    settings = get_settings()
    duracion = settings.access_token_minutos * 60
    ahora = datetime.now(timezone.utc)
    claims = {
        "sub": str(usuario_id),
        "org": str(organizacion_id),
        "rol": rol,
        "ver": token_version,
        "typ": "access",
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(ahora.timestamp()),
        "exp": int((ahora + timedelta(seconds=duracion)).timestamp()),
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(claims, settings.jwt_secret_key, algorithm=ALGORITMO), duracion


def decodificar_access_token(token: str) -> ClaimsAcceso | None:
    """Valida un access token. Devuelve None ante cualquier problema.

    Rechaza: firma inválida, otro algoritmo (incluido ``none``), vencido,
    emisor/audiencia distintos, claims faltantes, ``typ`` distinto de
    ``access`` y ``sub``/``org`` que no sean UUID.
    """
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[ALGORITMO],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            leeway=LEEWAY_SEGUNDOS,
            options={"require": list(CLAIMS_OBLIGATORIOS)},
        )
        if claims.get("typ") != "access":
            return None
        return ClaimsAcceso(
            usuario_id=uuid.UUID(str(claims["sub"])),
            organizacion_id=uuid.UUID(str(claims["org"])),
            rol=str(claims["rol"]),
            jti=str(claims["jti"]),
            exp=int(claims["exp"]),
            version=int(claims["ver"]),
        )
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        return None


def generar_refresh_token() -> tuple[str, str]:
    """Genera un refresh token opaco.

    Returns:
        tuple[str, str]: (token en claro para el cliente, SHA-256 para la base).
    """
    token = secrets.token_urlsafe(48)
    return token, hashear_refresh_token(token)


def hashear_refresh_token(token: str) -> str:
    """SHA-256 hex del refresh token (es aleatorio de 384 bits: no necesita bcrypt)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
