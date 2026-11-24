"""Verificación en dos pasos (docs/013-Seguridad/09). Sin FastAPI.

Flujo de alta: ``iniciar`` (clave pendiente + QR) → ``activar`` con un código
válido (recién ahí se activa y se entregan 10 códigos de respaldo, una sola vez).

Login: si el usuario la tiene activada, la contraseña (o Google) no alcanza:
se emite un **desafío** de un solo uso (Redis, 5 minutos, 5 intentos) que se
canjea por la sesión con un código del celular o uno de respaldo.

Re-verificación: para acciones sensibles (confirmar pagos) se pide de nuevo un
código o la contraseña; vale 10 minutos.
"""

import hashlib
import secrets
import uuid

import segno
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import totp
from app.core.cifrado import cifrar, descifrar
from app.core.security import verificar_password
from app.models.usuario import Usuario

DESAFIO_TTL = 300
DESAFIO_MAX_INTENTOS = 5
REAUTH_TTL = 600


class CodigoInvalidoError(Exception):
    pass


def _contexto(usuario_id: uuid.UUID) -> str:
    return f"totp:{usuario_id}"


async def _usuario_bloqueado(db_session: AsyncSession, usuario_id: uuid.UUID) -> Usuario:
    return (await db_session.execute(select(Usuario).where(Usuario.id == usuario_id).with_for_update())).scalar_one()


# Todas reciben el ID y no el objeto: después de un rollback (código incorrecto)
# el objeto queda vencido y leerlo fuera del contexto async rompe.


async def iniciar(db_session: AsyncSession, usuario_id: uuid.UUID) -> dict:
    """Genera una clave nueva (pendiente). La activa recién ``activar``."""
    u = await _usuario_bloqueado(db_session, usuario_id)
    secreto = totp.generar_secreto()
    u.totp_pendiente = cifrar(secreto, _contexto(u.id))
    email = u.email
    await db_session.commit()
    enlace = totp.uri(secreto, email)
    return {"secreto": secreto, "uri": enlace, "qr": segno.make(enlace, error="m").svg_data_uri(scale=5, border=2)}


async def activar(db_session: AsyncSession, usuario_id: uuid.UUID, codigo: str) -> list[str]:
    u = await _usuario_bloqueado(db_session, usuario_id)
    if not u.totp_pendiente:
        await db_session.rollback()
        raise CodigoInvalidoError("Primero generá el código QR.")
    secreto = descifrar(u.totp_pendiente, _contexto(u.id))
    paso = totp.verificar(secreto, codigo, None)
    if paso is None:
        await db_session.rollback()
        raise CodigoInvalidoError("El código no es correcto. Revisá la hora del celular y probá con el código nuevo.")
    respaldo = totp.generar_codigos_respaldo()
    u.totp_secreto, u.totp_pendiente = u.totp_pendiente, None
    u.totp_activado, u.totp_ultimo_paso = True, paso
    u.codigos_respaldo = [totp.hash_respaldo(c) for c in respaldo]
    await db_session.commit()
    return respaldo


async def verificar_codigo(db_session: AsyncSession, usuario_id: uuid.UUID, codigo: str) -> bool:
    """Código del celular (sin repetir) o de respaldo (se consume). Deja la sesión commiteada."""
    u = await _usuario_bloqueado(db_session, usuario_id)
    if not u.totp_activado or not u.totp_secreto:
        await db_session.rollback()
        return False
    limpio = (codigo or "").strip()
    if limpio.replace(" ", "").isdigit():
        paso = totp.verificar(descifrar(u.totp_secreto, _contexto(u.id)), limpio, u.totp_ultimo_paso)
        if paso is not None:
            u.totp_ultimo_paso = paso
            await db_session.commit()
            return True
    else:
        h = totp.hash_respaldo(limpio)
        if h in (u.codigos_respaldo or []):
            u.codigos_respaldo = [x for x in u.codigos_respaldo if x != h]  # un solo uso
            await db_session.commit()
            return True
    await db_session.rollback()
    return False


async def desactivar(db_session: AsyncSession, usuario_id: uuid.UUID, codigo: str) -> None:
    if not await verificar_codigo(db_session, usuario_id, codigo):
        raise CodigoInvalidoError("El código no es correcto.")
    u = await _usuario_bloqueado(db_session, usuario_id)
    u.totp_secreto = u.totp_pendiente = None
    u.totp_activado, u.totp_ultimo_paso, u.codigos_respaldo = False, None, []
    await db_session.commit()


# ------------------------------------------------------------------ desafío de login


def _clave_desafio(token: str) -> str:
    return "2fa:desafio:" + hashlib.sha256(token.encode()).hexdigest()


async def crear_desafio(redis: Redis, usuario_id: uuid.UUID) -> str:
    token = secrets.token_urlsafe(32)
    await redis.set(_clave_desafio(token), str(usuario_id), ex=DESAFIO_TTL)
    return token


async def usuario_del_desafio(redis: Redis, token: str) -> uuid.UUID | None:
    """El usuario del desafío, contando un intento. Pasados 5 intentos el desafío se borra."""
    clave = _clave_desafio(token)
    valor = await redis.get(clave)
    if not valor:
        return None
    intentos = await redis.incr(clave + ":intentos")
    await redis.expire(clave + ":intentos", DESAFIO_TTL)
    if intentos > DESAFIO_MAX_INTENTOS:
        await redis.delete(clave, clave + ":intentos")
        return None
    return uuid.UUID(valor.decode() if isinstance(valor, bytes) else valor)


async def consumir_desafio(redis: Redis, token: str) -> None:
    clave = _clave_desafio(token)
    await redis.delete(clave, clave + ":intentos")


# ------------------------------------------------------------------ re-verificación


async def reautenticar(
    redis: Redis, db_session: AsyncSession, usuario_id: uuid.UUID, codigo: str | None, password: str | None
) -> bool:
    """Con 2FA activada: solo el código (la contraseña no alcanza). Sin 2FA: la contraseña."""
    fila = (
        await db_session.execute(select(Usuario.totp_activado, Usuario.password_hash).where(Usuario.id == usuario_id))
    ).one()
    con_codigo, password_hash = fila
    if con_codigo:
        ok = bool(codigo) and await verificar_codigo(db_session, usuario_id, codigo)
    else:
        ok = bool(password) and bool(password_hash) and verificar_password(password, password_hash)
    if ok:
        await redis.set(f"reauth:{usuario_id}", "1", ex=REAUTH_TTL)
    return ok


async def reautenticado(redis: Redis, usuario_id: uuid.UUID) -> bool:
    return bool(await redis.exists(f"reauth:{usuario_id}"))
