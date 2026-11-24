"""Endpoints de autenticación (docs/013-Seguridad/01 y 04).

Todas las respuestas de /auth llevan ``Cache-Control: no-store`` (lo pone
el middleware de headers de seguridad).
"""

import logging
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db_session
from sqlalchemy import or_, select

from app.core.dependencias import contexto_peticion, obtener_claims, obtener_ip_cliente, obtener_usuario_autenticado
from app.services.auditoria import hash_corto, registrar_evento
from app.core.redis import get_redis_client
from app.core.security import ClaimsAcceso
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.schemas.auth import (
    CodigoInput,
    CodigosRespaldo,
    DesafioOutput,
    DosPasosInicio,
    ReautenticarInput,
    VerificarDosPasosInput,
    GoogleLoginInput,
    OlvidePasswordInput,
    RestablecerPasswordInput,
    LoginInput,
    LogoutInput,
    RefreshInput,
    SesionOutput,
    UsuarioActual,
)
from app.services.autenticacion import (
    RefreshInvalidoError,
    Sesion,
    autenticar_usuario,
    cerrar_todas_las_sesiones,
    emitir_sesion,
    revocar_refresh,
    rotar_refresh,
    usuario_desde_google,
)
from app.core.security import PasswordInvalidaError
from app.schemas.usuarios import AceptarInvitacionEntrada
from app.services.recuperar_password import (
    TokenRestablecimientoInvalidoError,
    restablecer_password,
    solicitar_restablecimiento,
)
from app.services.equipo import InvitacionInvalidaError, aceptar_invitacion
from app.services.google_auth import GoogleTokenInvalidoError, verificar_id_token_google
from app.services import dos_pasos
from app.services.limites import LimitesLogin, RedisError, revocar_jti

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

_CREDENCIALES_INVALIDAS = "Email o contraseña incorrectos."


def _a_output(sesion: Sesion) -> SesionOutput:
    return SesionOutput(
        access_token=sesion.access_token,
        expira_en=sesion.expira_en,
        refresh_token=sesion.refresh_token,
        refresh_expira_en=sesion.refresh_expira_en,
    )


async def _sesion_o_desafio(db_session: AsyncSession, redis: Redis, usuario: Usuario) -> SesionOutput | DesafioOutput:
    """Con la verificación en dos pasos activada, la contraseña (o Google) no alcanza: falta el código."""
    if usuario.totp_activado:
        try:
            return DesafioOutput(desafio=await dos_pasos.crear_desafio(redis, usuario.id))
        except RedisError:
            raise _servicio_no_disponible()
    return _a_output(await emitir_sesion(db_session, usuario))


def _limites(redis: Redis) -> LimitesLogin:
    s = get_settings()
    return LimitesLogin(
        redis, s.login_max_fallos_email_ip, s.login_max_fallos_ip, s.login_ventana_segundos,
        max_email=s.login_max_fallos_email,
    )


def _demasiados_intentos(segundos: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Demasiados intentos. Esperá unos minutos y volvé a probar.",
        headers={"Retry-After": str(segundos)},
    )


def _servicio_no_disponible() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="El inicio de sesión no está disponible en este momento.",
    )


@router.post("/login", response_model=SesionOutput | DesafioOutput)
async def login(
    entrada: LoginInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> SesionOutput | DesafioOutput:
    """Login con email y contraseña.

    429 tras 5 fallos por email+IP o 20 por IP en 15 min. Si Redis no
    responde, 503 (fail-closed: sin límite de intentos no hay login).
    """
    ip = obtener_ip_cliente(request)
    limites = _limites(redis)
    try:
        espera = await limites.segundos_bloqueado(entrada.email, ip)
    except RedisError:
        logger.error("Redis no disponible: login rechazado (fail-closed)")
        raise _servicio_no_disponible()
    if espera:
        raise _demasiados_intentos(espera)

    usuario = await autenticar_usuario(db_session, entrada.email, entrada.password)
    if usuario is None:
        try:
            await limites.registrar_fallo(entrada.email, ip)
        except RedisError:
            raise _servicio_no_disponible()
        logger.info("login_fallido")
        await registrar_evento("login_fallido", detalle={"email_hash": hash_corto(entrada.email)}, **contexto_peticion(request))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_CREDENCIALES_INVALIDAS)

    try:
        await limites.limpiar(entrada.email, ip)
    except RedisError:
        pass
    if usuario.totp_activado:
        return await _sesion_o_desafio(db_session, redis, usuario)  # el login_ok se registra al verificar el código
    logger.info("login_ok usuario=%s", usuario.id)
    await registrar_evento("login_ok", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id, **contexto_peticion(request))
    return _a_output(await emitir_sesion(db_session, usuario))


