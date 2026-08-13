"""Endpoint del Agente de Marketing.

Expone el contrato técnico documentado en
``docs/007-Agentes/06-Agente-de-Marketing.md``. Nivel de permiso 1
(análisis y recomendación, sección 6 del contrato): este endpoint nunca
publica anuncios ni ejecuta gasto real.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.marketing import MarketingInput, MarketingOutput
from app.services.agente_marketing import AgenteMarketing, ProductosInvalidosError
from app.services.proveedores.marketing_simulado import ProveedorMarketingSimulado

router = APIRouter(prefix="/agentes", tags=["agentes"])


@router.post(
    "/marketing",
    response_model=MarketingOutput,
    status_code=status.HTTP_200_OK,
)
async def generar_campana_marketing(
    entrada: MarketingInput,
    db_session: AsyncSession = Depends(get_db_session),
) -> MarketingOutput:
    """Genera una propuesta de campaña de marketing.

    Args:
        entrada: solicitud validada automáticamente por FastAPI/Pydantic
            contra ``MarketingInput`` (sección 2 del contrato).
        db_session: sesión de base de datos inyectada.

    Returns:
        MarketingOutput: la propuesta de campaña (sección 3 del contrato).

    Raises:
        HTTPException: 422 si algún producto referenciado no existe o no
            está en estado 'en_catalogo' (``ProductosInvalidosError``).
    """
    # Proveedor provisional (ver
    # app/services/proveedores/marketing_simulado.py): todavía no hay
    # integración real con ChatGPT (rol "Marketing IA").
    proveedor = ProveedorMarketingSimulado()
    agente = AgenteMarketing(proveedor=proveedor, db_session=db_session)

    try:
        return await agente.ejecutar(entrada)
    except ProductosInvalidosError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error
