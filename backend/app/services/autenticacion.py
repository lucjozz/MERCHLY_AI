"""Servicio de autenticación (docs/013-Seguridad/04, sección 3). Sin FastAPI."""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    COSTO_BCRYPT,
    crear_access_token,
    generar_refresh_token,
    hashear_refresh_token,
    necesita_rehash,
    verificar_password,
)
from app.models.organizacion import Organizacion
from app.models.refresh_token import RefreshToken
from app.models.usuario import Usuario

logger = logging.getLogger(__name__)

# Requests paralelos del navegador pueden refrescar con el mismo token a la
# vez; dentro de esta ventana no se considera robo.
GRACIA_ROTACION_SEGUNDOS = 20


@dataclass(frozen=True)
class Sesion:
    access_token: str
    expira_en: int
    refresh_token: str
    refresh_expira_en: int


class RefreshInvalidoError(Exception):
    """Refresh token inexistente, vencido, revocado o de un usuario inactivo."""


async def autenticar_usuario(
    db_session: AsyncSession, email: str, password: str
) -> Usuario | None:
    """Valida email y contraseña en tiempo ~constante.

    Siempre se ejecuta un bcrypt (contra el hash real o un señuelo), para
    que "no existe", "contraseña mala" e "inactivo" tarden lo mismo y
    devuelvan lo mismo (None).
    """
    consulta = select(Usuario).where(Usuario.email == email.strip().lower())
    usuario = (await db_session.execute(consulta)).scalar_one_or_none()

    hash_guardado = usuario.password_hash if usuario is not None else None
    valida = verificar_password(password, hash_guardado)

    if usuario is None or not valida or not usuario.activo or usuario.eliminado_en is not None:
        return None

    organizacion = await db_session.get(Organizacion, usuario.organizacion_id)
    if organizacion is None or not organizacion.activo:
        return None

    if hash_guardado and necesita_rehash(hash_guardado):
        import bcrypt  # local: solo en el caso raro de re-hash

        usuario.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(COSTO_BCRYPT)
        ).decode("utf-8")
        await db_session.commit()

    return usuario


async def emitir_sesion(
    db_session: AsyncSession, usuario: Usuario, familia: uuid.UUID | None = None
) -> Sesion:
    """Crea access token + refresh token (persistido hasheado)."""
    settings = get_settings()
    access, expira_en = crear_access_token(
        usuario_id=usuario.id,
        organizacion_id=usuario.organizacion_id,
        rol=usuario.rol,
        token_version=usuario.token_version,
    )
    refresh, refresh_hash = generar_refresh_token()
    refresh_duracion = settings.refresh_token_dias * 86400
    db_session.add(
        RefreshToken(
            id=uuid.uuid4(),
            usuario_id=usuario.id,
            token_hash=refresh_hash,
            familia=familia or uuid.uuid4(),
            expira_en=datetime.now(timezone.utc) + timedelta(seconds=refresh_duracion),
        )
    )
    await db_session.commit()
    return Sesion(access, expira_en, refresh, refresh_duracion)


async def _revocar_familia(db_session: AsyncSession, familia: uuid.UUID) -> None:
    await db_session.execute(
        update(RefreshToken)
        .where(RefreshToken.familia == familia, RefreshToken.revocado_en.is_(None))
        .values(revocado_en=datetime.now(timezone.utc))
    )