@router.post("/refresh", response_model=SesionOutput)
async def refrescar(
    entrada: RefreshInput, db_session: AsyncSession = Depends(get_db_session)
) -> SesionOutput:
    """Canjea el refresh token por un par nuevo (rotación)."""
    try:
        return _a_output(await rotar_refresh(db_session, entrada.refresh_token))
    except RefreshInvalidoError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión vencida.")


@router.post("/google", response_model=SesionOutput | DesafioOutput)
async def login_google(
    entrada: GoogleLoginInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> SesionOutput | DesafioOutput:
    """Login / auto-registro con Google. 503 si GOOGLE_CLIENT_ID no está configurado."""
    client_id = get_settings().google_client_id
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El inicio de sesión con Google no está habilitado.",
        )
    ip = obtener_ip_cliente(request)
    limites = _limites(redis)
    try:
        espera = await limites.segundos_bloqueado("google", ip)
    except RedisError:
        raise _servicio_no_disponible()
    if espera:
        raise _demasiados_intentos(espera)

    try:
        identidad = await verificar_id_token_google(entrada.id_token, client_id)
    except GoogleTokenInvalidoError as error:
        # Solo el motivo (p. ej. "Invalid audience"), nunca el token.
        logger.warning("Token de Google rechazado: %s", error)
        await limites.registrar_fallo("google", ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo validar tu cuenta de Google.")

    existia = await db_session.scalar(
        select(Usuario.id).where(or_(Usuario.google_sub == identidad.sub, Usuario.email == identidad.email.strip().lower()))
    )
    usuario = await usuario_desde_google(db_session, identidad.sub, identidad.email, identidad.nombre)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo validar tu cuenta de Google.")
    if usuario.totp_activado:
        return await _sesion_o_desafio(db_session, redis, usuario)
    await registrar_evento(
        "login_google" if existia else "registro_google",
        organizacion_id=usuario.organizacion_id, usuario_id=usuario.id, **contexto_peticion(request),
    )
    return _a_output(await emitir_sesion(db_session, usuario))


@router.post("/aceptar-invitacion", response_model=SesionOutput)
async def aceptar(
    entrada: AceptarInvitacionEntrada,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> SesionOutput:
    """Crea la cuenta de una persona invitada e inicia su sesión.

    Mismo mensaje para token inexistente, vencido, usado o revocado.
    Comparte el límite de intentos del login (por IP).
    """
    ip = obtener_ip_cliente(request)
    limites = _limites(redis)
    try:
        espera = await limites.segundos_bloqueado("invitacion", ip)
    except RedisError:
        raise _servicio_no_disponible()
    if espera:
        raise _demasiados_intentos(espera)
    try:
        usuario = await aceptar_invitacion(db_session, entrada.token, entrada.nombre, entrada.password)
    except PasswordInvalidaError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
    except InvitacionInvalidaError:
        try:
            await limites.registrar_fallo("invitacion", ip)
        except RedisError:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La invitación no es válida o ya venció. Pedile una nueva al admin de tu negocio.",
        )
    logger.info("invitacion_aceptada usuario=%s", usuario.id)
    await registrar_evento(
        "invitacion_aceptada", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
        detalle={"rol": usuario.rol}, **contexto_peticion(request),
    )
    return _a_output(await emitir_sesion(db_session, usuario))


@router.post("/olvide-password", status_code=status.HTTP_202_ACCEPTED)
async def olvide_password(
    entrada: OlvidePasswordInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> dict[str, str]:
    """Siempre la misma respuesta, exista o no el email (sin enumeración).
    Comparte el límite de intentos del login."""
    ip = obtener_ip_cliente(request)
    limites = _limites(redis)
    try:
        espera = await limites.segundos_bloqueado(f"olvido:{entrada.email}", ip)
        if espera:
            raise _demasiados_intentos(espera)
        await limites.registrar_fallo(f"olvido:{entrada.email}", ip)  # cada pedido cuenta
    except RedisError:
        raise _servicio_no_disponible()
    usuario = await solicitar_restablecimiento(db_session, entrada.email)
    if usuario is not None:
        await registrar_evento(
            "password_restablecimiento_pedido", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
            **contexto_peticion(request),
        )
    return {"detail": "Si el email está registrado, te mandamos un link para restablecer la contraseña."}


@router.post("/restablecer-password", status_code=status.HTTP_204_NO_CONTENT)
async def restablecer(
    entrada: RestablecerPasswordInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> Response:
    """Cambia la contraseña con el link del email y cierra todas las sesiones."""
    ip = obtener_ip_cliente(request)
    limites = _limites(redis)
    try:
        espera = await limites.segundos_bloqueado("restablecer", ip)
    except RedisError:
        raise _servicio_no_disponible()
    if espera:
        raise _demasiados_intentos(espera)
    try:
        usuario = await restablecer_password(db_session, entrada.token, entrada.password)
    except PasswordInvalidaError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error
    except TokenRestablecimientoInvalidoError:
        try:
            await limites.registrar_fallo("restablecer", ip)
        except RedisError:
            pass
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El link no es válido o ya venció. Pedí uno nuevo.",
        )
    await registrar_evento(
        "password_restablecida", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
        **contexto_peticion(request),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    entrada: LogoutInput,
    request: Request,
    claims: ClaimsAcceso = Depends(obtener_claims),
    usuario: Usuario = Depends(obtener_usuario_autenticado),
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> Response:
    """Revoca el access token actual (denylist por jti) y el refresh token."""
    try:
        await revocar_jti(redis, claims.jti, claims.exp - int(time.time()))
    except RedisError:
        logger.warning("Redis no disponible: el access token vence solo en <=15 min")
    if entrada.refresh_token:
        await revocar_refresh(db_session, entrada.refresh_token, usuario.id)
    await registrar_evento("logout", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id, **contexto_peticion(request))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/cerrar-todas-las-sesiones", status_code=status.HTTP_204_NO_CONTENT)
async def cerrar_sesiones(
    request: Request,
    usuario: Usuario = Depends(obtener_usuario_autenticado),
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Invalida todas las sesiones del usuario en todos sus dispositivos."""
    await cerrar_todas_las_sesiones(db_session, usuario)
    await registrar_evento(
        "sesiones_cerradas", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id, **contexto_peticion(request)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UsuarioActual)
async def obtener_usuario_actual(
    usuario: Usuario = Depends(obtener_usuario_autenticado),
    db_session: AsyncSession = Depends(get_db_session),
) -> UsuarioActual:
    """Datos del usuario autenticado y su organización (nunca el hash)."""
    organizacion = await db_session.get(Organizacion, usuario.organizacion_id)
    salida = UsuarioActual.model_validate(usuario)
    salida.organizacion_nombre = organizacion.nombre if organizacion else None
    return salida


# ------------------------------------------------------------ verificación en dos pasos (013-09)

_CODIGO_INVALIDO = "El código no es correcto o ya venció. Volvé a iniciar sesión si hace falta."


@router.post("/2fa/verificar", response_model=SesionOutput)
async def verificar_dos_pasos(
    entrada: VerificarDosPasosInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> SesionOutput:
    """Segundo paso del login: desafío + código del celular (o de respaldo). Pública (no hay sesión todavía)."""
    ip = obtener_ip_cliente(request)
    limites = _limites(redis)
    try:
        espera = await limites.segundos_bloqueado("2fa", ip)
        if espera:
            raise _demasiados_intentos(espera)
        usuario_id = await dos_pasos.usuario_del_desafio(redis, entrada.desafio)
    except RedisError:
        raise _servicio_no_disponible()
    if usuario_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_CODIGO_INVALIDO)
    if not await dos_pasos.verificar_codigo(db_session, usuario_id, entrada.codigo):
        try:
            await limites.registrar_fallo("2fa", ip)
        except RedisError:
            pass
        await registrar_evento("dos_pasos_fallido", usuario_id=usuario_id, **contexto_peticion(request))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_CODIGO_INVALIDO)
    await dos_pasos.consumir_desafio(redis, entrada.desafio)
    usuario = await db_session.get(Usuario, usuario_id)
    if usuario is None or not usuario.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_CODIGO_INVALIDO)
    await registrar_evento("login_ok", organizacion_id=usuario.organizacion_id, usuario_id=usuario.id,
                           detalle={"dos_pasos": True}, **contexto_peticion(request))
    return _a_output(await emitir_sesion(db_session, usuario))


@router.post("/2fa/iniciar", response_model=DosPasosInicio)
async def iniciar_dos_pasos(
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(obtener_usuario_autenticado),
) -> DosPasosInicio:
    if usuario.totp_activado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La verificación en dos pasos ya está activada.")
    return DosPasosInicio(**await dos_pasos.iniciar(db_session, usuario.id))


@router.post("/2fa/activar", response_model=CodigosRespaldo)
async def activar_dos_pasos(
    entrada: CodigoInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(obtener_usuario_autenticado),
) -> CodigosRespaldo:
    """Activa con un código válido. Devuelve los 10 códigos de respaldo UNA sola vez."""
    if usuario.totp_activado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La verificación en dos pasos ya está activada.")
    org_id, usuario_id = usuario.organizacion_id, usuario.id
    try:
        codigos = await dos_pasos.activar(db_session, usuario_id, entrada.codigo)
    except dos_pasos.CodigoInvalidoError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error))
    await registrar_evento("dos_pasos_activado", organizacion_id=org_id, usuario_id=usuario_id, **contexto_peticion(request))
    return CodigosRespaldo(codigos=codigos)


@router.post("/2fa/desactivar", status_code=status.HTTP_204_NO_CONTENT)
async def desactivar_dos_pasos(
    entrada: CodigoInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(obtener_usuario_autenticado),
) -> Response:
    """Pide un código válido: alguien con la sesión abierta no puede apagarla sin el celular."""
    if not usuario.totp_activado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La verificación en dos pasos no está activada.")
    org_id, usuario_id = usuario.organizacion_id, usuario.id
    try:
        await dos_pasos.desactivar(db_session, usuario_id, entrada.codigo)
    except dos_pasos.CodigoInvalidoError as error:
        await registrar_evento("dos_pasos_fallido", organizacion_id=org_id, usuario_id=usuario_id, **contexto_peticion(request))
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error))
    await registrar_evento("dos_pasos_desactivado", organizacion_id=org_id, usuario_id=usuario_id, **contexto_peticion(request))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/reautenticar", status_code=status.HTTP_204_NO_CONTENT)
async def reautenticar(
    entrada: ReautenticarInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
    usuario: Usuario = Depends(obtener_usuario_autenticado),
) -> Response:
    """Confirmar que sos vos antes de una acción sensible (vale 10 minutos)."""
    limites = _limites(redis)
    org_id, usuario_id, con_codigo = usuario.organizacion_id, usuario.id, usuario.totp_activado
    ip = obtener_ip_cliente(request)
    try:
        espera = await limites.segundos_bloqueado(f"reauth:{usuario_id}", ip)
        if espera:
            raise _demasiados_intentos(espera)
        ok = await dos_pasos.reautenticar(redis, db_session, usuario_id, entrada.codigo, entrada.password)
        if not ok:
            await limites.registrar_fallo(f"reauth:{usuario_id}", ip)
    except RedisError:
        raise _servicio_no_disponible()
    if not ok:
        await registrar_evento("reautenticacion_fallida", organizacion_id=org_id, usuario_id=usuario_id, **contexto_peticion(request))
        detalle = "El código no es correcto." if con_codigo else "La contraseña no es correcta."
        # 422 y no 401: la sesión sigue siendo válida (un 401 haría que el navegador cierre la sesión).
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detalle)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
