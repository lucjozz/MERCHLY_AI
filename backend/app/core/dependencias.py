"""Dependencias compartidas de FastAPI (docs/013-Seguridad/03 y 04)."""

import logging

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import fijar_organizacion, get_db_session
from app.core.redis import get_redis_client
from app.core.security import ClaimsAcceso, decodificar_access_token
from app.models.organizacion import Organizacion
from app.models.usuario import Usuario
from app.services.limites import RedisError, jti_revocado

logger = logging.getLogger(__name__)

# auto_error=False: sin header respondemos 401 nosotros (FastAPI viejo daba
# 403, que según la norma 6 es "sin permiso", no "sin identidad").
security_scheme = HTTPBearer(auto_error=False)

ROLES_DECISION = ("admin_principal", "responsable_tecnico", "responsable_negocio")
ROLES_BORRADO = ("admin_principal", "responsable_negocio")
TODOS_LOS_ROLES = (*ROLES_DECISION, "usuario_operativo")


def _no_autenticado() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión inválida o vencida.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def obtener_ip_cliente(request: Request) -> str:
    """IP del cliente. Solo confía en headers de proxy si CONFIAR_PROXY=true
    (si el origen no está cerrado detrás del proxy, son falsificables)."""
    if get_settings().confiar_proxy:
        cf = request.headers.get("cf-connecting-ip")
        if cf:
            return cf.strip()
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
    return request.client.host if request.client else "desconocida"


def contexto_peticion(request: Request) -> dict[str, str | None]:
    """IP real y navegador, para la bitácora de auditoría."""
    return {"ip": obtener_ip_cliente(request), "user_agent": request.headers.get("user-agent")}


async def obtener_claims(
    request: Request,
    credenciales: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    redis: Redis = Depends(get_redis_client),
) -> ClaimsAcceso:
    """Valida el access token y que no esté revocado."""
    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise _no_autenticado()
    claims = decodificar_access_token(credenciales.credentials)
    if claims is None:
        raise _no_autenticado()
    try:
        if await jti_revocado(redis, claims.jti):
            raise _no_autenticado()
    except RedisError:
        # Fail-open documentado: el access token vive 15 min como máximo.
        logger.warning("Redis no disponible al verificar revocación de token")
    request.state.claims = claims
    return claims


async def obtener_usuario_autenticado(
    claims: ClaimsAcceso = Depends(obtener_claims),
    db_session: AsyncSession = Depends(get_db_session),
) -> Usuario:
    """Confirma que el usuario existe, está activo, su organización está
    activa y el token no fue invalidado (token_version). Fija la
    organización en la sesión de base de datos (RLS).

    Es la pieza que los tests reemplazan vía app.dependency_overrides; el
    chequeo de rol de requiere_rol() sigue corriendo de verdad encima.
    """
    usuario = await db_session.get(Usuario, claims.usuario_id)
    if (
        usuario is None
        or not usuario.activo
        or usuario.eliminado_en is not None
        or usuario.token_version != claims.version
        or usuario.organizacion_id != claims.organizacion_id
    ):
        raise _no_autenticado()

    organizacion = await db_session.get(Organizacion, usuario.organizacion_id)
    if organizacion is None or not organizacion.activo:
        raise _no_autenticado()

    await fijar_organizacion(db_session, usuario.organizacion_id)
    return usuario


def requiere_rol(*roles_permitidos: str):
    """Crea una dependencia que exige uno de los roles indicados (403 si no)."""

    async def _verificar(
        usuario: Usuario = Depends(obtener_usuario_autenticado),
        db_session: AsyncSession = Depends(get_db_session),
    ) -> Usuario:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tenés permiso para realizar esta acción.",
            )
        # Idempotente: asegura RLS también cuando los tests reemplazan
        # obtener_usuario_autenticado.
        await fijar_organizacion(db_session, usuario.organizacion_id)
        return usuario

    return _verificar
