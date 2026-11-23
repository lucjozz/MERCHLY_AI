"""Envío de emails transaccionales (DEC-036). Sin FastAPI.

Proveedor: Resend (API HTTP) si hay RESEND_API_KEY. Sin proveedor:
* en ENVIRONMENT=local se escribe el contenido en el log del backend (solo
  para probar en tu PC; nunca se activa en staging/producción);
* en staging/producción no se envía nada y se registra el error.
"""

import logging
from dataclasses import dataclass

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
RESEND_URL = "https://api.resend.com/emails"


@dataclass
class Email:
    para: str
    asunto: str
    texto: str


class EmailNoEnviadoError(Exception):
    pass


async def enviar_email(email: Email, cliente: httpx.AsyncClient | None = None) -> None:
    s = get_settings()
    if not s.resend_api_key:
        if s.environment == "local":
            logger.warning(
                "EMAIL SIMULADO (solo desarrollo, sin RESEND_API_KEY) | para=%s | asunto=%s\n%s",
                email.para, email.asunto, email.texto,
            )
            return
        logger.error("No hay proveedor de email configurado (RESEND_API_KEY): no se envió '%s'", email.asunto)
        raise EmailNoEnviadoError()

    propio = cliente is None
    cliente = cliente or httpx.AsyncClient(timeout=10.0)
    try:
        respuesta = await cliente.post(
            RESEND_URL,
            headers={"Authorization": f"Bearer {s.resend_api_key}"},
            json={"from": s.email_remitente, "to": [email.para], "subject": email.asunto, "text": email.texto},
        )
        if respuesta.status_code >= 300:
            logger.error("Resend rechazó el email (%s)", respuesta.status_code)
            raise EmailNoEnviadoError()
    except httpx.HTTPError as error:
        logger.error("No se pudo contactar a Resend: %s", type(error).__name__)
        raise EmailNoEnviadoError() from error
    finally:
        if propio:
            await cliente.aclose()
