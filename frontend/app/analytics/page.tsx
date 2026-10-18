import { obtenerReporteAnalitica } from "@/lib/api/analitica";
import { redirect } from "next/navigation";
import { SesionInvalidaError } from "@/lib/api/errores";
export const dynamic = "force-dynamic";

export default async function Analytics() {
  let reporte;
  let error: string | null = null;

  try {
    reporte = await obtenerReporteAnalitica();
    
    } catch (e) {
    if (e instanceof SesionInvalidaError) redirect("/login");
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  const conversion = reporte?.tasa_conversion_catalogo;
  const grupos = reporte?.resumen_catalogo.grupos ?? [];

  const embudo = conversion
    ? [
        { etiqueta: "Candidato", valor: conversion.candidato, color: "#E8B84B" },
        { etiqueta: "En catálogo", valor: conversion.en_catalogo, color: "#4ADE80" },
        { etiqueta: "Descartado", valor: conversion.descartado, color: "#7C8699" },
      ]
    : [];
  const maxEmbudo = Math.max(1, ...embudo.map((e) => e.valor));

  return (
    <div className="px-10 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#F5F7FA]">Analytics</h1>
        <p className="text-[#7C8699] mt-1">
          Métricas del catálogo y del trabajo del Investigador de Producto.
        </p>
      </header>

      {error && (
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {reporte && conversion && (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                Conversión a catálogo
              </p>
              <p className="text-3xl font-bold text-[#4ADE80]">
                {(conversion.tasa_candidato_a_en_catalogo * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                Productos analizados
              </p>
              <p className="text-3xl font-bold text-[#F5F7FA]">
                {reporte.resumen_catalogo.total_productos_candidatos}
              </p>
            </div>
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                Investigaciones
              </p>
              <p className="text-3xl font-bold text-[#3D7DD8]">
                {reporte.actividad_agente_investigador.total_investigaciones}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6">
              <h2 className="text-lg font-semibold text-[#F5F7FA] mb-5">
                Embudo de decisión
              </h2>
              <div className="space-y-4">
                {embudo.map((fila) => (
                  <div key={fila.etiqueta}>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="text-[#7C8699]">{fila.etiqueta}</span>
                      <span className="text-[#F5F7FA] font-medium">{fila.valor}</span>
                    </div>
                    <div className="h-2 rounded-full bg-[#0B0D12]">
                      <div
                        className="h-2 rounded-full transition-all duration-700"
                        style={{
                          width: `${(fila.valor / maxEmbudo) * 100}%`,
                          backgroundColor: fila.color,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6">
              <h2 className="text-lg font-semibold text-[#F5F7FA] mb-5">
                Productos por categoría
              </h2>
              {grupos.length === 0 && (
                <p className="text-[#5B6272] text-sm">Todavía no hay datos.</p>
              )}
              <div className="space-y-4">
                {grupos.map((grupo) => (
                  <div key={grupo.clave}>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="text-[#F5F7FA]">{grupo.clave}</span>
                      <span className="text-[#7C8699]">
                        {grupo.cantidad} · {grupo.porcentaje_del_total}%
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-[#0B0D12]">
                      <div
                        className="h-2 rounded-full bg-[#3D7DD8] transition-all duration-700"
                        style={{ width: `${grupo.porcentaje_del_total}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}