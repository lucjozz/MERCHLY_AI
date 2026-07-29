"""Endpoint del Agente Investigador de Producto.

Expone el contrato técnico documentado en
``docs/007-Agentes/03-Agente-Investigador-de-Producto.md`` como una API
HTTP. Nivel de permiso 1 (análisis y recomendación, sección 6 del
contrato): este endpoint nunca modifica el catálogo real de una tienda,
solo persiste candidatos en estado ``'candidato'``.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.investigador_producto import InvestigacionInput, InvestigacionOutput
from app.services.agente_investigador_producto import AgenteInvestigadorProducto
from app.services.proveedores.simulado import ProveedorInvestigacionSimulado

router = APIRouter(prefix="/agentes", tags=["agentes"])


@router.post(
    "/investigador-producto",
    response_model=InvestigacionOutput,
    status_code=status.HTTP_200_OK,
)
async def investigar_producto(
    entrada: InvestigacionInput,
    db_session: AsyncSession = Depends(get_db_session),
) -> InvestigacionOutput:
    """Ejecuta una investigación de producto.

    Args:
        entrada: solicitud validada automáticamente por FastAPI/Pydantic
            contra ``InvestigacionInput`` (sección 2 del contrato) antes
            de que este cuerpo de función se ejecute.
        db_session: sesión de base de datos inyectada.

    Returns:
        InvestigacionOutput: productos candidatos encontrados y su
        metadata (sección 3 del contrato).
    """
    # Proveedor provisional (ver app/services/proveedores/simulado.py):
    # todavía no hay integración real con Gemini.
    proveedor = ProveedorInvestigacionSimulado()
    agente = AgenteInvestigadorProducto(proveedor=proveedor, db_session=db_session)

    return await agente.ejecutar(entrada)
