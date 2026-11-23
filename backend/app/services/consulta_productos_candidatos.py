"""Consultas de productos candidatos. Sin FastAPI.

Toda consulta filtra por organización (además de RLS en la base) y excluye
los borrados lógicos (``eliminado_en IS NULL``). Ver 013-04, secciones 2 y 6.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.producto_candidato import ProductoCandidato
from app.schemas.productos_candidatos import EstadoProducto


def _vigentes(organizacion_id: uuid.UUID):
    return (
        ProductoCandidato.organizacion_id == organizacion_id,
        ProductoCandidato.eliminado_en.is_(None),
    )


async def listar_productos_candidatos(
    db_session: AsyncSession,
    organizacion_id: uuid.UUID,
    pagina: int = 1,
    tamano_pagina: int = 20,
    categoria: str | None = None,
    estado: EstadoProducto | None = None,
    mercado_objetivo: str | None = None,
) -> tuple[list[ProductoCandidato], int]:
    """Lista productos de la organización, con filtros y paginación.

    ``pagina`` y ``tamano_pagina`` llegan ya validados (>= 1, <= 100).
    """
    condiciones = list(_vigentes(organizacion_id))
    if categoria:
        condiciones.append(ProductoCandidato.categoria == categoria)
    if estado:
        condiciones.append(ProductoCandidato.estado == estado.value)
    if mercado_objetivo:
        condiciones.append(ProductoCandidato.mercado_objetivo == mercado_objetivo)

    total = await db_session.scalar(
        select(func.count()).select_from(ProductoCandidato).where(*condiciones)
    )
    consulta_pagina = (
        select(ProductoCandidato)
        .where(*condiciones)
        .order_by(ProductoCandidato.creado_en.desc(), ProductoCandidato.id)
        .offset((pagina - 1) * tamano_pagina)
        .limit(tamano_pagina)
    )
    productos = list((await db_session.execute(consulta_pagina)).scalars().all())
    return productos, total or 0


async def obtener_producto_candidato_por_id(
    db_session: AsyncSession,
    organizacion_id: uuid.UUID,
    producto_candidato_id: uuid.UUID,
    para_actualizar: bool = False,
) -> ProductoCandidato | None:
    """Busca un producto vigente de la organización. None si no existe o es
    de otra organización (el endpoint responde 404 en ambos casos: IDOR).

    Args:
        para_actualizar: bloquea la fila (``SELECT ... FOR UPDATE``) hasta
            el fin de la transacción, para decisiones concurrentes.
    """
    consulta = select(ProductoCandidato).where(
        ProductoCandidato.id == producto_candidato_id, *_vigentes(organizacion_id)
    )
    if para_actualizar:
        consulta = consulta.with_for_update()
    return (await db_session.execute(consulta)).scalar_one_or_none()


async def eliminar_producto_candidato(
    db_session: AsyncSession, organizacion_id: uuid.UUID, producto_candidato_id: uuid.UUID
) -> bool:
    """Borrado LÓGICO (013-04, sección 6.2). True si se borró."""
    producto = await obtener_producto_candidato_por_id(
        db_session, organizacion_id, producto_candidato_id, para_actualizar=True
    )
    if producto is None:
        return False
    producto.eliminado_en = datetime.now(timezone.utc)
    await db_session.commit()
    return True
