"""Endpoints de productos candidatos (todos exigen autenticación, 013-04)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import ROLES_BORRADO, TODOS_LOS_ROLES, requiere_rol
from app.models.usuario import Usuario
from app.schemas.productos_candidatos import (
    TAMANO_PAGINA_MAXIMO,
    EstadoProducto,
    ProductoCandidatoDetalle,
    ProductosCandidatosListado,
)
from app.services.consulta_productos_candidatos import (
    eliminar_producto_candidato,
    listar_productos_candidatos,
    obtener_producto_candidato_por_id,
)

router = APIRouter(prefix="/productos-candidatos", tags=["productos-candidatos"])

NO_ENCONTRADO = "No existe ese producto."


@router.get("", response_model=ProductosCandidatosListado)
async def listar_productos(
    pagina: int = Query(default=1, ge=1, le=10_000),
    tamano_pagina: int = Query(default=20, ge=1, le=TAMANO_PAGINA_MAXIMO),
    categoria: str | None = Query(default=None, max_length=120),
    estado: EstadoProducto | None = None,
    mercado_objetivo: str | None = Query(default=None, min_length=2, max_length=2),
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> ProductosCandidatosListado:
    """Lista los productos de la organización del usuario."""
    productos, total = await listar_productos_candidatos(
        db_session=db_session,
        organizacion_id=usuario.organizacion_id,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
        categoria=categoria,
        estado=estado,
        mercado_objetivo=mercado_objetivo.upper() if mercado_objetivo else None,
    )
    return ProductosCandidatosListado(
        productos=productos, total=total, pagina=pagina, tamano_pagina=tamano_pagina
    )


@router.get("/{producto_id}", response_model=ProductoCandidatoDetalle)
async def obtener_producto(
    producto_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> ProductoCandidatoDetalle:
    """Detalle de un producto. 404 si no existe o es de otra organización."""
    producto = await obtener_producto_candidato_por_id(
        db_session, usuario.organizacion_id, producto_id
    )
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_ENCONTRADO)
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(
    producto_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*ROLES_BORRADO)),
) -> Response:
    """Borrado lógico. Solo admin_principal y responsable_negocio."""
    if not await eliminar_producto_candidato(db_session, usuario.organizacion_id, producto_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_ENCONTRADO)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
