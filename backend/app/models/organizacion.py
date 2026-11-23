"""Model for ``organizaciones`` (multi-tenancy, docs/013-Seguridad/04, sección 2).

Cada negocio que usa MERCHLY AI es una organización. Todo dato de negocio
(productos candidatos, decisiones) pertenece a exactamente una, y la base
de datos impide (Row-Level Security) que una organización vea o toque los
datos de otra.
"""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo


class Organizacion(ConMarcaDeTiempo, Base):
    """Un negocio cliente de MERCHLY AI.

    Attributes:
        nombre: nombre para mostrar del negocio.
        activo: una organización inactiva no puede operar (sus usuarios
            reciben 401), sin perder su historial.
    """

    __tablename__ = "organizaciones"

    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