async def rotar_refresh(db_session: AsyncSession, refresh_token: str) -> Sesion:
    """Canjea un refresh token por una sesión nueva (rotación).

    Si el token ya había sido usado (revocado), se asume robo: se revoca
    toda la familia y se rechaza.

    Raises:
        RefreshInvalidoError: en cualquier caso inválido.
    """
    consulta = (
        select(RefreshToken)
        .where(RefreshToken.token_hash == hashear_refresh_token(refresh_token))
        .with_for_update()
    )
    fila = (await db_session.execute(consulta)).scalar_one_or_none()
    if fila is None:
        raise RefreshInvalidoError()

    ahora = datetime.now(timezone.utc)
    if fila.revocado_en is not None or fila.expira_en <= ahora:
        raise RefreshInvalidoError()
    if fila.rotado_en is not None:
        if ahora - fila.rotado_en > timedelta(seconds=GRACIA_ROTACION_SEGUNDOS):
            logger.warning("Reutilización de refresh token detectada: se revoca la familia")
            await _revocar_familia(db_session, fila.familia)
            await db_session.commit()
            raise RefreshInvalidoError()
        # Dentro de la gracia: otra pestaña/request refrescó al mismo tiempo.

    usuario = await db_session.get(Usuario, fila.usuario_id)
    organizacion = (
        await db_session.get(Organizacion, usuario.organizacion_id) if usuario else None
    )
    if (
        usuario is None
        or not usuario.activo
        or usuario.eliminado_en is not None
        or organizacion is None
        or not organizacion.activo
    ):
        await _revocar_familia(db_session, fila.familia)
        await db_session.commit()
        raise RefreshInvalidoError()

    if fila.rotado_en is None:
        fila.rotado_en = ahora
    return await emitir_sesion(db_session, usuario, familia=fila.familia)


async def revocar_refresh(db_session: AsyncSession, refresh_token: str, usuario_id: uuid.UUID) -> None:
    """Revoca la familia del refresh token (logout). Solo si es del usuario."""
    consulta = select(RefreshToken).where(
        RefreshToken.token_hash == hashear_refresh_token(refresh_token),
        RefreshToken.usuario_id == usuario_id,
    )
    fila = (await db_session.execute(consulta)).scalar_one_or_none()
    if fila is not None:
        await _revocar_familia(db_session, fila.familia)
        await db_session.commit()


async def cerrar_todas_las_sesiones(db_session: AsyncSession, usuario: Usuario) -> None:
    """Invalida todos los access tokens (token_version) y refresh tokens."""
    usuario.token_version += 1
    await db_session.execute(
        update(RefreshToken)
        .where(RefreshToken.usuario_id == usuario.id, RefreshToken.revocado_en.is_(None))
        .values(revocado_en=datetime.now(timezone.utc))
    )
    await db_session.commit()


async def usuario_desde_google(
    db_session: AsyncSession, google_sub: str, email: str, nombre: str
) -> Usuario | None:
    """Login o auto-registro con Google (013-04, sección 3.1).

    * ``google_sub`` ya vinculado → ese usuario.
    * Email existente sin vincular → se vincula.
    * Nuevo → se crea su organización y queda como ``admin_principal``.

    Returns:
        Usuario | None: None si el usuario/organización está inactivo.
    """
    email = email.strip().lower()
    usuario = (
        await db_session.execute(select(Usuario).where(Usuario.google_sub == google_sub))
    ).scalar_one_or_none()

    if usuario is None:
        usuario = (
            await db_session.execute(select(Usuario).where(Usuario.email == email))
        ).scalar_one_or_none()
        if usuario is not None:
            if usuario.google_sub is not None:
                return None  # el email está vinculado a OTRA cuenta de Google
            usuario.google_sub = google_sub
        else:
            nombre_limpio = (nombre or email.split("@")[0]).strip()[:120] or "Usuario"
            organizacion = Organizacion(id=uuid.uuid4(), nombre=f"Negocio de {nombre_limpio}"[:120])
            db_session.add(organizacion)
            await db_session.flush()
            usuario = Usuario(
                id=uuid.uuid4(),
                organizacion_id=organizacion.id,
                email=email,
                password_hash=None,
                google_sub=google_sub,
                nombre=nombre_limpio,
                rol="admin_principal",
                activo=True,
                token_version=0,
            )
            db_session.add(usuario)
        await db_session.commit()

    if not usuario.activo or usuario.eliminado_en is not None:
        return None
    organizacion = await db_session.get(Organizacion, usuario.organizacion_id)
    if organizacion is None or not organizacion.activo:
        return None
    return usuario
