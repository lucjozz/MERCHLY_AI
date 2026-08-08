"""Pydantic schemas for the Agente de Analitica Basica.

Mirror exactly the Input/Output schema defined in the agent's technical
contract: ``docs/007-Agentes/05-Agente-Analitica-Basica.md``, secciones 2 y
3. Any change here must be reflected there first (documentación antes que
código).
"""

import re
from datetime import date, datetime, timedelta, timezone
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

_ISO_3166_1_ALPHA_2 = re.compile(r"^[A-Z]{2}$")

_RANGO_MAXIMO_DIAS = 365


class AgruparPor(str, Enum):
    """Valores permitidos para agrupar el resumen del catálogo (contrato,
    sección 2). Un valor fuera de esta lista se rechaza explícitamente —
    no hay default silencioso ante un valor inválido."""

    CATEGORIA = "categoria"
    ESTADO = "estado"
    NIVEL_DEMANDA_ESTIMADO = "nivel_demanda_estimado"
    NIVEL_COMPETENCIA_ESTIMADO = "nivel_competencia_estimado"


class AnaliticaInput(BaseModel):
    """Entrada de un reporte de analítica (contrato, sección 2).

    Attributes:
        fecha_desde: inicio del rango a analizar. Default: hace 30 días.
        fecha_hasta: fin del rango a analizar. Default: hoy.
        categoria: filtro opcional por categoría (sin filtro = todas).
        mercado_objetivo: filtro opcional, código ISO 3166-1 alpha-2.
        agrupar_por: criterio de agrupación del resumen del catálogo.
    """

    fecha_desde: date = Field(
        default_factory=lambda: date.today() - timedelta(days=30)
    )
    fecha_hasta: date = Field(default_factory=date.today)
    categoria: str | None = None
    mercado_objetivo: str | None = None
    agrupar_por: AgruparPor = AgruparPor.CATEGORIA

    @field_validator("mercado_objetivo")
    @classmethod
    def validar_mercado_objetivo(cls, valor: str | None) -> str | None:
        """Valida ISO 3166-1 alpha-2 si se provee (contrato, sección 2).

        A diferencia del Investigador de Producto, acá el campo es
        opcional: sin filtro significa "todos los mercados", no un error.
        """
        if valor is None:
            return None
        valor_normalizado = valor.strip().upper()
        if not _ISO_3166_1_ALPHA_2.match(valor_normalizado):
            raise ValueError(
                "mercado_objetivo debe ser un código ISO 3166-1 alpha-2 "
                "válido (ej. 'BO', 'MX', 'US')."
            )
        return valor_normalizado

    @model_validator(mode="after")
    def validar_rango_de_fechas(self) -> "AnaliticaInput":
        """Aplica las dos reglas de rango del contrato, sección 2:
        fecha_desde no puede ser posterior a fecha_hasta, y el rango no
        puede exceder 365 días."""
        if self.fecha_desde > self.fecha_hasta:
            raise ValueError(
                "fecha_desde no puede ser posterior a fecha_hasta."
            )
        if (self.fecha_hasta - self.fecha_desde).days > _RANGO_MAXIMO_DIAS:
            raise ValueError(
                f"El rango de fechas no puede exceder {_RANGO_MAXIMO_DIAS} "
                "días."
            )
        return self


class GrupoResumen(BaseModel):
    """Un grupo dentro del resumen agrupado del catálogo (contrato,
    sección 3)."""

    clave: str
    cantidad: int = Field(ge=0)
    porcentaje_del_total: float = Field(ge=0, le=100)


class ResumenCatalogo(BaseModel):
    """Resumen del catálogo de productos candidatos, agrupado según
    ``agrupar_por`` (contrato, sección 3)."""

    total_productos_candidatos: int = Field(ge=0)
    agrupado_por: AgruparPor
    grupos: list[GrupoResumen] = Field(default_factory=list)


class TasaConversionCatalogo(BaseModel):
    """Tasa de conversión de productos candidatos a catálogo real
    (contrato, sección 3)."""

    candidato: int = Field(ge=0)
    en_catalogo: int = Field(ge=0)
    descartado: int = Field(ge=0)
    tasa_candidato_a_en_catalogo: float = Field(ge=0, le=1)


class ActividadAgenteInvestigador(BaseModel):
    """Resumen de actividad del Agente Investigador de Producto en el
    período consultado (contrato, sección 3)."""

    total_investigaciones: int = Field(ge=0)
    promedio_productos_por_investigacion: float = Field(ge=0)
    categorias_mas_investigadas: list[str] = Field(default_factory=list)


class Periodo(BaseModel):
    """Rango de fechas efectivamente usado para generar el reporte
    (contrato, sección 3) — eco de la entrada, ya con los defaults
    resueltos."""

    fecha_desde: date
    fecha_hasta: date


class AnaliticaMetadata(BaseModel):
    """Metadata de una ejecución del reporte (contrato, sección 3)."""

    fecha_generacion_reporte: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    filtros_aplicados: dict = Field(default_factory=dict)


class AnaliticaOutput(BaseModel):
    """Salida completa de un reporte de analítica básica (contrato,
    sección 3)."""

    periodo: Periodo
    resumen_catalogo: ResumenCatalogo
    tasa_conversion_catalogo: TasaConversionCatalogo
    actividad_agente_investigador: ActividadAgenteInvestigador
    metadata: AnaliticaMetadata