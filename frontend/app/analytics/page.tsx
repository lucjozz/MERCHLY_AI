import { obtenerReporteAnalitica } from "@/lib/api/analitica";
import { BarChart3, Percent, Package, Search, PieChart } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Card, { TituloCard } from "@/components/ui/Card";
import Metrica from "@/components/ui/Metrica";
import EmptyState from "@/components/ui/EmptyState";
import Alerta from "@/components/ui/Alerta";
import { PISTA_BARRA } from "@/components/ui/estilos";
import { ESTADOS } from "@/lib/etiquetas";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

export default async function Analytics() {
  let reporte;
  let error: string | null = null;

  try {
    reporte = await obtenerReporteAnalitica();
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  const conversion = reporte?.tasa_conversion_catalogo;
  const grupos = reporte?.resumen_catalogo.grupos ?? [];

  const embudo = conversion
    ? [
        { etiqueta: ESTADOS.candidato.etiqueta, valor: conversion.candidato, color: "bg-ambar" },
        { etiqueta: ESTADOS.en_catalogo.etiqueta, valor: conversion.en_catalogo, color: "bg-verde" },
        { etiqueta: ESTADOS.descartado.etiqueta, valor: conversion.descartado, color: "bg-texto-2" },
      ]
    : [];
  const maxEmbudo = Math.max(1, ...embudo.map((e) => e.valor));
  const sinDatos = (reporte?.resumen_catalogo.total_productos_candidatos ?? 0) === 0;

  return (
    <>
      <PageHeader
        titulo="Analytics"
        icono={BarChart3}
        descripcion="Cómo viene tu catálogo y el trabajo de la IA en los últimos 30 días."
        ayuda="Mirá cuántos productos encontró la IA, cuántos aprobaste y en qué categorías estás buscando más. Son datos reales de tu cuenta."
      />

      {error && <Alerta>{error}</Alerta>}

      {reporte && conversion && (
        <div className="space-y-6">
          <div className="grid gap-3 sm:grid-cols-3 sm:gap-4">
            <Metrica
              etiqueta="Pasaron al catálogo"
              valor={`${(conversion.tasa_candidato_a_en_catalogo * 100).toFixed(1)}%`}
              icono={Percent}
              color="verde"
              detalle="De cada 100 productos sugeridos, cuántos aprobaste"
            />
            <Metrica
              etiqueta="Productos analizados"
              valor={reporte.resumen_catalogo.total_productos_candidatos}
              icono={Package}
              detalle="Sugeridos por la IA"
              retraso={60}
            />
            <Metrica
              etiqueta="Búsquedas con IA"
              valor={reporte.actividad_agente_investigador.total_investigaciones}
              icono={Search}
              color="azul"
              detalle="Categorías que le pediste investigar"
              retraso={120}
            />
          </div>

          {sinDatos ? (
            <EmptyState
              icono={PieChart}
              titulo="Todavía no hay datos para graficar"
              descripcion="Cuando busques productos con IA y tomes decisiones, acá vas a ver cómo evoluciona tu catálogo."
              accion={{ href: "/productos", texto: "Buscar productos" }}
            />
          ) : (
            <div className="grid gap-6 lg:grid-cols-2">
              <Card as="section" aria-label="Embudo de decisión">
                <TituloCard descripcion="En qué estado están los productos que sugirió la IA.">
                  ¿Qué pasó con cada producto?
                </TituloCard>
                <div className="space-y-5">
                  {embudo.map((fila) => (
                    <div key={fila.etiqueta}>
                      <div className="mb-1.5 flex justify-between text-sm">
                        <span className="text-texto-2">{fila.etiqueta}</span>
                        <span className="font-semibold tabular-nums text-texto">{fila.valor}</span>
                      </div>
                      <div className={PISTA_BARRA}>
                        <div
                          className={`h-full rounded-full transition-[width] duration-700 ${fila.color}`}
                          style={{ width: `${(fila.valor / maxEmbudo) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card as="section" aria-label="Productos por categoría">
                <TituloCard descripcion="Dónde se concentran tus oportunidades.">
                  Productos por categoría
                </TituloCard>
                {grupos.length === 0 && (
                  <p className="text-sm text-texto-2">Todavía no hay datos.</p>
                )}
                <div className="space-y-5">
                  {grupos.map((grupo) => (
                    <div key={grupo.clave}>
                      <div className="mb-1.5 flex justify-between gap-3 text-sm">
                        <span className="min-w-0 truncate text-texto">{grupo.clave}</span>
                        <span className="shrink-0 tabular-nums text-texto-2">
                          {grupo.cantidad} · {grupo.porcentaje_del_total}%
                        </span>
                      </div>
                      <div className={PISTA_BARRA}>
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-acento-boton to-acento-claro transition-[width] duration-700"
                          style={{ width: `${grupo.porcentaje_del_total}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          )}
        </div>
      )}
    </>
  );
}
