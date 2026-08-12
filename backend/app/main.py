"""FastAPI application entrypoint for MERCHLY AI (AICOS) backend.

This is the first piece of running code in the project, corresponding to
the technical closure criteria of Fase 0 (Fundación):
``docker compose up -d`` + a working ``/health`` endpoint. See
``docs/003-CEO/03-Criterios-de-Exito-Fase0.md``.
"""

from fastapi import FastAPI

from app.api.agentes import router as agentes_router
from app.api.analitica import router as analitica_router
from app.api.health import router as health_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI Commerce Operating System — API principal.",
)

app.include_router(health_router)
app.include_router(agentes_router)
app.include_router(analitica_router)
