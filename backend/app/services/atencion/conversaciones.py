"""Conversaciones, mensajes, avisos al vendedor y derivación a una persona (docs/007-Agentes/09, secciones 3.2 y 3.5)."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.atencion import Conversacion, Mensaje, Notificacion

MAX_TEXTO = 2000


def ahora() -> datetime:
    return datetime.now(timezone.utc)


async def crear_conversacion(
    db_session: AsyncSession, organizacion_id: uuid.UUID, canal: str, contacto: str, nombre: str | None = None
) -> Conversacion:
    conversacion = Conversacion(
        id=uuid.uuid4(), organizacion_id=organizacion_id, canal=canal, contacto=contacto[:120],
        nombre_contacto=(nombre or None) and nombre[:120], atendida_por="agente",
    )
    db_session.add(conversacion)
    await db_session.flush()
    return conversacion


async def obtener_conversacion(
    db_session: AsyncSession, organizacion_id: uuid.UUID, conversacion_id: uuid.UUID, para_actualizar: bool = False
) -> Conversacion | None:
    consulta = select(Conversacion).where(
        Conversacion.id == conversacion_id, Conversacion.organizacion_id == organizacion_id, Conversacion.eliminado_en.is_(None)
    )
    if para_actualizar:
        consulta = consulta.with_for_update()
    return (await db_session.execute(consulta)).scalar_one_or_none()


async def listar_conversaciones(
    db_session: AsyncSession, organizacion_id: uuid.UUID, limite: int = 50
) -> list[Conversacion]:
    return list(
        (
            await db_session.execute(
                select(Conversacion)
                .where(Conversacion.organizacion_id == organizacion_id, Conversacion.eliminado_en.is_(None))
                .order_by(Conversacion.ultimo_mensaje_en.desc().nullslast(), Conversacion.creado_en.desc())
                .limit(limite)
            )
        ).scalars()
    )


async def agregar_mensaje(
    db_session: AsyncSession,
    conversacion: Conversacion,
    rol: str,
    texto: str,
    adjuntos: list | None = None,
    simulado: bool = False,
) -> Mensaje:
    mensaje = Mensaje(
        id=uuid.uuid4(), organizacion_id=conversacion.organizacion_id, conversacion_id=conversacion.id, rol=rol,
        texto=texto[:MAX_TEXTO], adjuntos=adjuntos or [], simulado=simulado, creado_en=ahora(),
    )
    db_session.add(mensaje)
    conversacion.ultimo_mensaje_en = mensaje.creado_en
    await db_session.flush()
    return mensaje


async def historial(db_session: AsyncSession, conversacion: Conversacion, limite: int = 200) -> list[Mensaje]:
    """Mensajes en orden cronológico (los últimos ``limite``)."""
    filas = list(
        (
            await db_session.execute(
                select(Mensaje)
                .where(Mensaje.organizacion_id == conversacion.organizacion_id, Mensaje.conversacion_id == conversacion.id)
                .order_by(Mensaje.creado_en.desc(), Mensaje.id)
                .limit(limite)
            )
        ).scalars()
    )
    return list(reversed(filas))


async def notificar(
    db_session: AsyncSession,
    organizacion_id: uuid.UUID,
    tipo: str,
    titulo: str,
    cuerpo: str | None = None,
    pedido_id: uuid.UUID | None = None,
    conversacion_id: uuid.UUID | None = None,
) -> None:
    db_session.add(
        Notificacion(
            id=uuid.uuid4(), organizacion_id=organizacion_id, tipo=tipo, titulo=titulo[:150],
            cuerpo=(cuerpo or None) and cuerpo[:500], pedido_id=pedido_id, conversacion_id=conversacion_id,
        )
    )
    await db_session.flush()


async def listar_notificaciones(
    db_session: AsyncSession, organizacion_id: uuid.UUID, limite: int = 30
) -> tuple[list[Notificacion], int]:
    filtro = (Notificacion.organizacion_id == organizacion_id, Notificacion.eliminado_en.is_(None))
    sin_leer = await db_session.scalar(
        select(func.count()).select_from(Notificacion).where(*filtro, Notificacion.leida_en.is_(None))
    ) or 0
    filas = list(
        (
            await db_session.execute(select(Notificacion).where(*filtro).order_by(Notificacion.creado_en.desc()).limit(limite))
        ).scalars()
    )
    return filas, sin_leer


async def marcar_leidas(db_session: AsyncSession, organizacion_id: uuid.UUID) -> None:
    await db_session.execute(
        update(Notificacion)
        .where(Notificacion.organizacion_id == organizacion_id, Notificacion.leida_en.is_(None))
        .values(leida_en=ahora())
    )
    await db_session.commit()


async def derivar_a_persona(db_session: AsyncSession, conversacion: Conversacion, motivo: str) -> None:
    """El agente deja de responder en esta conversación y avisa al vendedor."""
    conversacion.atendida_por = "humano"
    nombre = conversacion.nombre_contacto or conversacion.contacto
    await notificar(
        db_session, conversacion.organizacion_id, "derivacion", f"{nombre} necesita que lo atienda una persona",
        motivo[:300], conversacion_id=conversacion.id,
    )
