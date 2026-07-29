"""Pydantic schemas for the Agente Investigador de Producto.

Mirror exactly the Input/Output schema defined in the agent's technical
contract: ``docs/007-Agentes/03-Agente-Investigador-de-Producto.md``,
secciones 2 y 3. Any change here must be reflected there first
(documentación antes que código).
"""

import re
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

_ISO_3166_1_ALPHA_2 = re.compile(r"^[A-Z]{2}$")

# Lista provisional de categorías prohibidas (contrato, sección 7).
# Se mantiene deliberadamente corta y explícita: es más seguro rechazar de
# más y requerir revisión humana que adivinar. Debe evolucionar junto con
# una política formal de categorías reguladas/prohibidas (docs/013-Seguridad
# o un anexo de 000-Constitucion/03-Valores.md), todavía no redactada.
CATEGORIAS_PROHIBIDAS = frozenset(
    {
        "armas",
        "explosivos",
        "drogas",
        "sustancias controladas",
        "medicamentos regulados",
        "vida silvestre en peligro",
        "contenido sexual explícito",
        "productos falsificados",
    }
)


class NivelEstimado(str, Enum):
    """Escala usada tanto para demanda como para competencia estimada."""

    ALTO = "alto"
    MEDIO = "medio"
    BAJO = "bajo"


class InvestigacionInput(BaseModel):
    """Entrada de una investigación (contrato, sección 2).

    Attributes:
        categoria: nicho o categoría de e-commerce a investigar.
        mercado_objetivo: código ISO 3166-1 alpha-2 del mercado objetivo.
        presupuesto_max_producto: presupuesto máximo por producto, en USD.
        excluir_marcas: marcas a excluir de los resultados.
        cantidad_resultados: cantidad de productos a devolver (máx. 50).
    """

    categoria: str = Field(min_length=1)
    mercado_objetivo: str
    presupuesto_max_producto: float | None = Field(default=None, gt=0)
    excluir_marcas: list[str] = Field(default_factory=list)
    cantidad_resultados: int = Field(default=10, gt=0)

    @field_validator("mercado_objetivo")
    @classmethod
    def validar_mercado_objetivo(cls, valor: str) -> str:
        """Valida que sea un código ISO 3166-1 alpha-2 (contrato, sección 2)."""
        valor_normalizado = valor.strip().upper()
        if not _ISO_3166_1_ALPHA_2.match(valor_normalizado):
            raise ValueError(
                "mercado_objetivo debe ser un código ISO 3166-1 alpha-2 "
                "válido (ej. 'BO', 'MX', 'US')."
            )
        return valor_normalizado

    @field_validator("categoria")
    @classmethod
    def validar_categoria_no_prohibida(cls, valor: str) -> str:
        """Rechaza categorías prohibidas (contrato, sección 7)."""
        if valor.strip().lower() in CATEGORIAS_PROHIBIDAS:
            raise ValueError(
                f"La categoría '{valor}' está prohibida por política de la "
                "empresa y no puede investigarse."
            )
        return valor

    @field_validator("cantidad_resultados")
    @classmethod
    def truncar_cantidad_resultados(cls, valor: int) -> int:
        """Trunca a 50 en vez de rechazar la solicitud (contrato, sección 2)."""
        return min(valor, 50)


class ProductoCandidatoOutput(BaseModel):
    """Un producto recomendado (contrato, sección 3)."""

    nombre_producto: str
    categoria: str
    precio_estimado_proveedor: float | None = None
    precio_sugerido_venta: float | None = None
    nivel_demanda_estimado: NivelEstimado
    nivel_competencia_estimado: NivelEstimado
    fuentes_evidencia: list[str] = Field(default_factory=list)
    riesgos_identificados: list[str] = Field(default_factory=list)


class InvestigacionMetadata(BaseModel):
    """Metadata de una ejecución de investigación (contrato, sección 3)."""

    categoria_consultada: str
    mercado_objetivo: str
    fecha_investigacion: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    total_productos_evaluados: int
    total_productos_devueltos: int
    confianza: Literal["normal", "baja"] = "normal"
    investigacion_id: uuid.UUID = Field(default_factory=uuid.uuid4)


class InvestigacionOutput(BaseModel):
    """Salida completa de una investigación (contrato, sección 3)."""

    productos: list[ProductoCandidatoOutput]
    metadata: InvestigacionMetadata
