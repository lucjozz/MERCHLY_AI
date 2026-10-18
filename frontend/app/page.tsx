import { obtenerReporteAnalitica } from "@/lib/api/analitica";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import Link from "next/link";
import { Package, CircleCheck, Zap, Bot } from "lucide-react";
import { redirect } from "next/navigation";
import { SesionInvalidaError } from "@/lib/api/errores";

export const dynamic = "force-dynamic";

export default async function Dashboard() {
  let reporte;
  let recientes;
  let error: string | null = null;

  try {
    [reporte, recientes] = await Promise.all([
      obtenerReporteAnalitica(),
      listarProductosCandidatos(1, 5, undefined, "candidato"),
    ]);
    } catch (e) {
    if (e instanceof SesionInvalidaError) redirect("/login");
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  return (
    <div className="px-10 py-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[#F5F7FA]">Buenos días</h1>
          <p className="text-[#7C8699] mt-1">
            Aquí está el estado actual de Merchly AI.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#4ADE80] opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#4ADE80]" />
          </span>
          <span className="text-[#7C8699]">SISTEMA OPERATIVO</span>
        </div>
      </header>

      {error && (
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {reporte && (
        <>
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <div className="flex items-center gap-2 text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                <Package className="h-4 w-4" aria-hidden="true" />
                Productos
              </div>
              <p className="text-3xl font-bold text-[#F5F7FA]">
                {reporte.resumen_catalogo.total_productos_candidatos}
              </p>
            </div>

            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <div className="flex items-center gap-2 text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                <CircleCheck className="h-4 w-4" aria-hidden="true" />
                En Catálogo
              </div>
              <p className="text-3xl font-bold text-[#4ADE80]">
                {reporte.tasa_conversion_catalogo.en_catalogo}
              </p>
            </div>

            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <div className="flex items-center gap-2 text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                <Zap className="h-4 w-4" aria-hidden="true" />
                Pendientes
              </div>
              <p className="text-3xl font-bold text-[#E8B84B]">
                {reporte.tasa_conversion_catalogo.candidato}
              </p>
            </div>

            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <div className="flex items-center gap-2 text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                <Bot className="h-4 w-4" aria-hidden="true" />
                Agentes
              </div>
              <p className="text-3xl font-bold text-[#3D7DD8]">3 / 3</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6">
              <h2 className="text-lg font-semibold text-[#F5F7FA] mb-1">
                Requiere tu atención
              </h2>
              <p className="text-[#E8B84B] text-sm mb-4">
                {reporte.tasa_conversion_catalogo.candidato} decisiones pendientes
              </p>

              {recientes && recientes.productos.length === 0 && (
                <p className="text-[#5B6272] text-sm">
                  No hay productos pendientes de revisión.
                </p>
              )}

              <div className="space-y-3">
                {recientes?.productos.map((producto) => (
                  <div
                    key={producto.id}
                    className="bg-[#0B0D12] border border-[#1F2430] rounded-md p-4 flex items-center justify-between"
                  >
                    <div>
                      <p className="text-[#E8B84B] text-xs font-medium mb-1">
                        NUEVO PRODUCTO
                      </p>
                      <p className="text-[#F5F7FA] font-medium">
                        {producto.nombre_producto}
                      </p>
                      <p className="text-[#7C8699] text-xs mt-1">
                        Demanda {producto.nivel_demanda_estimado} · Competencia{" "}
                        {producto.nivel_competencia_estimado}
                      </p>
                    </div>
                    <Link
                      href={`/productos/${producto.id}`}
                      className="text-[#3D7DD8] text-sm font-medium hover:underline whitespace-nowrap ml-4"
                    >
                      Ver análisis →
                    </Link>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6">
              <h2 className="text-lg font-semibold text-[#F5F7FA] mb-4">
                Categorías más investigadas
              </h2>
              {reporte.actividad_agente_investigador.categorias_mas_investigadas
                .length === 0 && (
                <p className="text-[#5B6272] text-sm">Todavía no hay actividad.</p>
              )}
              <div className="space-y-3">
                {reporte.actividad_agente_investigador.categorias_mas_investigadas.map(
                  (categoria, i) => (
                    <div key={categoria} className="flex items-center gap-3">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#3D7DD8]" />
                      <p className="text-[#F5F7FA] text-sm">{categoria}</p>
                    </div>
                  )
                )}
              </div>
              <div className="border-t border-[#1F2430] mt-5 pt-4">
                <p className="text-[#7C8699] text-xs">
                  {reporte.actividad_agente_investigador.total_investigaciones}{" "}
                  investigaciones ·{" "}
                  {reporte.actividad_agente_investigador.promedio_productos_por_investigacion}{" "}
                  productos en promedio
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}