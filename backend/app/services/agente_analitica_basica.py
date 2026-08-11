"""Agente de Analítica Básica — orquestación.

Implementa el contrato técnico en
``docs/007-Agentes/05-Agente-Analitica-Basica.md``: agente de solo
lectura (Nivel de permiso 0) que agrega y resume los datos ya existentes
en ``productos_candidatos``, sin generar datos nuevos ni escribir nada.

Nota de diseño: la agregación se hace en Python sobre el resultado ya
filtrado, no con ``GROUP BY`` en SQL. Es la opción más simple y más fácil
de testear sin infraestructura real, razonable mientras el catálogo es
pequeño (no hay tienda operando todavía, Fase 2 pendiente — ver el
contrato, "Alcance deliberadamente acotado"). Si el volumen de
``productos_candidatos`` crece de forma significativa, esto debería
migrarse a agregación en SQL por rendimiento.
"""

import logging
from collections import Counter
from datetime import datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.producto_candidato import ProductoCandidato
from app.schemas.analitica_basica import (
    ActividadAgenteInvestigador,
    AnaliticaInput,
    AnaliticaMetadata,
    AnaliticaOutput,
    GrupoResumen,
    Periodo,
    ResumenCatalogo,
    TasaConversionCatalogo,
)

logger = logging.getLogger(__name__)

# Contrato, sección 8: "máximo 1 reintento, sin backoff" — a diferencia
# del Investigador de Producto, esta es una consulta de solo lectura
# sobre infraestructura propia, no una fuente externa.
MAX_REINTENTOS = 1

_ESTADOS_CONOCIDOS = ("candidato", "en_catalogo", "descartado")
_TOP_CATEGORIAS = 5


class AnaliticaBasicaError(Exception):
    """Se lanza cuando la consulta a base de datos falla tras reintentar."""


class AgenteAnaliticaBasica:
    """Orquesta la generación de un reporte de analítica básica.

    Attributes:
        db_session: sesión async de SQLAlchemy, de solo lectura para este
            agente (contrato, sección 4 — ninguna escritura permitida).
    """

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def ejecutar(self, entrada: AnaliticaInput) -> AnaliticaOutput:
        """Genera un reporte de analítica básica.

        Args:
            entrada: filtros ya validados por ``AnaliticaInput``.

        Returns:
            AnaliticaOutput: el reporte completo. Un resultado sin filas
            es una respuesta válida (contrato, sección 8), no un error.

        Raises:
            AnaliticaBasicaError: si la consulta falla tras el reintento.
        """
        filas = await self._consultar_con_reintento(entrada)

        return AnaliticaOutput(
            periodo=Periodo(fecha_desde=entrada.fecha_desde, fecha_hasta=entrada.fecha_hasta),
            resumen_catalogo=self._resumen_catalogo(filas, entrada),
            tasa_conversion_catalogo=self._tasa_conversion(filas),
            actividad_agente_investigador=self._actividad_investigador(filas),
            metadata=AnaliticaMetadata(filtros_aplicados=entrada.model_dump(mode="json")),
        )

    async def _consultar_con_reintento(
        self, entrada: AnaliticaInput
    ) -> list[ProductoCandidato]:
        """Ejecuta la consulta filtrada, con 1 reintento sin backoff."""
        consulta = self._construir_consulta(entrada)
        ultimo_error: Exception | None = None

        for intento in range(MAX_REINTENTOS + 1):
            try:
                resultado = await self.db_session.execute(consulta)
                return list(resultado.scalars().all())
            except Exception as error:
                ultimo_error = error
                logger.warning(
                    "Fallo al consultar productos_candidatos para analítica "
                    "(intento %s/%s): %s",
                    intento + 1,
                    MAX_REINTENTOS + 1,
                    error,
                )

        logger.error(
            "La consulta de analítica básica falló tras agotar reintentos: %s",
            ultimo_error,
        )
        raise AnaliticaBasicaError(
            f"No se pudo consultar productos_candidatos: {ultimo_error}"
        ) from ultimo_error

    @staticmethod
    def _construir_consulta(entrada: AnaliticaInput):
        """Arma el SELECT filtrado (contrato, sección 4: solo lectura)."""
        inicio = datetime.combine(entrada.fecha_desde, time.min, tzinfo=timezone.utc)
        fin = datetime.combine(entrada.fecha_hasta, time.max, tzinfo=timezone.utc)

        consulta = select(ProductoCandidato).where(
            ProductoCandidato.eliminado_en.is_(None),
            ProductoCandidato.creado_en >= inicio,
            ProductoCandidato.creado_en <= fin,
        )
        if entrada.categoria:
            consulta = consulta.where(ProductoCandidato.categoria == entrada.categoria)
        if entrada.mercado_objetivo:
            consulta = consulta.where(
                ProductoCandidato.mercado_objetivo == entrada.mercado_objetivo
            )
        return consulta

    @staticmethod
    def _resumen_catalogo(
        filas: list[ProductoCandidato], entrada: AnaliticaInput
    ) -> ResumenCatalogo:
        """Agrupa las filas según ``entrada.agrupar_por`` (contrato, sección 3)."""
        total = len(filas)
        claves = [getattr(fila, entrada.agrupar_por.value) for fila in filas]
        conteo = Counter(claves)

        grupos = [
            GrupoResumen(
                clave=clave,
                cantidad=cantidad,
                porcentaje_del_total=round((cantidad / total) * 100, 2) if total else 0.0,
            )
            for clave, cantidad in sorted(conteo.items(), key=lambda item: -item[1])
        ]

        return ResumenCatalogo(
            total_productos_candidatos=total,
            agrupado_por=entrada.agrupar_por,
            grupos=grupos,
        )

    @staticmethod
    def _tasa_conversion(filas: list[ProductoCandidato]) -> TasaConversionCatalogo:
        """Cuenta filas por estado y calcula la tasa de conversión."""
        conteo_por_estado = Counter(fila.estado for fila in filas)
        candidato = conteo_por_estado.get("candidato", 0)
        en_catalogo = conteo_por_estado.get("en_catalogo", 0)
        descartado = conteo_por_estado.get("descartado", 0)
        total = candidato + en_catalogo + descartado

        return TasaConversionCatalogo(
            candidato=candidato,
            en_catalogo=en_catalogo,
            descartado=descartado,
            tasa_candidato_a_en_catalogo=round(en_catalogo / total, 4) if total else 0.0,
        )

    @staticmethod
    def _actividad_investigador(
        filas: list[ProductoCandidato],
    ) -> ActividadAgenteInvestigador:
        """Resume la actividad del Investigador de Producto sobre estas filas."""
        investigaciones = {fila.investigacion_id for fila in filas}
        total_investigaciones = len(investigaciones)
        total_productos = len(filas)
        promedio = (
            round(total_productos / total_investigaciones, 2)
            if total_investigaciones
            else 0.0
        )

        conteo_categorias = Counter(fila.categoria for fila in filas)
        categorias_mas_investigadas = [
            categoria
            for categoria, _ in sorted(
                conteo_categorias.items(), key=lambda item: -item[1]
            )[:_TOP_CATEGORIAS]
        ]

        return ActividadAgenteInvestigador(
            total_investigaciones=total_investigaciones,
            promedio_productos_por_investigacion=promedio,
            categorias_mas_investigadas=categorias_mas_investigadas,
        )
