"""Sub-agente Envíos (docs/007-Agentes/09, sección 3.6).

Fase A: tarifas por zona que carga el dueño. Fase B: cotización con la API de
Yango (``check-price``) si el negocio conecta su cuenta de empresa; las zonas
quedan como respaldo. Siempre es un costo ESTIMADO.
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.atencion import ZonaEnvio
from app.services.atencion.configuracion import listar_zonas
from app.services.atencion.stock import normalizar


def elegir_zona(texto: str, zonas: list[ZonaEnvio]) -> ZonaEnvio | None:
    """La zona mencionada en el texto (la de nombre más largo si hay varias)."""
    normal = f" {normalizar(texto)} "
    candidatas = [z for z in zonas if f" {normalizar(z.nombre).strip()} " in normal]
    return max(candidatas, key=lambda z: len(z.nombre)) if candidatas else None


async def cotizar(db_session: AsyncSession, organizacion_id: uuid.UUID, texto_zona: str | None) -> dict:
    """{"zona": ZonaEnvio} si la encontró; {"zonas": [...]} para que el comprador elija; {} si no hay tarifas."""
    zonas = await listar_zonas(db_session, organizacion_id)
    if not zonas:
        return {}
    zona = elegir_zona(texto_zona or "", zonas) if texto_zona else None
    return {"zona": zona} if zona else {"zonas": zonas}
