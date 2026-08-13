"""Endpoint del Agente de Analítica Básica.

Expone el contrato técnico documentado en
``docs/007-Agentes/05-Agente-Analitica-Basica.md``. Nivel de permiso 0
(solo lectura, sección 6 del contrato): este endpoint nunca escribe en
``productos_candidatos`` ni en ninguna otra tabla.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.analitica_basica import AnaliticaInput, AnaliticaOutput
from app.services.agente_analitica_basica import AgenteAnaliticaBasica

router = APIRouter(prefix="/agentes", tags=["agentes"])


@router.post(
    "/analitica-basica",
    response_model=AnaliticaOutput,
    status_code=status.HTTP_200_OK,
)
async def generar_reporte_analitica_basica(
    entrada: AnaliticaInput,
    db_session: AsyncSession = Depends(get_db_session),
) -> AnaliticaOutput:
    """Genera un reporte de analítica básica sobre productos candidatos.

    Args:
        entrada: filtros validados automáticamente por FastAPI/Pydantic
            contra ``AnaliticaInput`` (sección 2 del contrato).
        db_session: sesión de base de datos inyectada, usada solo para
            lectura.

    Returns:
        AnaliticaOutput: el reporte completo (sección 3 del contrato).
    """
    agente = AgenteAnaliticaBasica(db_session=db_session)
    return await agente.ejecutar(entrada)
