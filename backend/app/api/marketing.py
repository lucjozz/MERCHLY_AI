"""Endpoint del Agente de Marketing.

Expone el contrato técnico documentado en
``docs/007-Agentes/06-Agente-de-Marketing.md``. Nivel de permiso 1
(análisis y recomendación, sección 6 del contrato): este endpoint nunca
publica anuncios ni ejecuta gasto real.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.api.cuotas import aplicar_cuota
from app.core.config import get_settings
from app.core.dependencias import ROLES_DECISION, requiere_rol
from app.core.redis import get_redis_client
from app.services.campanas import guardar_campana
from app.services.planes import modelo_para, plan_de_organizacion
from app.services.proveedores.marketing_base import ProveedorMarketing
from app.services.proveedores.marketing_openai import ProveedorMarketingOpenAI
from app.models.usuario import Usuario
from app.schemas.marketing import MarketingInput, MarketingOutput
from app.services.agente_marketing import AgenteMarketing, ProductosInvalidosError
from app.services.proveedores.marketing_simulado import ProveedorMarketingSimulado

router = APIRouter(prefix="/agentes", tags=["agentes"])


def _obtener_proveedor(plan: str = "beta") -> ProveedorMarketing:
    """OpenAI (modelo según el plan) si hay OPENAI_API_KEY; si no, el simulado."""
    if get_settings().openai_api_key:
        return ProveedorMarketingOpenAI(modelo=modelo_para("marketing", plan))
    return ProveedorMarketingSimulado()


@router.post(
    "/marketing",
    response_model=MarketingOutput,
    status_code=status.HTTP_200_OK,
)
async def generar_campana_marketing(
    entrada: MarketingInput,
    db_session: AsyncSession = Depends(get_db_session),
    usuario: Usuario = Depends(requiere_rol(*ROLES_DECISION)),
    redis: Redis = Depends(get_redis_client),
) -> MarketingOutput:
    """Genera una propuesta de campaña de marketing.

    Args:
        entrada: solicitud validada automáticamente por FastAPI/Pydantic
            contra ``MarketingInput`` (sección 2 del contrato).
        db_session: sesión de base de datos inyectada.
        usuario: usuario autenticado (docs/013-Seguridad/02-..., matriz).

    Returns:
        MarketingOutput: la propuesta de campaña (sección 3 del contrato).

    Raises:
        HTTPException: 422 si algún producto referenciado no existe o no
            está en estado 'en_catalogo' (``ProductosInvalidosError``).
    """
    await aplicar_cuota(
        redis, "marketing", usuario.organizacion_id, get_settings().cuota_marketing_por_hora
    )
    plan = await plan_de_organizacion(db_session, usuario.organizacion_id)
    proveedor = _obtener_proveedor(plan)
    agente = AgenteMarketing(
        proveedor=proveedor, db_session=db_session, organizacion_id=usuario.organizacion_id
    )

    try:
        salida = await agente.ejecutar(entrada)
    except ProductosInvalidosError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error

    # Se guarda en el historial solo si se generó contenido (DEC-034).
    if salida.angulos_de_campana or salida.copy_por_canal:
        campana = await guardar_campana(
            db_session, usuario.organizacion_id, usuario.id, entrada, salida, agente.nombres_productos
        )
        salida.metadata.campana_id = campana.id
    return salida