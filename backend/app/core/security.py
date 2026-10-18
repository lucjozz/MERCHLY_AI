"""Utilidades de seguridad: hashing de contraseñas y JWT.

Ver docs/013-Seguridad/01-Modelo-de-Usuarios-y-Autenticacion.md.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()

ALGORITMO = "HS256"
EXPIRACION_HORAS = settings.jwt_expiracion_horas


def verificar_password(password: str, password_hash: str) -> bool:
    """Compara una contraseña en texto plano contra su hash bcrypt.

    Args:
        password: la contraseña ingresada por el usuario.
        password_hash: el hash guardado en la base de datos.

    Returns:
        bool: True si coinciden.
    """
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def crear_token(usuario_id: str, email: str, rol: str) -> tuple[str, int]:
    """Genera un JWT firmado (contrato, sección 3.2 y 3.3).

    Args:
        usuario_id: el UUID del usuario, como string.
        email: el email del usuario.
        rol: el rol del usuario.

    Returns:
        tuple[str, int]: el token firmado, y su duración en segundos.
    """
    expiracion_segundos = EXPIRACION_HORAS * 3600
    ahora = datetime.now(timezone.utc)
    expira = ahora + timedelta(hours=EXPIRACION_HORAS)

    claims = {
        "sub": usuario_id,
        "email": email,
        "rol": rol,
        "iat": int(ahora.timestamp()),
        "exp": int(expira.timestamp()),
    }

    token = jwt.encode(claims, settings.jwt_secret_key, algorithm=ALGORITMO)
    return token, expiracion_segundos


def decodificar_token(token: str) -> dict | None:
    """Valida y decodifica un JWT.

    Args:
        token: el token a validar.

    Returns:
        dict | None: los claims si el token es válido, None si no lo es
        (firma inválida, expirado, o mal formado).
    """
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[ALGORITMO])
    except JWTError:
        return None
    