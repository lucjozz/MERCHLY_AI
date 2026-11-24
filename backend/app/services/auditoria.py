"""Bitácora de auditoría (docs/013-Seguridad/06, DEC-037). Sin FastAPI.

* Se registra en una sesión de base PROPIA (independiente de la del
  request), así un evento nunca queda atado a un rollback del request ni
  hace commit de cambios ajenos.
* Si registrar falla, la acción del usuario no se corta: se loguea el error.
* El detalle se filtra: nunca contraseñas, tokens, códigos ni links.
"""

import hashlib
import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.evento_auditoria import EventoAuditoria

logger = logging.getLogger(__name__)

ACCIONES = frozenset({
    "login_ok", "login_fallido", "login_google", "registro_google", "logout", "sesiones_cerradas",
    "password_restablecimiento_pedido", "password_restablecida",
    "invitacion_creada", "invitacion_revocada", "invitacion_aceptada",
    "rol_cambiado", "usuario_desactivado", "usuario_reactivado",
    "producto_borrado", "campana_borrada", "perfil_actualizado",
    "inventario_creado", "inventario_editado", "inventario_borrado", "inventario_importado",
    "atencion_configurada", "qr_subido", "qr_borrado", "pago_confirmado", "pago_rechazado", "pedido_entregado", "pedido_cancelado",
})
_CLAVES_PROHIBIDAS = ("password", "token", "codigo", "secret", "link", "enlace", "authorization")


def hash_corto(valor: str) -> str:
    """Identifica un valor (ej. un email intentado) sin guardarlo en claro."""
    return hashlib.sha256(valor.strip().lower().encode("utf-8")).hexdigest()[:16]


def _limpiar_detalle(detalle: dict | None) -> dict:
    limpio = {}
    for clave, valor in (detalle or {}).items():
        if any(p in clave.lower() for p in _CLAVES_PROHIBIDAS):
            continue
        limpio[str(clave)[:40]] = valor if isinstance(valor, (int, float, bool)) or valor is None else str(valor)[:200]
    return limpio


async def registrar_evento(
    accion: str,
    *,
    organizacion_id: uuid.UUID | None = None,
    usuario_id: uuid.UUID | None = None,
    objetivo_tipo: str | None = None,
    objetivo_id: uuid.UUID | None = None,
    detalle: dict | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
) -> None:
    """Registra un evento. Nunca lanza excepciones hacia el llamador."""
    if accion not in ACCIONES:
        logger.error("Acción de auditoría desconocida: %s", accion)
        return
    evento = EventoAuditoria(
        id=uuid.uuid4(),
        organizacion_id=organizacion_id,
        usuario_id=usuario_id,
        accion=accion,
        objetivo_tipo=objetivo_tipo,
        objetivo_id=objetivo_id,
        detalle=_limpiar_detalle(detalle),
        ip=(ip or None) and ip[:64],
        user_agent=(user_agent or None) and user_agent[:200],
    )
    try:
        await _guardar(evento)
    except Exception as error:  # noqa: BLE001 - la auditoría no puede tumbar la acción
        logger.error("No se pudo registrar el evento de auditoría '%s': %s", accion, type(error).__name__)


async def guardar_en_base(evento: EventoAuditoria) -> None:
    from app.core.database import async_session_factory  # import local: evita ciclos

    async with async_session_factory() as sesion:
        sesion.add(evento)
        await sesion.commit()


# Punto de reemplazo: los tests unitarios lo cambian por un registro en memoria.
_guardar = guardar_en_base


async def listar_eventos(
    db_session: AsyncSession, organizacion_id: uuid.UUID, pagina: int, tamano_pagina: int, accion: str | None = None
) -> tuple[list[EventoAuditoria], int]:
    condiciones = [EventoAuditoria.organizacion_id == organizacion_id]
    if accion:
        condiciones.append(EventoAuditoria.accion == accion)
    total = await db_session.scalar(select(func.count()).select_from(EventoAuditoria).where(*condiciones))
    consulta = (
        select(EventoAuditoria)
        .where(*condiciones)
        .order_by(EventoAuditoria.creado_en.desc(), EventoAuditoria.id)
        .offset((pagina - 1) * tamano_pagina)
        .limit(tamano_pagina)
    )
    return list((await db_session.execute(consulta)).scalars().all()), total or 0
