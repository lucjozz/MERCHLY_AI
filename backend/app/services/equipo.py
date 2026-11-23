"""Gestión del equipo: miembros, invitaciones y roles (docs/004-Backend/03, sección 5). Sin FastAPI.

Reglas:
* Todo dentro de la organización del admin (la app filtra siempre por organización).
* Nadie cambia su propio rol ni se desactiva a sí mismo.
* La organización nunca se queda sin un admin_principal activo.
* Desactivar a alguien o cambiarle el rol cierra todas sus sesiones.
* El token de invitación solo existe en el link: en la base, su SHA-256.
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hashear_password, hashear_refresh_token
from app.models.invitacion import Invitacion
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.schemas.usuarios import InvitacionEntrada, MiembroCambio
from app.services.autenticacion import cerrar_todas_las_sesiones

DIAS_VALIDEZ_INVITACION = 7
# Código corto y legible (Crockford base32: sin I, L, O, U). 12 caracteres = 60 bits:
# imposible de adivinar con el límite de intentos por IP y la vigencia de 7 días.
ALFABETO_CODIGO = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_EQUIVALENTES = str.maketrans({"O": "0", "I": "1", "L": "1"})


def generar_codigo_invitacion() -> str:
    crudo = "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(12))
    return f"{crudo[:4]}-{crudo[4:8]}-{crudo[8:]}"


def normalizar_codigo(codigo: str) -> str:
    """Acepta el código con o sin guiones, en minúsculas y con O/I/L confundidas."""
    return "".join(c for c in codigo.upper().translate(_EQUIVALENTES) if c in ALFABETO_CODIGO)
MAX_INVITACIONES_PENDIENTES = 50


class ReglaEquipoError(Exception):
    """La operación viola una regla del equipo (-> 409 / 422 según el caso)."""


class InvitacionInvalidaError(Exception):
    """Token inexistente, vencido, usado o revocado (-> 400, mismo mensaje siempre)."""


async def listar_miembros(db_session: AsyncSession, organizacion_id: uuid.UUID) -> list[Usuario]:
    consulta = (
        select(Usuario)
        .where(Usuario.organizacion_id == organizacion_id, Usuario.eliminado_en.is_(None))
        .order_by(Usuario.creado_en)
    )
    return list((await db_session.execute(consulta)).scalars().all())


async def listar_invitaciones(db_session: AsyncSession, organizacion_id: uuid.UUID) -> list[Invitacion]:
    consulta = (
        select(Invitacion)
        .where(Invitacion.organizacion_id == organizacion_id, Invitacion.eliminado_en.is_(None))
        .order_by(Invitacion.creado_en.desc())
        .limit(100)
    )
    return list((await db_session.execute(consulta)).scalars().all())


async def invitar(
    db_session: AsyncSession, admin: Usuario, entrada: InvitacionEntrada
) -> tuple[Invitacion, str]:
    """Crea una invitación. Devuelve (invitación, token en claro para el link)."""
    existente = (
        await db_session.execute(select(Usuario).where(Usuario.email == entrada.email))
    ).scalar_one_or_none()
    if existente is not None:
        # Mensaje neutro: no confirmar a qué organización pertenece ese email.
        raise ReglaEquipoError("Ese email ya tiene una cuenta en MERCHLY.")

    ahora = datetime.now(timezone.utc)
    pendientes = await db_session.scalar(
        select(func.count()).select_from(Invitacion).where(
            Invitacion.organizacion_id == admin.organizacion_id,
            Invitacion.aceptada_en.is_(None),
            Invitacion.revocada_en.is_(None),
            Invitacion.expira_en > ahora,
        )
    )
    if (pendientes or 0) >= MAX_INVITACIONES_PENDIENTES:
        raise ReglaEquipoError("Hay demasiadas invitaciones pendientes. Revocá alguna antes de crear otra.")

    # Una invitación pendiente previa al mismo email se revoca (vale la última).
    previas = await db_session.execute(
        select(Invitacion).where(
            Invitacion.organizacion_id == admin.organizacion_id,
            Invitacion.email == entrada.email,
            Invitacion.aceptada_en.is_(None),
            Invitacion.revocada_en.is_(None),
        )
    )
    for previa in previas.scalars().all():
        previa.revocada_en = ahora

    token = generar_codigo_invitacion()
    invitacion = Invitacion(
        id=uuid.uuid4(),
        organizacion_id=admin.organizacion_id,
        email=entrada.email,
        rol=entrada.rol,
        token_hash=hashear_refresh_token(normalizar_codigo(token)),
        expira_en=ahora + timedelta(days=DIAS_VALIDEZ_INVITACION),
        creado_por=admin.id,
    )
    db_session.add(invitacion)
    await db_session.commit()
    await db_session.refresh(invitacion)
    return invitacion, token


async def revocar_invitacion(db_session: AsyncSession, organizacion_id: uuid.UUID, invitacion_id: uuid.UUID) -> bool:
    invitacion = (
        await db_session.execute(
            select(Invitacion).where(Invitacion.id == invitacion_id, Invitacion.organizacion_id == organizacion_id)
        )
    ).scalar_one_or_none()
    if invitacion is None or invitacion.aceptada_en is not None:
        return False
    invitacion.revocada_en = invitacion.revocada_en or datetime.now(timezone.utc)
    await db_session.commit()
    return True


async def _admins_activos(db_session: AsyncSession, organizacion_id: uuid.UUID) -> int:
    return int(
        await db_session.scalar(
            select(func.count()).select_from(Usuario).where(
                Usuario.organizacion_id == organizacion_id,
                Usuario.rol == "admin_principal",
                Usuario.activo.is_(True),
                Usuario.eliminado_en.is_(None),
            )
        )
        or 0
    )


async def cambiar_miembro(
    db_session: AsyncSession, admin: Usuario, miembro_id: uuid.UUID, cambio: MiembroCambio
) -> Usuario | None:
    """Cambia rol y/o estado de un miembro de la MISMA organización. None = no existe (404)."""
    if miembro_id == admin.id:
        raise ReglaEquipoError("No podés cambiar tu propio rol ni desactivarte. Pedíselo a otro admin.")
    miembro = (
        await db_session.execute(
            select(Usuario)
            .where(
                Usuario.id == miembro_id,
                Usuario.organizacion_id == admin.organizacion_id,
                Usuario.eliminado_en.is_(None),
            )
            .with_for_update()
        )
    ).scalar_one_or_none()
    if miembro is None:
        return None

    deja_de_ser_admin_activo = miembro.rol == "admin_principal" and miembro.activo and (
        (cambio.rol is not None and cambio.rol != "admin_principal") or cambio.activo is False
    )
    if deja_de_ser_admin_activo and await _admins_activos(db_session, admin.organizacion_id) <= 1:
        raise ReglaEquipoError("El negocio tiene que tener al menos un administrador activo.")

    cambio_sensible = (cambio.rol is not None and cambio.rol != miembro.rol) or (
        cambio.activo is not None and cambio.activo != miembro.activo
    )
    if cambio.rol is not None:
        miembro.rol = cambio.rol
    if cambio.activo is not None:
        miembro.activo = cambio.activo
    if cambio_sensible:
        await cerrar_todas_las_sesiones(db_session, miembro)  # hace commit
    else:
        await db_session.commit()
    await db_session.refresh(miembro)
    return miembro


async def aceptar_invitacion(db_session: AsyncSession, token: str, nombre: str, password: str) -> Usuario:
    """Crea el usuario de la invitación. Raises InvitacionInvalidaError o PasswordInvalidaError."""
    password_hash = hashear_password(password)  # valida la política antes de tocar la base
    invitacion = (
        await db_session.execute(
            select(Invitacion)
            .where(Invitacion.token_hash == hashear_refresh_token(normalizar_codigo(token)))
            .with_for_update()
        )
    ).scalar_one_or_none()
    ahora = datetime.now(timezone.utc)
    if (
        invitacion is None
        or invitacion.aceptada_en is not None
        or invitacion.revocada_en is not None
        or invitacion.expira_en <= ahora
    ):
        raise InvitacionInvalidaError()
    organizacion = await db_session.get(Organizacion, invitacion.organizacion_id)
    if organizacion is None or not organizacion.activo:
        raise InvitacionInvalidaError()
    ya_existe = (
        await db_session.execute(select(Usuario).where(Usuario.email == invitacion.email))
    ).scalar_one_or_none()
    if ya_existe is not None:
        raise InvitacionInvalidaError()

    usuario = Usuario(
        id=uuid.uuid4(),
        organizacion_id=invitacion.organizacion_id,
        email=invitacion.email,
        password_hash=password_hash,
        nombre=nombre.strip()[:120],
        rol=invitacion.rol,
        activo=True,
        token_version=0,
    )
    db_session.add(usuario)
    invitacion.aceptada_en = ahora
    await db_session.commit()
    await db_session.refresh(usuario)
    return usuario
