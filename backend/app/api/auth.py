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
from app.core.dependencias import obtener_claims, obtener_ip_cliente, obtener_usuario_autenticado
from app.core.redis import get_redis_client
from app.core.security import ClaimsAcceso
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.schemas.auth import (
    GoogleLoginInput,
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
from app.services.google_auth import GoogleTokenInvalidoError, verificar_id_token_google
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


@router.post("/login", response_model=SesionOutput)
async def login(
    entrada: LoginInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> SesionOutput:
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=_CREDENCIALES_INVALIDAS)

    try:
        await limites.limpiar(entrada.email, ip)
    except RedisError:
        pass
    logger.info("login_ok usuario=%s", usuario.id)
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


@router.post("/google", response_model=SesionOutput)
async def login_google(
    entrada: GoogleLoginInput,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis_client),
) -> SesionOutput:
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
    except GoogleTokenInvalidoError:
        await limites.registrar_fallo("google", ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo validar tu cuenta de Google.")

    usuario = await usuario_desde_google(db_session, identidad.sub, identidad.email, identidad.nombre)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pudo validar tu cuenta de Google.")
    return _a_output(await emitir_sesion(db_session, usuario))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    entrada: LogoutInput,
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
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/cerrar-todas-las-sesiones", status_code=status.HTTP_204_NO_CONTENT)
async def cerrar_sesiones(
    usuario: Usuario = Depends(obtener_usuario_autenticado),
    db_session: AsyncSession = Depends(get_db_session),
) -> Response:
    """Invalida todas las sesiones del usuario en todos sus dispositivos."""
    await cerrar_todas_las_sesiones(db_session, usuario)
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
