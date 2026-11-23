"""Model for ``organizaciones`` (multi-tenancy, docs/013-Seguridad/04, sección 2).

Cada negocio que usa MERCHLY AI es una organización. Todo dato de negocio
(productos candidatos, decisiones) pertenece a exactamente una, y la base
de datos impide (Row-Level Security) que una organización vea o toque los
datos de otra.
"""

from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo


class Organizacion(ConMarcaDeTiempo, Base):
    """Un negocio cliente de MERCHLY AI.

    Attributes:
        nombre: nombre para mostrar del negocio.
        activo: una organización inactiva no puede operar (sus usuarios
            reciben 401), sin perder su historial.
        plan: beta, emprendedor o negocio. Define los modelos de IA de sus
            agentes (docs/007-Agentes/07). Lo cambia solo el sistema.
    """

    __tablename__ = "organizaciones"

    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    plan: Mapped[str] = mapped_column(
        String(20), nullable=False, default="beta", server_default="beta"
    )

    # Perfil del negocio (onboarding, docs/004-Backend/03 sección 3).
    pais: Mapped[str] = mapped_column(String(2), nullable=False, default="BO", server_default="BO")
    rubro: Mapped[str | None] = mapped_column(String(120), nullable=True)
    presupuesto_mensual: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default="BOB", server_default="BOB")
    tipo_cambio: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    costo_envio_unitario_usd: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    impuestos_importacion_pct: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, default=Decimal("0"), server_default="0"
    )
    onboarding_completo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
