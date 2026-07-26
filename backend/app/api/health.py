"""Health check endpoint.

Satisfies the technical closure criterion of Fase 0 defined in
``docs/003-CEO/03-Criterios-de-Exito-Fase0.md``: "Existe al menos un
endpoint de backend funcionando (/health)".
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

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


@router.get("/health", response_model=HealthResponse, tags=["infra"])
def health_check() -> HealthResponse:
    """Report the current health of the backend service.

    Returns:
        HealthResponse: a minimal, dependency-free health signal. This
        endpoint intentionally does not check downstream services
        (database, Redis) yet; that will be added once those
        integrations exist in Fase 2 (Núcleo de Plataforma).
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
