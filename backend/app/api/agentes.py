"""Endpoint del Agente Investigador de Producto.

Expone el contrato técnico documentado en
``docs/007-Agentes/03-Agente-Investigador-de-Producto.md`` como una API
HTTP. Nivel de permiso 1 (análisis y recomendación, sección 6 del
contrato): este endpoint nunca modifica el catálogo real de una tienda,
solo persiste candidatos en estado ``'candidato'``.
"""

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db_session
from app.schemas.investigador_producto import InvestigacionInput, InvestigacionOutput
from app.services.agente_investigador_producto import AgenteInvestigadorProducto
from app.services.proveedores.base import ProveedorInvestigacion
from app.services.proveedores.gemini import ProveedorInvestigacionGemini
from app.services.proveedores.simulado import ProveedorInvestigacionSimulado
from app.api.cuotas import aplicar_cuota
from app.core.dependencias import ROLES_DECISION, requiere_rol
from app.core.redis import get_redis_client
from app.services.planes import modelo_para, plan_de_organizacion
from app.models.usuario import Usuario

router = APIRouter(prefix="/agentes", tags=["agentes"])


def _obtener_proveedor(plan: str = "beta") -> ProveedorInvestigacion:
    """Elige el proveedor de investigación según configuración.

    Returns:
        ProveedorInvestigacion: ``ProveedorInvestigacionGemini`` si
        ``GEMINI_API_KEY`` está configurada; de lo contrario,
        ``ProveedorInvestigacionSimulado`` (ver
        ``docs/007-Agentes/04-Registro-de-Agentes.md`` para el estado de
        este pendiente).
    """
    settings = get_settings()
    if settings.gemini_api_key:
        return ProveedorInvestigacionGemini(modelo=modelo_para("investigador", plan))
    return ProveedorInvestigacionSimulado()


@router.post(
    "/investigador-producto",
    response_model=InvestigacionOutput,
    status_code=status.HTTP_200_OK,
)
async def investigar_producto(
    entrada: InvestigacionInput,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*ROLES_DECISION)),
    redis: Redis = Depends(get_redis_client),
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
    await aplicar_cuota(
        redis, "investigador", usuario.organizacion_id,
        get_settings().cuota_investigador_por_hora,
    )
    plan = await plan_de_organizacion(db_session, usuario.organizacion_id)
    proveedor = _obtener_proveedor(plan)
    agente = AgenteInvestigadorProducto(
        proveedor=proveedor, db_session=db_session, organizacion_id=usuario.organizacion_id
    )

    return await agente.ejecutar(entrada)
