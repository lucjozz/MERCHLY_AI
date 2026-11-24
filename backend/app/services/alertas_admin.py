"""Aviso de inicio de sesión del administrador desde una IP nueva (docs/013-Seguridad/09, sección 9).

Si la cuenta de un admin entra desde una IP que no usó en los últimos 90 días,
se deja un aviso en la app y se le manda un email: si no fue él, sabe que
tiene que cambiar la contraseña y cerrar todas las sesiones. Nunca bloquea el
login ni lanza errores (si falla, solo se registra).
"""

import logging
import uuid

from sqlalchemy import func, select

from app.models.evento_auditoria import EventoAuditoria
from app.services.auditoria import registrar_evento

logger = logging.getLogger(__name__)
LOGINS = ("login_ok", "login_google")
DIAS = 90


async def avisar_si_ip_nueva(usuario_id: uuid.UUID, organizacion_id: uuid.UUID, email: str, ip: str | None,
                             user_agent: str | None, fabrica=None) -> bool:
    """True si era una IP nueva (y se avisó). Llamar DESPUÉS de registrar el login."""
    if not ip or ip == "desconocida":
        return False
    try:
        from app.core.database import async_session_factory, fijar_organizacion
        from app.services.atencion.conversaciones import notificar

        async with (fabrica or async_session_factory)() as s:
            await fijar_organizacion(s, organizacion_id)
            filtro = (
                EventoAuditoria.usuario_id == usuario_id,
                EventoAuditoria.accion.in_(LOGINS),
                EventoAuditoria.creado_en > func.now() - func.make_interval(0, 0, 0, DIAS),
            )
            total = await s.scalar(select(func.count()).select_from(EventoAuditoria).where(*filtro)) or 0
            misma_ip = await s.scalar(
                select(func.count()).select_from(EventoAuditoria).where(*filtro, EventoAuditoria.ip == ip)
            ) or 0
            # total <= 1: es el primer login registrado (el de recién), no hay con qué comparar.
            if total <= 1 or misma_ip > 1:
                return False
            await notificar(
                s, organizacion_id, "seguridad", "Tu cuenta de administrador entró desde una conexión nueva",
                f"IP {ip}. Si no fuiste vos, cambiá tu contraseña y cerrá todas las sesiones en Configuración.",
            )
            await s.commit()
        await registrar_evento("login_ip_nueva", organizacion_id=organizacion_id, usuario_id=usuario_id, ip=ip,
                               user_agent=user_agent)
        from app.services.email import Email, enviar_email

        await enviar_email(Email(
            para=email,
            asunto="MERCHLY AI: tu cuenta entró desde una conexión nueva",
            texto=(
                f"Tu cuenta de administrador inició sesión desde la IP {ip}.\n\n"
                "Si fuiste vos, no tenés que hacer nada. Si NO fuiste vos: entrá, cambiá tu contraseña "
                "y tocá «Cerrar todas las sesiones» en Configuración. Te recomendamos activar la verificación en dos pasos."
            ),
        ))
        return True
    except Exception as error:  # noqa: BLE001 - un aviso nunca puede romper el login
        logger.warning("No se pudo avisar el login desde IP nueva: %s", type(error).__name__)
        return False
