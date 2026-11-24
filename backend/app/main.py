"""FastAPI application entrypoint for MERCHLY AI (AICOS) backend.

Seguridad según docs/013-Seguridad/04-Endurecimiento-para-Lanzamiento.md:
arranque que rechaza secretos débiles, headers de seguridad, tope de
tamaño de body, errores que no filtran datos, CORS por variable de entorno
y documentación de la API oculta salvo EXPONER_DOCS=true.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.agentes import router as agentes_router
from app.api.analitica import router as analitica_router
from app.api.auditoria import router as auditoria_router
from app.api.auth import router as auth_router
from app.api.campanas import router as campanas_router
from app.api.decisiones import router as decisiones_router
from app.api.health import router as health_router
from app.api.marketing import router as marketing_router
from app.api.organizacion import router as organizacion_router
from app.api.productos_candidatos import router as productos_candidatos_router
from app.api.atencion import router as atencion_router
from app.api.inventario import router as inventario_router
from app.api.temporadas import router as temporadas_router
from app.api.tipo_cambio import router as tipo_cambio_router
from app.api.usuarios import router as usuarios_router
from app.core.config import get_settings
from app.core.limite_peticiones import LimiteDePeticionesMiddleware
from app.core.middleware import HeadersDeSeguridadMiddleware, LimiteDeBodyMiddleware

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("merchly")


class ConfiguracionInseguraError(RuntimeError):
    """El backend se niega a arrancar con una configuración insegura."""


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    problemas = get_settings().problemas_de_seguridad()
    if problemas:
        for problema in problemas:
            logger.critical("Configuración insegura: %s", problema)
        raise ConfiguracionInseguraError("; ".join(problemas))
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Commerce Operating System — API principal.",
    lifespan=lifespan,
    docs_url="/docs" if settings.exponer_docs else None,
    redoc_url="/redoc" if settings.exponer_docs else None,
    openapi_url="/openapi.json" if settings.exponer_docs else None,
)


@app.exception_handler(RequestValidationError)
async def _validacion_sin_eco(_: Request, error: RequestValidationError) -> JSONResponse:
    """422 sin devolver el valor enviado (``input``) ni el contexto interno:
    si el campo era una contraseña, no vuelve en la respuesta."""
    detalle = [
        {"loc": list(e.get("loc", ())), "msg": e.get("msg", ""), "type": e.get("type", "")}
        for e in error.errors()
    ]
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detail": detalle})


@app.exception_handler(Exception)
async def _error_generico(request: Request, error: Exception) -> JSONResponse:
    """500 genérico con request_id; el detalle va solo al log."""
    request_id = getattr(request.state, "request_id", None) or request.scope.get("state", {}).get("request_id")
    logger.exception("Error no manejado request_id=%s ruta=%s", request_id, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocurrió un error interno. Probá de nuevo en un momento.", "request_id": request_id},
    )


# Orden: el último agregado es el más externo. Headers de seguridad envuelve
# todo (también los 413 y los errores de CORS).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.lista_cors_origenes,
    allow_credentials=False,  # se usa Bearer, no cookies, entre el BFF y el backend
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Retry-After", "X-Request-ID"],
    max_age=600,
)
app.add_middleware(LimiteDeBodyMiddleware, max_bytes=settings.max_body_bytes)


def _redis_para_limites():
    # Respeta el reemplazo de los tests (dependency_overrides) para no tocar el Redis real.
    from app.core.redis import get_redis_client

    from app.core.redis import redis_client

    reemplazo = app.dependency_overrides.get(get_redis_client)
    return reemplazo() if reemplazo else redis_client


app.add_middleware(LimiteDePeticionesMiddleware, obtener_redis=_redis_para_limites)
app.add_middleware(HeadersDeSeguridadMiddleware, hsts=settings.es_produccion)

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(agentes_router)
app.include_router(analitica_router)
app.include_router(marketing_router)
app.include_router(productos_candidatos_router)
app.include_router(decisiones_router)
app.include_router(campanas_router)
app.include_router(organizacion_router)
app.include_router(usuarios_router)
app.include_router(tipo_cambio_router)
app.include_router(temporadas_router)
app.include_router(inventario_router)
app.include_router(atencion_router)
app.include_router(auditoria_router)
