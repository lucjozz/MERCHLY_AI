import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.productos_candidatos import EstadoProducto, ProductoCandidatoDetalle, ProductosCandidatosListado
from app.services.consulta_productos_candidatos import (
    listar_productos_candidatos,
    obtener_producto_candidato_por_id,
)

router = APIRouter(prefix="/productos-candidatos", tags=["productos-candidatos"])
@router.get(
    "",
    response_model=ProductosCandidatosListado,
    status_code=status.HTTP_200_OK,
)
async def listar_productos(
    pagina: int = 1,
    tamano_pagina: int = 20,
    categoria: str | None = None,
    estado: EstadoProducto | None = None,
    mercado_objetivo: str | None = None,
    db_session: AsyncSession = Depends(get_db_session),
) -> ProductosCandidatosListado:
    """Lista productos candidatos, con filtros opcionales y paginación.

    Args:
        pagina: número de página (empieza en 1).
        tamano_pagina: cantidad de resultados por página (máx. 100).
        categoria: filtro opcional por categoría exacta.
        estado: filtro opcional por estado (candidato/en_catalogo/descartado).
        mercado_objetivo: filtro opcional por mercado objetivo.
        db_session: sesión de base de datos inyectada, usada solo para lectura.

    Returns:
        ProductosCandidatosListado: la página de resultados pedida.
    """
    productos, total = await listar_productos_candidatos(
        db_session=db_session,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
        categoria=categoria,
        estado=estado,
        mercado_objetivo=mercado_objetivo,
    )

    return ProductosCandidatosListado(
        productos=productos,
        total=total,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
    )
@router.get(
    "/{producto_id}",
    response_model=ProductoCandidatoDetalle,
    status_code=status.HTTP_200_OK,
)
async def obtener_producto(
    producto_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
) -> ProductoCandidatoDetalle:
    """Busca un producto candidato específico por su ID.

    Args:
        producto_id: el UUID del producto a buscar (viene de la URL).
        db_session: sesión de base de datos inyectada, usada solo para lectura.

    Returns:
        ProductoCandidatoDetalle: el producto encontrado.

    Raises:
        HTTPException: 404 si no existe ningún producto con ese ID.
    """
    producto = await obtener_producto_candidato_por_id(
        db_session=db_session, producto_candidato_id=producto_id
    )

    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe un producto candidato con id {producto_id}.",
        )

    return producto