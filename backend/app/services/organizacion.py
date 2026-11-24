"""Perfil del negocio y uso del plan (docs/004-Backend/03, secciones 3 y 6). Sin FastAPI."""

import uuid
from datetime import date

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.organizacion import Organizacion
from app.schemas.organizacion import PerfilEntrada, UsoCuota, UsoPlan
from app.services.limites import RedisError, estado_cuota
from app.services.temporadas import resumen_para_ia

VENTANA_CUOTA_SEGUNDOS = 3600


async def obtener_organizacion(db_session: AsyncSession, organizacion_id: uuid.UUID) -> Organizacion | None:
    return await db_session.get(Organizacion, organizacion_id)


async def actualizar_perfil(
    db_session: AsyncSession, organizacion_id: uuid.UUID, perfil: PerfilEntrada
) -> Organizacion | None:
    organizacion = await db_session.get(Organizacion, organizacion_id)
    if organizacion is None:
        return None
    organizacion.nombre = perfil.nombre
    organizacion.pais = perfil.pais
    organizacion.rubro = perfil.rubro
    organizacion.presupuesto_mensual = perfil.presupuesto_mensual
    organizacion.moneda = perfil.moneda
    organizacion.tipo_cambio = perfil.tipo_cambio
    organizacion.costo_envio_unitario_usd = perfil.costo_envio_unitario_usd
    organizacion.impuestos_importacion_pct = perfil.impuestos_importacion_pct
    organizacion.onboarding_completo = True
    await db_session.commit()
    await db_session.refresh(organizacion)
    return organizacion


def contexto_para_ia(organizacion: Organizacion | None) -> dict[str, str]:
    """Datos del negocio que se le pasan a la IA (siempre como datos delimitados)."""
    if organizacion is None:
        return {}
    contexto = {"País del negocio": organizacion.pais}
    if organizacion.rubro:
        contexto["Rubro del negocio"] = organizacion.rubro
    if organizacion.presupuesto_mensual is not None:
        contexto["Presupuesto mensual"] = f"{organizacion.presupuesto_mensual} {organizacion.moneda}"
    if organizacion.pais == "BO":
        contexto["Próximas fechas comerciales en Bolivia"] = resumen_para_ia(date.today())
    return contexto


async def uso_del_plan(redis: Redis, organizacion: Organizacion) -> UsoPlan:
    s = get_settings()
    limites = {"investigador": s.cuota_investigador_por_hora, "marketing": s.cuota_marketing_por_hora}
    cuotas: list[UsoCuota] = []
    try:
        for agente, limite in limites.items():
            usadas, ttl = await estado_cuota(redis, agente, str(organizacion.id))
            cuotas.append(
                UsoCuota(
                    agente=agente,
                    limite_por_hora=limite,
                    usadas=min(usadas, limite),
                    restantes=max(0, limite - usadas),
                    se_renueva_en_segundos=ttl if usadas else 0,
                )
            )
    except RedisError:
        return UsoPlan(plan=organizacion.plan, cuotas=[], disponible=False)
    return UsoPlan(plan=organizacion.plan, cuotas=cuotas)
