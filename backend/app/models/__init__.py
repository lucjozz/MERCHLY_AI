"""SQLAlchemy models for AICOS.

Schema source of truth: ``docs/006-BaseDatos``.
"""

from app.models.base import Base
from app.models.producto_candidato import ProductoCandidato

__all__ = ["Base", "ProductoCandidato"]
