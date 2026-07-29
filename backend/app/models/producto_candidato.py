"""Model for ``productos_candidatos``.

Implements the schema documented in
``docs/006-BaseDatos/02-Esquema-Fase1.md``, which persists the output of
the Agente Investigador de Producto
(``docs/007-Agentes/03-Agente-Investigador-de-Producto.md``, sección 3).
"""

import uuid

from sqlalchemy import CheckConstraint, Index, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ConMarcaDeTiempo

NIVELES_VALIDOS = ("alto", "medio", "bajo")
ESTADOS_VALIDOS = ("candidato", "en_catalogo", "descartado")


class ProductoCandidato(ConMarcaDeTiempo, Base):
    """A product recommended by the Agente Investigador de Producto.

    See ``docs/006-BaseDatos/02-Esquema-Fase1.md`` for the full column
    reference and its correspondence with the agent's technical contract.

    Attributes:
        nombre_producto: name of the candidate product.
        categoria: category researched.
        mercado_objetivo: ISO 3166-1 alpha-2 target market code.
        precio_estimado_proveedor: estimated supplier cost (USD).
        precio_sugerido_venta: suggested selling price (USD).
        nivel_demanda_estimado: one of "alto", "medio", "bajo".
        nivel_competencia_estimado: one of "alto", "medio", "bajo".
        fuentes_evidencia: list of URLs/references backing the recommendation.
        riesgos_identificados: list of risks identified by the agent.
        estado: one of "candidato", "en_catalogo", "descartado". Only a
            human can move a row to "en_catalogo" (contrato del agente,
            sección 7 — Límites Explícitos).
        investigacion_id: groups every product returned by a single agent
            run. Not a foreign key yet (no ``investigaciones`` table).
    """

    __tablename__ = "productos_candidatos"
    __table_args__ = (
        CheckConstraint(
            "nivel_demanda_estimado IN ('alto', 'medio', 'bajo')",
            name="ck_productos_candidatos_nivel_demanda",
        ),
        CheckConstraint(
            "nivel_competencia_estimado IN ('alto', 'medio', 'bajo')",
            name="ck_productos_candidatos_nivel_competencia",
        ),
        CheckConstraint(
            "estado IN ('candidato', 'en_catalogo', 'descartado')",
            name="ck_productos_candidatos_estado",
        ),
        Index("ix_productos_candidatos_categoria", "categoria"),
        Index("ix_productos_candidatos_investigacion_id", "investigacion_id"),
        Index("ix_productos_candidatos_estado", "estado"),
    )

    nombre_producto: Mapped[str] = mapped_column(String(255), nullable=False)
    categoria: Mapped[str] = mapped_column(String(120), nullable=False)
    mercado_objetivo: Mapped[str] = mapped_column(String(2), nullable=False)
    precio_estimado_proveedor: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    precio_sugerido_venta: Mapped[float | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    nivel_demanda_estimado: Mapped[str] = mapped_column(String(10), nullable=False)
    nivel_competencia_estimado: Mapped[str] = mapped_column(String(10), nullable=False)
    fuentes_evidencia: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    riesgos_identificados: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list
    )
    estado: Mapped[str] = mapped_column(
        String(20), nullable=False, default="candidato", server_default="candidato"
    )
    investigacion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
