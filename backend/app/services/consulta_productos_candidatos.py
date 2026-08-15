import uuid 
from  sqlalchemy import func, select 
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.producto_candidato import ProductoCandidato
from app.schemas.productos_candidatos import EstadoProducto

async def listar_productos_candidatos(
        db_session: AsyncSession,
        pagina: int = 1,
        tamano_pagina: int = 20,
        categoria: str | None = None,
        estado: EstadoProducto | None = None,
        mercado_objetivo: str | None = None,
) -> tuple[list[ProductoCandidato], int]: 
    """Lista productos candidatos, con filtros opcionales y paginación.

    Args:
        db_session: sesión async de SQLAlchemy.
        pagina: número de página, empezando en 1.
        tamano_pagina: cantidad de resultados por página (máx. 100).
        categoria: filtro opcional por categoría exacta.
        estado: filtro opcional por estado.
        mercado_objetivo: filtro opcional por mercado objetivo.

    Returns:
        tuple[list[ProductoCandidato], int]: los productos de esta página,
        y el total de productos que cumplen el filtro (sin paginar).
    """
    condiciones = []
    if categoria:
        condiciones.append(ProductoCandidato.categoria == categoria)
    if estado:
        condiciones.append(ProductoCandidato.estado == estado.value)
    if mercado_objetivo:
        condiciones.append(ProductoCandidato.mercado_objetivo == mercado_objetivo)

    consulta_total = select(func.count()).select_from(ProductoCandidato).where(*condiciones)
    total = await db_session.scalar(consulta_total)

    desplazamiento = (pagina - 1) * tamano_pagina
    consulta_pagina = (
        select(ProductoCandidato)
        .where(*condiciones)
        .order_by(ProductoCandidato.creado_en.desc())
        .offset(desplazamiento)
        .limit(tamano_pagina)
    )
    resultado = await db_session.execute(consulta_pagina)
    productos = list(resultado.scalars().all())

    return productos, total or 0
async def obtener_producto_candidato_por_id(db_session: AsyncSession, producto_candidato_id: uuid.UUID) -> ProductoCandidato | None:
    """Busca un producto candidato por su ID.

    Args:
        db_session: sesión async de SQLAlchemy.
        producto_id: el UUID del producto a buscar.

    Returns:
        ProductoCandidato | None: el producto si existe, o ``None`` si no
        hay ningún producto con ese ID (el endpoint decide qué hacer con
        eso — típicamente, responder 404).
    """
    consulta = select(ProductoCandidato).where(ProductoCandidato.id == producto_candidato_id)
    resultado = await db_session.execute(consulta)
    return resultado.scalar_one_or_none()