"""Endpoints del Agente de Atención al Cliente (docs/007-Agentes/09).

* Simulador, conversaciones y avisos: los 4 roles (atender es tarea operativa).
* Configuración, QR, zonas y decisiones sobre pedidos (confirmar pago, etc.):
  admin principal y responsable de negocio.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.cuotas import aplicar_cuota
from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.dependencias import ROLES_BORRADO, TODOS_LOS_ROLES, contexto_peticion, requiere_rol
from app.core.redis import get_redis_client
from app.models.atencion import ESTADOS_PEDIDO
from app.models.usuario import Usuario
from app.schemas.atencion import (
    ConfigEntrada,
    ConfigSalida,
    ConversacionCambio,
    ConversacionDetalle,
    ConversacionResumen,
    MensajeSalida,
    MensajeVendedorEntrada,
    NotificacionesListado,
    PedidoSalida,
    QrEntrada,
    QrSalida,
    SimuladorEntrada,
    SimuladorSalida,
    ZonaSalida,
    ZonasEntrada,
)
from app.services.atencion import configuracion, conversaciones, venta
from app.services.atencion.orquestador import procesar_mensaje
from app.services.auditoria import registrar_evento
from app.services.imagenes import ImagenInvalidaError, decodificar_base64, recodificar
from app.services.planes import plan_de_organizacion, plan_incluye_atencion

router = APIRouter(prefix="/atencion", tags=["atencion"])
EDITORES = ROLES_BORRADO
NO_CONVERSACION = "No existe esa conversación."
NO_PEDIDO = "No existe ese pedido."


async def _exigir_plan(db_session: AsyncSession, usuario: Usuario) -> None:
    if not plan_incluye_atencion(await plan_de_organizacion(db_session, usuario.organizacion_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tu plan no incluye el asistente de atención al cliente.")


# ------------------------------------------------------------------ configuración


@router.get("/config", response_model=ConfigSalida)
async def ver_config(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> ConfigSalida:
    c = await configuracion.obtener_config(db_session, usuario.organizacion_id)
    plan = await plan_de_organizacion(db_session, usuario.organizacion_id)
    return ConfigSalida(
        encendido=c.encendido, completar_ventas=c.completar_ventas, presentacion=c.presentacion,
        info_negocio=c.info_negocio, minutos_reserva=c.minutos_reserva,
        proveedor="openai" if get_settings().openai_api_key else "simulado", plan_incluye=plan_incluye_atencion(plan),
    )


@router.put("/config", response_model=ConfigSalida)
async def guardar_config(
    entrada: ConfigEntrada,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> ConfigSalida:
    await _exigir_plan(db_session, usuario)
    await configuracion.guardar_config(db_session, usuario.organizacion_id, entrada.model_dump())
    await registrar_evento(
        "atencion_configurada", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
        detalle={"encendido": entrada.encendido, "completar_ventas": entrada.completar_ventas}, **contexto_peticion(request),
    )
    return await ver_config(db_session, usuario)


@router.get("/qr", response_model=list[QrSalida])
async def listar_qr(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> list[QrSalida]:
    return [QrSalida(id=q.id, etiqueta=q.etiqueta) for q in await configuracion.listar_qr(db_session, usuario.organizacion_id)]


@router.post("/qr", response_model=QrSalida, status_code=status.HTTP_201_CREATED)
async def subir_qr(
    entrada: QrEntrada,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> QrSalida:
    try:
        contenido = recodificar(decodificar_base64(entrada.imagen_base64, 800 * 1024), formato="PNG", lado_maximo=1200)
    except ImagenInvalidaError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error))
    try:
        qr_id, etiqueta = await configuracion.agregar_qr(db_session, usuario.organizacion_id, entrada.etiqueta, contenido)
    except configuracion.DemasiadosQrError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Podés tener hasta {configuracion.MAX_QR} QR.")
    await registrar_evento(
        "qr_subido", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id, objetivo_tipo="qr",
        objetivo_id=qr_id, detalle={"etiqueta": etiqueta}, **contexto_peticion(request),
    )
    return QrSalida(id=qr_id, etiqueta=etiqueta)


@router.get("/qr/{qr_id}/imagen")
async def ver_qr(
    qr_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> Response:
    qr = await configuracion.obtener_qr(db_session, usuario.organizacion_id, qr_id)
    if qr is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe ese QR.")
    return Response(content=qr.contenido, media_type="image/png", headers={"Cache-Control": "private, max-age=3600"})


@router.delete("/qr/{qr_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar_qr(
    qr_id: uuid.UUID,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> Response:
    if not await configuracion.borrar_qr(db_session, usuario.organizacion_id, qr_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No existe ese QR.")
    await registrar_evento(
        "qr_borrado", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id, objetivo_tipo="qr",
        objetivo_id=qr_id, **contexto_peticion(request),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/zonas", response_model=list[ZonaSalida])
async def listar_zonas(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> list[ZonaSalida]:
    return await configuracion.listar_zonas(db_session, usuario.organizacion_id)


@router.put("/zonas", response_model=list[ZonaSalida])
async def guardar_zonas(
    entrada: ZonasEntrada,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> list[ZonaSalida]:
    nombres = [z.nombre.lower() for z in entrada.zonas]
    if len(set(nombres)) != len(nombres):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Hay zonas repetidas.")
    return await configuracion.reemplazar_zonas(
        db_session, usuario.organizacion_id, [(z.nombre, z.precio, z.notas) for z in entrada.zonas]
    )


# ------------------------------------------------------------------ simulador y conversaciones


@router.post("/simulador", response_model=SimuladorSalida)
async def simulador(
    entrada: SimuladorEntrada,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> SimuladorSalida:
    """Escribís como si fueras un comprador y el agente responde de verdad (con tu catálogo), marcado como simulado."""
    await _exigir_plan(db_session, usuario)
    await aplicar_cuota(redis, "atencion_simulador", usuario.organizacion_id, get_settings().cuota_atencion_simulador_hora)
    if entrada.conversacion_id is None:
        conversacion = await conversaciones.crear_conversacion(
            db_session, usuario.organizacion_id, "simulador", f"prueba-{uuid.uuid4().hex[:6]}", entrada.nombre or "Comprador de prueba"
        )
        await db_session.commit()  # que exista aunque el proveedor falle
    else:
        conversacion = await conversaciones.obtener_conversacion(db_session, usuario.organizacion_id, entrada.conversacion_id)
        if conversacion is None or conversacion.canal != "simulador":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_CONVERSACION)
    await aplicar_cuota(redis, f"atencion_conv:{conversacion.id}", usuario.organizacion_id,
                        get_settings().cuota_atencion_por_conversacion_hora)
    resultado = await procesar_mensaje(db_session, conversacion, entrada.texto, simulado=True)
    return SimuladorSalida(
        conversacion_id=conversacion.id, atendida_por=conversacion.atendida_por, proveedor=resultado.proveedor,
        mensajes=[MensajeSalida.model_validate(m) for m in resultado.mensajes],
    )


@router.get("/conversaciones", response_model=list[ConversacionResumen])
async def listar_conversaciones(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> list[ConversacionResumen]:
    return await conversaciones.listar_conversaciones(db_session, usuario.organizacion_id)


@router.get("/conversaciones/{conversacion_id}", response_model=ConversacionDetalle)
async def ver_conversacion(
    conversacion_id: uuid.UUID,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> ConversacionDetalle:
    conversacion = await conversaciones.obtener_conversacion(db_session, usuario.organizacion_id, conversacion_id)
    if conversacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_CONVERSACION)
    mensajes = await conversaciones.historial(db_session, conversacion)
    return ConversacionDetalle(
        **ConversacionResumen.model_validate(conversacion).model_dump(),
        mensajes=[MensajeSalida.model_validate(m) for m in mensajes],
    )


@router.patch("/conversaciones/{conversacion_id}", response_model=ConversacionResumen)
async def cambiar_conversacion(
    conversacion_id: uuid.UUID,
    cambio: ConversacionCambio,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> ConversacionResumen:
    """Tomar la conversación (el agente deja de responder) o devolvérsela al agente."""
    conversacion = await conversaciones.obtener_conversacion(db_session, usuario.organizacion_id, conversacion_id, True)
    if conversacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_CONVERSACION)
    conversacion.atendida_por = cambio.atendida_por
    await db_session.commit()
    await db_session.refresh(conversacion)
    return conversacion


@router.post("/conversaciones/{conversacion_id}/mensajes", response_model=MensajeSalida, status_code=status.HTTP_201_CREATED)
async def responder_como_vendedor(
    conversacion_id: uuid.UUID,
    entrada: MensajeVendedorEntrada,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> MensajeSalida:
    """Respuesta escrita por una persona del negocio. (En Fase B también se manda por el canal real.)"""
    conversacion = await conversaciones.obtener_conversacion(db_session, usuario.organizacion_id, conversacion_id, True)
    if conversacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_CONVERSACION)
    mensaje = await conversaciones.agregar_mensaje(
        db_session, conversacion, "vendedor", entrada.texto, simulado=conversacion.canal == "simulador"
    )
    salida = MensajeSalida.model_validate(mensaje)
    await db_session.commit()
    return salida


# ------------------------------------------------------------------ pedidos y avisos


@router.get("/pedidos", response_model=list[PedidoSalida])
async def listar_pedidos(
    estado: str | None = Query(default=None, max_length=20),
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> list[PedidoSalida]:
    if estado is not None and estado not in ESTADOS_PEDIDO:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Estado de pedido inválido.")
    return await venta.listar_pedidos(db_session, usuario.organizacion_id, (estado,) if estado else None)


ACCIONES = {"confirmar-pago": "confirmar_pago", "rechazar-pago": "rechazar_pago", "entregado": "entregado", "cancelar": "cancelar"}
EVENTOS = {"confirmar_pago": "pago_confirmado", "rechazar_pago": "pago_rechazado", "entregado": "pedido_entregado", "cancelar": "pedido_cancelado"}


@router.post("/pedidos/{pedido_id}/{accion}", response_model=PedidoSalida)
async def decidir_pedido(
    pedido_id: uuid.UUID,
    accion: str,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*EDITORES)),
) -> PedidoSalida:
    """Solo una PERSONA confirma un pago (el agente nunca)."""
    if accion not in ACCIONES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Acción desconocida.")
    try:
        pedido = await venta.decidir(db_session, usuario.organizacion_id, pedido_id, ACCIONES[accion], usuario.id)
    except venta.TransicionInvalidaError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El pedido está «{error.estado}»: no se puede hacer eso.")
    except venta.VentaError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if pedido is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_PEDIDO)
    await registrar_evento(
        EVENTOS[ACCIONES[accion]], organizacion_id=usuario.organizacion_id, usuario_id=usuario.id, objetivo_tipo="pedido",
        objetivo_id=pedido_id, detalle={"total": str(pedido.total), "simulado": pedido.simulado}, **contexto_peticion(request),
    )
    return pedido


@router.get("/notificaciones", response_model=NotificacionesListado)
async def listar_notificaciones(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> NotificacionesListado:
    filas, sin_leer = await conversaciones.listar_notificaciones(db_session, usuario.organizacion_id)
    return NotificacionesListado(notificaciones=filas, sin_leer=sin_leer)


@router.post("/notificaciones/leer", status_code=status.HTTP_204_NO_CONTENT)
async def leer_notificaciones(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES)),
) -> Response:
    await conversaciones.marcar_leidas(db_session, usuario.organizacion_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
