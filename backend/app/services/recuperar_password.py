"""Recuperación de contraseña (DEC-036). Sin FastAPI.

* Respuesta idéntica exista o no el email (sin enumeración).
* Token aleatorio de 256 bits, solo en el link; en la base, su SHA-256.
* Vence en 1 hora y se usa una sola vez; pedir otro invalida los anteriores.
* Al restablecer: nueva contraseña (política 013-04) y se cierran TODAS las
  sesiones del usuario.
"""

import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hashear_password, hashear_refresh_token
from app.models.restablecimiento import RestablecimientoPassword
from app.models.usuario import Usuario
from app.services.autenticacion import cerrar_todas_las_sesiones
from app.services.email import Email, EmailNoEnviadoError, enviar_email

logger = logging.getLogger(__name__)
VIGENCIA = timedelta(hours=1)


class TokenRestablecimientoInvalidoError(Exception):
    pass


async def solicitar_restablecimiento(db_session: AsyncSession, email: str) -> None:
    """Si el email corresponde a un usuario activo, le manda el link. Nunca revela si existe."""
    usuario = (
        await db_session.execute(select(Usuario).where(Usuario.email == email.strip().lower()))
    ).scalar_one_or_none()
    if usuario is None or not usuario.activo or usuario.eliminado_en is not None:
        return

    ahora = datetime.now(timezone.utc)
    await db_session.execute(  # vale solo el último link pedido
        update(RestablecimientoPassword)
        .where(RestablecimientoPassword.usuario_id == usuario.id, RestablecimientoPassword.usado_en.is_(None))
        .values(usado_en=ahora)
    )
    token = secrets.token_urlsafe(32)
    db_session.add(
        RestablecimientoPassword(
            id=uuid.uuid4(),
            usuario_id=usuario.id,
            token_hash=hashear_refresh_token(token),
            expira_en=ahora + VIGENCIA,
        )
    )
    await db_session.commit()

    enlace = f"{get_settings().app_url.rstrip('/')}/restablecer#{token}"
    try:
        await enviar_email(
            Email(
                para=usuario.email,
                asunto="Restablecé tu contraseña de MERCHLY AI",
                texto=(
                    f"Hola {usuario.nombre}:\n\n"
                    "Pediste restablecer tu contraseña. Entrá a este link para elegir una nueva "
                    f"(vence en 1 hora y se usa una sola vez):\n\n{enlace}\n\n"
                    "Si no fuiste vos, ignorá este email: tu contraseña no cambia."
                ),
            )
        )
    except EmailNoEnviadoError:
        logger.error("No se pudo enviar el email de restablecimiento")


async def restablecer_password(db_session: AsyncSession, token: str, password_nueva: str) -> Usuario:
    """Raises TokenRestablecimientoInvalidoError o PasswordInvalidaError."""
    password_hash = hashear_password(password_nueva)  # política antes de tocar la base
    fila = (
        await db_session.execute(
            select(RestablecimientoPassword)
            .where(RestablecimientoPassword.token_hash == hashear_refresh_token(token))
            .with_for_update()
        )
    ).scalar_one_or_none()
    ahora = datetime.now(timezone.utc)
    if fila is None or fila.usado_en is not None or fila.expira_en <= ahora:
        raise TokenRestablecimientoInvalidoError()
    usuario = await db_session.get(Usuario, fila.usuario_id)
    if usuario is None or not usuario.activo or usuario.eliminado_en is not None:
        raise TokenRestablecimientoInvalidoError()

    fila.usado_en = ahora
    usuario.password_hash = password_hash
    await cerrar_todas_las_sesiones(db_session, usuario)  # token_version++ y refresh revocados; commit
    logger.info("password_restablecida usuario=%s", usuario.id)
    return usuario
