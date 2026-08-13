"""Agente de Analitica Basica — orquestacion.

Implementa el ciclo descrito en el contrato tecnico
(``docs/007-Agentes/05-Agente-Analitica-Basica.md``): validar entrada,
consultar ``productos_candidatos`` (solo lectura, sin proveedor externo),
y devolver el reporte estructurado.
"""

from datetime import datetime, timezone

from sqlalchemy import func, select
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


class AgenteAnaliticaBasica:
    """Orquesta la generacion de un reporte de analitica basica.

    A diferencia del Agente Investigador de Producto, no depende de un
    proveedor externo intercambiable: consulta directamente
    ``productos_candidatos`` via SQLAlchemy (contrato, seccion 4 —
    unica herramienta permitida).

    Attributes:
        db_session: sesion async de SQLAlchemy para consultar (solo
            lectura — nunca escribe, contrato seccion 4).
    """

    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def ejecutar(self, entrada: AnaliticaInput) -> AnaliticaOutput:
        """Genera el reporte completo (contrato, seccion 3)."""
        # Aca vamos a ir agregando cada consulta, paso a paso
        periodo = Periodo(
            fecha_desde=entrada.fecha_desde,
            fecha_hasta=entrada.fecha_hasta,
        )
        columna_agrupacion = getattr(ProductoCandidato, entrada.agrupar_por.value)

        condiciones = [
            ProductoCandidato.creado_en >= entrada.fecha_desde,
            ProductoCandidato.creado_en <= entrada.fecha_hasta,
        ]

        if entrada.categoria:
            condiciones.append(ProductoCandidato.categoria == entrada.categoria)
        if entrada.mercado_objetivo:
            condiciones.append(
                ProductoCandidato.mercado_objetivo == entrada.mercado_objetivo
            )

        consulta_agrupada = (
            select(columna_agrupacion, func.count().label("cantidad"))
            .where(*condiciones)
            .group_by(columna_agrupacion)
        )
        resultado_agrupado = await self.db_session.execute(consulta_agrupada)
        filas_agrupadas = resultado_agrupado.all()

        total_productos = sum(fila.cantidad for fila in filas_agrupadas)

        grupos = [
            GrupoResumen(
                clave=fila[0],
                cantidad=fila.cantidad,
                porcentaje_del_total=(
                    round(fila.cantidad / total_productos * 100, 2)
                    if total_productos > 0
                    else 0
                ),
            )
            for fila in filas_agrupadas
        ]

        resumen_catalogo = ResumenCatalogo(
            total_productos_candidatos=total_productos,
            agrupado_por=entrada.agrupar_por,
            grupos=grupos,
        )
        consulta_estados = (
            select(ProductoCandidato.estado, func.count().label("cantidad"))
            .where(*condiciones)
            .group_by(ProductoCandidato.estado)
        )
        resultado_estados = await self.db_session.execute(consulta_estados)
        cantidad_por_estado = {
            fila.estado: fila.cantidad for fila in resultado_estados.all()
        }

        candidato = cantidad_por_estado.get("candidato", 0)
        en_catalogo = cantidad_por_estado.get("en_catalogo", 0)
        descartado = cantidad_por_estado.get("descartado", 0)
        total_para_tasa = candidato + en_catalogo + descartado

        tasa_conversion_catalogo = TasaConversionCatalogo(
            candidato=candidato,
            en_catalogo=en_catalogo,
            descartado=descartado,
            tasa_candidato_a_en_catalogo=(
                round(en_catalogo / total_para_tasa, 4)
                if total_para_tasa > 0
                else 0
            ),
        )  
        consulta_investigaciones = select(
            ProductoCandidato.investigacion_id
        ).where(*condiciones)
        resultado_investigaciones = await self.db_session.execute(
            consulta_investigaciones
        )
        ids_investigaciones = [
            fila.investigacion_id for fila in resultado_investigaciones.all()
        ]
        total_investigaciones = len(set(ids_investigaciones))

        promedio_productos_por_investigacion = (
            round(len(ids_investigaciones) / total_investigaciones, 2)
            if total_investigaciones > 0
            else 0
        )

        consulta_categorias = (
            select(ProductoCandidato.categoria, func.count().label("cantidad"))
            .where(*condiciones)
            .group_by(ProductoCandidato.categoria)
            .order_by(func.count().desc())
        )
        resultado_categorias = await self.db_session.execute(consulta_categorias)
        categorias_mas_investigadas = [
            fila.categoria for fila in resultado_categorias.all()
        ]

        actividad_agente_investigador = ActividadAgenteInvestigador(
            total_investigaciones=total_investigaciones,
            promedio_productos_por_investigacion=promedio_productos_por_investigacion,
            categorias_mas_investigadas=categorias_mas_investigadas,
        )
        metadata = AnaliticaMetadata(
            fecha_generacion_reporte=datetime.now(timezone.utc).isoformat(),
            filtros_aplicados={
                "fecha_desde": entrada.fecha_desde.isoformat(),
                "fecha_hasta": entrada.fecha_hasta.isoformat(),
                "categoria": entrada.categoria,
                "mercado_objetivo": entrada.mercado_objetivo,
                "agrupar_por": entrada.agrupar_por.value,
            },
        )

        return AnaliticaOutput(
            periodo=periodo,
            resumen_catalogo=resumen_catalogo,
            tasa_conversion_catalogo=tasa_conversion_catalogo,
            actividad_agente_investigador=actividad_agente_investigador,
            metadata=metadata,
        )