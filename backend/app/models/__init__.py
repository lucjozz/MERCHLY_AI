"""SQLAlchemy models for AICOS.

Schema source of truth: ``docs/006-BaseDatos``. Se importan todos para que
``Base.metadata`` (usado por Alembic) los conozca.
"""

from app.models.atencion import AtencionConfig, Conversacion, Mensaje, Notificacion, Pedido, QrPago, ZonaEnvio
from app.models.base import Base
from app.models.campana import Campana
from app.models.decisiones import (
    DecisionContext,
    DecisionEvidence,
    DecisionOutcome,
    DecisionRecord,
)
from app.models.evento_auditoria import EventoAuditoria
from app.models.inventario import InventarioFoto, InventarioProducto
from app.models.invitacion import Invitacion
from app.models.organizacion import Organizacion
from app.models.producto_candidato import ProductoCandidato
from app.models.refresh_token import RefreshToken
from app.models.restablecimiento import RestablecimientoPassword
from app.models.usuario import Usuario

__all__ = [
    "AtencionConfig",
    "Conversacion",
    "Mensaje",
    "Notificacion",
    "Pedido",
    "QrPago",
    "ZonaEnvio",
    "Base",
    "Campana",
    "DecisionContext",
    "DecisionEvidence",
    "DecisionOutcome",
    "DecisionRecord",
    "EventoAuditoria",
    "InventarioFoto",
    "InventarioProducto",
    "Invitacion",
    "Organizacion",
    "ProductoCandidato",
    "RefreshToken",
    "RestablecimientoPassword",
    "Usuario",
]
