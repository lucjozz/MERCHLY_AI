"""Health check endpoints.

`/health` satisfies the technical closure criterion of Fase 0 defined in
``docs/003-CEO/03-Criterios-de-Exito-Fase0.md``: "Existe al menos un
endpoint de backend funcionando (/health)".

`/health/ready` was added in Fase 1 once the backend actually connects to
PostgreSQL and Redis (see ``docs/007-Agentes`` and ``memory/DECISIONS.md``,
DEC-018): it checks those dependencies are reachable, following the
standard liveness/readiness separation (liveness = "is the process up",
readiness = "can it actually serve traffic that needs its dependencies").
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.redis import get_redis_client

router = APIRouter()


class HealthResponse(BaseModel):
    """Response schema for the /health endpoint.

    Attributes:
        status: Literal health status of the service.
        service: Name of the service reporting health.
        version: Deployed version of the service.
        environment: Environment the service is running in.
        timestamp: UTC timestamp of the check, in ISO 8601 format.
    """

    status: str
    service: str
    version: str
    environment: str
    timestamp: str


class ReadinessResponse(BaseModel):
    """Response schema for the /health/ready endpoint.

    Attributes:
        status: "ok" only if every dependency below is also "ok".
        database: Status of the PostgreSQL connection ("ok" or "error").
        redis: Status of the Redis connection ("ok" or "error").
        timestamp: UTC timestamp of the check, in ISO 8601 format.
    """

    status: str
    database: str
    redis: str
    timestamp: str


@router.get("/health", response_model=HealthResponse, tags=["infra"])
def health_check() -> HealthResponse:
    """Report the current liveness of the backend service.

    Returns:
        HealthResponse: a minimal, dependency-free health signal. This
        endpoint deliberately does not check downstream services; use
        ``/health/ready`` for that.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/health/ready", response_model=ReadinessResponse, tags=["infra"])
async def readiness_check(
    db_session: AsyncSession = Depends(get_db_session),
    redis_client: Redis = Depends(get_redis_client),
) -> ReadinessResponse:
    """Report whether the backend's dependencies (DB, Redis) are reachable.

    Args:
        db_session: injected async SQLAlchemy session.
        redis_client: injected async Redis client.

    Returns:
        ReadinessResponse: per-dependency status. Overall ``status`` is
        "ok" only if both PostgreSQL and Redis respond successfully;
        otherwise it is "degraded", without raising an HTTP error, so
        callers can inspect which dependency failed.
    """
    database_status = "ok"
    try:
        await db_session.execute(text("SELECT 1"))
    except Exception:
        database_status = "error"

    redis_status = "ok"
    try:
        await redis_client.ping()
    except Exception:
        redis_status = "error"

    overall = "ok" if database_status == "ok" and redis_status == "ok" else "degraded"

    return ReadinessResponse(
        status=overall,
        database=database_status,
        redis=redis_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
