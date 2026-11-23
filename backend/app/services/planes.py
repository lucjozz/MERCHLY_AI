"""Planes de organización y modelo de IA según el plan (docs/007-Agentes/07). Sin FastAPI."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.organizacion import Organizacion

PLANES = ("beta", "emprendedor", "negocio")
AGENTES = ("investigador", "marketing")


def modelo_para(agente: str, plan: str) -> str:
    """Modelo configurado para un agente en un plan. Plan desconocido -> beta."""
    if agente not in AGENTES:
        raise ValueError(f"Agente desconocido: {agente}")
    plan = plan if plan in PLANES else "beta"
    return str(getattr(get_settings(), f"modelo_{agente}_{plan}"))


async def plan_de_organizacion(db_session: AsyncSession, organizacion_id: uuid.UUID) -> str:
    organizacion = await db_session.get(Organizacion, organizacion_id)
    plan = getattr(organizacion, "plan", None)
    return plan if plan in PLANES else "beta"
