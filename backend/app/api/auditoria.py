"""GET /auditoria: actividad de seguridad del negocio (solo admin; docs/013-Seguridad/06)."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencias import requiere_rol
from app.models.usuario import Usuario
from app.services.auditoria import ACCIONES, listar_eventos

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


class EventoSalida(BaseModel):
    id: uuid.UUID
    accion: str
    usuario_id: uuid.UUID | None
    usuario_nombre: str | None
    objetivo_tipo: str | None
    detalle: dict
    ip: str | None
    creado_en: datetime


class EventosListado(BaseModel):
    eventos: list[EventoSalida]
    total: int
    pagina: int
    tamano_pagina: int


@router.get("", response_model=EventosListado)
async def eventos(
    pagina: int = Query(default=1, ge=1, le=10_000),
    tamano_pagina: int = Query(default=50, ge=1, le=100),
    accion: str | None = Query(default=None, max_length=50),
    db_session: AsyncSession = Depends(get_db_session),
    admin: Usuario = Depends(requiere_rol("admin_principal")),
) -> EventosListado:
    filtro = accion if accion in ACCIONES else None
    filas, total = await listar_eventos(db_session, admin.organizacion_id, pagina, tamano_pagina, filtro)
    ids = {f.usuario_id for f in filas if f.usuario_id}
    nombres: dict[uuid.UUID, str] = {}
    if ids:
        resultado = await db_session.execute(
            select(Usuario.id, Usuario.nombre).where(Usuario.id.in_(ids), Usuario.organizacion_id == admin.organizacion_id)
        )
        nombres = {fila.id: fila.nombre for fila in resultado}
    return EventosListado(
        eventos=[
            EventoSalida(
                id=f.id,
                accion=f.accion,
                usuario_id=f.usuario_id,
                usuario_nombre=nombres.get(f.usuario_id) if f.usuario_id else None,
                objetivo_tipo=f.objetivo_tipo,
                detalle=f.detalle or {},
                ip=f.ip,
                creado_en=f.creado_en,
            )
            for f in filas
        ],
        total=total,
        pagina=pagina,
        tamano_pagina=tamano_pagina,
    )
