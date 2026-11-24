"""Endpoints del inventario y del catálogo público (docs/007-Agentes/08, secciones 2 y 3.3).

Leer: los 4 roles. Editar, borrar, fotos e importar: admin principal y
responsable de negocio. Todo cambio queda en la bitácora de auditoría.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import ROLES_BORRADO, TODOS_LOS_ROLES, contexto_peticion, requiere_rol
from app.models.usuario import Usuario
from app.schemas.inventario import (
    FotoEntrada,
    FotoSalida,
    ImportarConfirmacion,
    ImportarResultado,
    ImportarVistaPrevia,
    ImportarVistaPreviaEntrada,
    InventarioListado,
    ItemCatalogoPublico,
    ProductoInventario,
    ProductoInventarioEdicion,
    ProductoInventarioEntrada,
)
from app.services import inventario
from app.services.auditoria import registrar_evento
from app.services.imagenes import ImagenInvalidaError, decodificar_base64, recodificar
from app.services.importar_inventario import MAX_BYTES_ARCHIVO, ArchivoInvalidoError, vista_previa

router = APIRouter(prefix="/inventario", tags=["inventario"])
NO_ENCONTRADO = "No existe ese producto en tu inventario."
EDITORES = ROLES_BORRADO  # admin principal y responsable de negocio


def _404() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_ENCONTRADO)


@router.get("", response_model=InventarioListado)
async def listar(
    pagina: int = Query(default=1, ge=1, le=10_000),
    tamano_pagina: int = Query(default=50, ge=1, le=100),
    buscar: str | None = Query(default=None, max_length=100),
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> InventarioListado:
    productos, total, resumen = await inventario.listar_inventario(
        db_session, usuario.organizacion_id, pagina, tamano_pagina, buscar
    )
    return InventarioListado(productos=productos, total=total, pagina=pagina, tamano_pagina=tamano_pagina, resumen=resumen)


@router.get("/catalogo-publico", response_model=list[ItemCatalogoPublico])
async def catalogo_publico(
    buscar: str | None = Query(default=None, max_length=100),
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> list[ItemCatalogoPublico]:
    """La cara pública: exactamente lo que ve la IA."""
    return await inventario.catalogo_publico(db_session, usuario.organizacion_id, buscar)


@router.get("/fotos/{foto_id}")
async def ver_foto(
    foto_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> Response:
    foto = await inventario.obtener_foto(db_session, usuario.organizacion_id, foto_id)
    if foto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe esa foto.")
    return Response(content=foto.contenido, media_type="image/webp", headers={"Cache-Control": "private, max-age=3600"})


@router.post("/importar/vista-previa", response_model=ImportarVistaPrevia)
async def importar_vista_previa(
    entrada: ImportarVistaPreviaEntrada,
    _: Usuario = Depends(requiere_rol(*EDITORES)),
) -> ImportarVistaPrevia:
    """Lee el archivo y devuelve lo que entendió. NO guarda nada."""
    try:
        datos = decodificar_base64(entrada.contenido_base64, MAX_BYTES_ARCHIVO)
        return vista_previa(entrada.nombre_archivo, datos)
    except (ImagenInvalidaError, ArchivoInvalidoError) as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error))


@router.post("/importar", response_model=ImportarResultado, status_code=status.HTTP_201_CREATED)
async def importar_confirmar(
    entrada: ImportarConfirmacion,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> ImportarResultado:
    """Guarda las filas que el dueño revisó y confirmó."""
    creados = await inventario.crear_varios(db_session, usuario.organizacion_id, entrada.productos)
    await registrar_evento(
        "inventario_importado", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
        detalle={"productos": creados}, **contexto_peticion(request),
    )
    return ImportarResultado(creados=creados)


@router.post("", response_model=ProductoInventario, status_code=status.HTTP_201_CREATED)
async def crear(
    entrada: ProductoInventarioEntrada,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> ProductoInventario:
    producto = await inventario.crear(db_session, usuario.organizacion_id, entrada)
    await registrar_evento(
        "inventario_creado", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
        objetivo_tipo="inventario", objetivo_id=producto.id, detalle={"nombre": producto.nombre},
        **contexto_peticion(request),
    )
    return producto


@router.get("/{producto_id}", response_model=ProductoInventario)
async def detalle(
    producto_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> ProductoInventario:
    producto = await inventario.obtener(db_session, usuario.organizacion_id, producto_id)
    if producto is None:
        raise _404()
    return await inventario.obtener_vista(db_session, usuario.organizacion_id, producto)


@router.patch("/{producto_id}", response_model=ProductoInventario)
async def editar(
    producto_id: uuid.UUID,
    cambios: ProductoInventarioEdicion,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> ProductoInventario:
    try:
        resultado = await inventario.editar(db_session, usuario.organizacion_id, producto_id, cambios)
    except inventario.StockMenorQueReservadoError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Hay unidades reservadas por pedidos sin confirmar: el stock no puede ser menor que eso.",
        )
    if resultado is None:
        raise _404()
    producto, cambios_hechos = resultado
    if cambios_hechos:
        await registrar_evento(
            "inventario_editado", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
            objetivo_tipo="inventario", objetivo_id=producto_id, detalle={"nombre": producto.nombre, **cambios_hechos},
            **contexto_peticion(request),
        )
    return producto


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar(
    producto_id: uuid.UUID,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> Response:
    if not await inventario.eliminar(db_session, usuario.organizacion_id, producto_id):
        raise _404()
    await registrar_evento(
        "inventario_borrado", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
        objetivo_tipo="inventario", objetivo_id=producto_id, **contexto_peticion(request),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{producto_id}/fotos", response_model=FotoSalida, status_code=status.HTTP_201_CREATED)
async def subir_foto(
    producto_id: uuid.UUID,
    entrada: FotoEntrada,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> FotoSalida:
    try:
        contenido = recodificar(decodificar_base64(entrada.imagen_base64, 800 * 1024))
    except ImagenInvalidaError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error))
    try:
        foto = await inventario.agregar_foto(db_session, usuario.organizacion_id, producto_id, contenido)
    except inventario.DemasiadasFotosError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cada producto puede tener hasta {inventario.MAX_FOTOS_POR_PRODUCTO} fotos.",
        )
    if foto is None:
        raise _404()
    return foto


@router.delete("/{producto_id}/fotos/{foto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_foto(
    producto_id: uuid.UUID,
    foto_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> Response:
    if not await inventario.borrar_foto(db_session, usuario.organizacion_id, producto_id, foto_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe esa foto.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
