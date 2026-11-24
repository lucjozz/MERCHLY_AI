"""GET /temporadas: próximas fechas comerciales de Bolivia (docs/004-Backend/05, sección 3).

Exige sesión (los 4 roles). Datos fijos: no lee ni escribe la base.
"""

from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.dependencias import TODOS_LOS_ROLES, requiere_rol
from app.models.usuario import Usuario
from app.services.temporadas import proximas_temporadas

router = APIRouter(prefix="/temporadas", tags=["temporadas"])


class TemporadaSalida(BaseModel):
    clave: str
    nombre: str
    fecha: date
    dias_faltantes: int
    anticipacion_dias: int
    preparar_ya: bool
    aproximada: bool
    ideas: list[str]


@router.get("", response_model=list[TemporadaSalida])
async def temporadas(_: Usuario = Depends(requiere_rol(*TODOS_LOS_ROLES))) -> list[TemporadaSalida]:
    return [
        TemporadaSalida(**{**t.__dict__, "ideas": list(t.ideas)}) for t in proximas_temporadas(date.today())
    ]
