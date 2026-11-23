"""Historial de campañas (docs/004-Backend/03, sección 1). Sin FastAPI.

Todo filtrado por organización (además de RLS) y sin borrados lógicos.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campana import Campana
from app.schemas.campanas import CampanaEdicion
from app.schemas.marketing import MarketingInput, MarketingOutput


def _vigentes(organizacion_id: uuid.UUID):
    return (Campana.organizacion_id == organizacion_id, Campana.eliminado_en.is_(None))


def titulo_por_defecto(nombres_productos: list[str]) -> str:
    base = ", ".join(nombres_productos[:2]) or "Campaña"
    extra = f" y {len(nombres_productos) - 2} más" if len(nombres_productos) > 2 else ""
    return f"Campaña: {base}{extra}"[:150]


async def guardar_campana(
    db_session: AsyncSession,
    organizacion_id: uuid.UUID,
    usuario_id: uuid.UUID,
    entrada: MarketingInput,
    salida: MarketingOutput,
    nombres_productos: list[str],
) -> Campana:
    """Guarda una campaña recién generada. Devuelve la fila creada."""
    campana = Campana(
        id=uuid.uuid4(),
        organizacion_id=organizacion_id,
        creado_por=usuario_id,
        titulo=titulo_por_defecto(nombres_productos),
        productos_candidato_ids=[str(i) for i in entrada.productos_candidato_ids],
        canales=[c.value for c in entrada.canales_objetivo],
        tono=entrada.tono.value,
        idioma=entrada.idioma_destino,
        modelo=salida.metadata.modelo,
        contenido={
            "angulos": salida.angulos_de_campana,
            "copy_por_canal": {
                canal.value: [v.model_dump() for v in variantes]
                for canal, variantes in salida.copy_por_canal.items()
            },
            "publico_objetivo": salida.publico_objetivo_sugerido,
            "advertencias": salida.advertencias,
        },
    )
    db_session.add(campana)
    await db_session.commit()
    return campana


async def listar_campanas(
    db_session: AsyncSession, organizacion_id: uuid.UUID, pagina: int, tamano_pagina: int
) -> tuple[list[Campana], int]:
    total = await db_session.scalar(select(func.count()).select_from(Campana).where(*_vigentes(organizacion_id)))
    consulta = (
        select(Campana)
        .where(*_vigentes(organizacion_id))
        .order_by(Campana.creado_en.desc(), Campana.id)
        .offset((pagina - 1) * tamano_pagina)
        .limit(tamano_pagina)
    )
    return list((await db_session.execute(consulta)).scalars().all()), total or 0


async def obtener_campana(
    db_session: AsyncSession, organizacion_id: uuid.UUID, campana_id: uuid.UUID, para_actualizar: bool = False
) -> Campana | None:
    consulta = select(Campana).where(Campana.id == campana_id, *_vigentes(organizacion_id))
    if para_actualizar:
        consulta = consulta.with_for_update()
    return (await db_session.execute(consulta)).scalar_one_or_none()


async def editar_campana(
    db_session: AsyncSession, organizacion_id: uuid.UUID, campana_id: uuid.UUID, cambios: CampanaEdicion
) -> Campana | None:
    campana = await obtener_campana(db_session, organizacion_id, campana_id, para_actualizar=True)
    if campana is None:
        return None
    contenido = dict(campana.contenido)
    if cambios.titulo is not None:
        campana.titulo = cambios.titulo
    if cambios.angulos is not None:
        contenido["angulos"] = cambios.angulos
    if cambios.copy_por_canal is not None:
        contenido["copy_por_canal"] = {
            canal.value: [v.model_dump() for v in variantes] for canal, variantes in cambios.copy_por_canal.items()
        }
    if cambios.publico_objetivo is not None:
        contenido["publico_objetivo"] = cambios.publico_objetivo
    campana.contenido = contenido  # reasignar: JSONB no detecta mutaciones in-place
    campana.editada = True
    await db_session.commit()
    await db_session.refresh(campana)
    return campana


async def eliminar_campana(db_session: AsyncSession, organizacion_id: uuid.UUID, campana_id: uuid.UUID) -> bool:
    campana = await obtener_campana(db_session, organizacion_id, campana_id, para_actualizar=True)
    if campana is None:
        return False
    campana.eliminado_en = datetime.now(timezone.utc)
    await db_session.commit()
    return True
