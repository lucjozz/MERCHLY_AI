"""Agente de Atención al Cliente: el orquestador (docs/007-Agentes/09, sección 1).

En cada mensaje:
1. Guarda el mensaje del comprador.
2. Si una persona tomó la conversación, no responde (solo guarda).
3. Le pide la respuesta al proveedor (IA real si hay clave; si no, simulado). El
   proveedor llama solo a los sub-agentes que necesita.
4. **Guardia de montos:** si la respuesta menciona un monto que no salió de los
   sub-agentes (precio, envío, total), se reemplaza por una respuesta segura y se
   avisa al vendedor. Los números nunca salen del modelo.
5. Guarda la respuesta con sus adjuntos (QR, fotos de productos).
"""

import logging
import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.atencion import Conversacion, Mensaje
from app.models.organizacion import Organizacion
from app.services.atencion.configuracion import obtener_config
from app.services.atencion.conversaciones import agregar_mensaje, historial, notificar
from app.services.atencion.dinero import montos_no_permitidos
from app.services.atencion import stock
from app.services.atencion.herramientas import Herramientas
from app.services.atencion.venta import vencer_reservas
from app.services.planes import modelo_para

logger = logging.getLogger(__name__)

RESPUESTA_SEGURA = "Dejame confirmarlo con el vendedor y te respondo en un ratito."
RESPUESTA_FALLA = "Ya te respondemos. Le avisé al vendedor para que te escriba."


@dataclass
class Resultado:
    mensajes: list[Mensaje]
    proveedor: str


async def _productos_recientes(db_session: AsyncSession, org_id: uuid.UUID, mensajes: list[Mensaje]) -> list:
    """Los productos que el agente mostró en su último mensaje: así "lo quiero" sabe de cuál se habla."""
    for m in reversed(mensajes):
        ids = [a.get("producto_id") for a in (m.adjuntos or []) if a.get("tipo") == "producto"]
        if m.rol == "agente" and ids:
            recientes = []
            for producto_id in ids[:3]:
                try:
                    p = await stock.por_id(db_session, org_id, uuid.UUID(str(producto_id)))
                except ValueError:
                    continue
                if p is not None:
                    recientes.append(p)
            return recientes
    return []


def elegir_proveedor(plan: str):
    if get_settings().openai_api_key:
        from app.services.atencion.proveedor_openai import ProveedorAtencionOpenAI

        return ProveedorAtencionOpenAI(modelo=modelo_para("atencion", plan))
    from app.services.atencion.proveedor_simulado import ProveedorAtencionSimulado

    return ProveedorAtencionSimulado()


async def procesar_mensaje(
    db_session: AsyncSession, conversacion: Conversacion, texto: str, simulado: bool, proveedor=None
) -> Resultado:
    org_id: uuid.UUID = conversacion.organizacion_id
    organizacion = await db_session.get(Organizacion, org_id)
    mensajes_previos = await historial(db_session, conversacion, limite=12)
    previos = [(m.rol, m.texto) for m in mensajes_previos]
    nuevos = [await agregar_mensaje(db_session, conversacion, "comprador", texto, simulado=simulado)]

    if conversacion.atendida_por == "humano":
        await db_session.commit()
        return Resultado(mensajes=nuevos, proveedor="ninguno")

    await vencer_reservas(db_session, org_id)
    config = await obtener_config(db_session, org_id)
    nombre_negocio = getattr(organizacion, "nombre", "el negocio")
    presentacion = config.presentacion or f"¡Hola! Soy el asistente virtual de {nombre_negocio}."
    proveedor = proveedor or elegir_proveedor(getattr(organizacion, "plan", "beta"))
    h = Herramientas(db_session, conversacion, getattr(organizacion, "moneda", "BOB") or "BOB", simulado)
    h.ultimos_productos = await _productos_recientes(db_session, org_id, mensajes_previos)

    try:
        respuesta = await proveedor.responder(texto, previos, h, presentacion, config.info_negocio or "")
    except Exception as error:  # noqa: BLE001 - nunca silencio ni datos inventados (contrato, sección 6)
        logger.warning("Fallo del proveedor de atención: %s", type(error).__name__)
        await db_session.rollback()
        conversacion = await db_session.merge(conversacion)
        nuevos = [await agregar_mensaje(db_session, conversacion, "comprador", texto, simulado=simulado)]
        await notificar(db_session, org_id, "falla_agente", "El asistente no pudo responder un mensaje",
                        texto[:300], conversacion_id=conversacion.id)
        nuevos.append(await agregar_mensaje(db_session, conversacion, "agente", RESPUESTA_FALLA, simulado=simulado))
        await db_session.commit()
        return Resultado(mensajes=nuevos, proveedor=proveedor.nombre)

    respuesta = (respuesta or "").strip() or RESPUESTA_SEGURA
    inventados = montos_no_permitidos(respuesta, h.montos_permitidos)
    if inventados:
        logger.warning("Guardia de montos: la respuesta tenía montos que no salieron de la base")
        await notificar(db_session, org_id, "guardia_montos", "El asistente quiso decir un precio que no está en tu catálogo",
                        "Se reemplazó la respuesta por una segura. Revisá la conversación.", conversacion_id=conversacion.id)
        respuesta = RESPUESTA_SEGURA
        h.adjuntos = [a for a in h.adjuntos if a.get("tipo") == "qr"]  # el QR sigue valiendo: el monto lo calculó la base

    nuevos.append(await agregar_mensaje(db_session, conversacion, "agente", respuesta, h.adjuntos, simulado=simulado))
    await db_session.commit()
    return Resultado(mensajes=nuevos, proveedor=proveedor.nombre)
