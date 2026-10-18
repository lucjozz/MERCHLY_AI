import Link from "next/link";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";

export const dynamic = "force-dynamic";

const ETIQUETA_DECISION: Record<string, { texto: string; estilo: string }> = {
  en_catalogo: {
    texto: "Aprobado",
    estilo: "bg-[#123420] text-[#4ADE80] border border-[#1B4A2C]",
  },
  descartado: {
    texto: "Descartado",
    estilo: "bg-[#1C2029] text-[#7C8699] border border-[#242938]",
  },
};

function formatearFecha(iso: string): string {
  return new Date(iso).toLocaleString("es-BO", {
    timeZone: "America/La_Paz",
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default async function Decisiones() {
  let aprobados;
  let descartados;
  let error: string | null = null;

  try {
    [aprobados, descartados] = await Promise.all([
      listarProductosCandidatos(1, 100, undefined, "en_catalogo"),
      listarProductosCandidatos(1, 100, undefined, "descartado"),
    ]);
  } catch {
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  const decididos = [
    ...(aprobados?.productos ?? []),
    ...(descartados?.productos ?? []),
  ].sort(
    (a, b) => new Date(b.creado_en).getTime() - new Date(a.creado_en).getTime()
  );

  const totalAprobados = aprobados?.total ?? 0;
  const totalDescartados = descartados?.total ?? 0;
  const totalDecididos = totalAprobados + totalDescartados;
  const tasa =
    totalDecididos > 0 ? Math.round((totalAprobados / totalDecididos) * 100) : 0;

  return (
    <div className="px-10 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#F5F7FA]">Decisiones</h1>
        <p className="text-[#7C8699] mt-1">
          Productos sobre los que una persona ya decidió. Cada decisión queda
          registrada con su motivo, evidencia y responsable.
        </p>
      </header>

      {error && (
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {!error && (
        <>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                Aprobados
              </p>
              <p className="text-3xl font-bold text-[#4ADE80]">{totalAprobados}</p>
            </div>
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                Descartados
              </p>
              <p className="text-3xl font-bold text-[#7C8699]">{totalDescartados}</p>
            </div>
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-5">
              <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                Tasa de aprobación
              </p>
              <p className="text-3xl font-bold text-[#F5F7FA]">{tasa}%</p>
            </div>
          </div>

          {decididos.length === 0 && (
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-12 text-center">
              <p className="text-[#F5F7FA] text-sm mb-1">
                Todavía no hay decisiones.
              </p>
              <p className="text-[#7C8699] text-xs mb-4">
                Aprobá o descartá un producto desde su pantalla de detalle.
              </p>
              <Link
                href="/productos"
                className="text-[#3D7DD8] text-sm font-medium hover:underline"
              >
                Ir a Productos →
              </Link>
            </div>
          )}

          {decididos.length > 0 && (
            <div className="bg-[#12151C] border border-[#1F2430] rounded-lg overflow-hidden">
              <table className="w-full border-collapse text-sm">
                <thead className="border-b border-[#1F2430]">
                  <tr className="text-left text-[#7C8699] text-xs uppercase tracking-wide">
                    <th className="p-4 font-medium">Producto</th>
                    <th className="p-4 font-medium">Categoría</th>
                    <th className="p-4 font-medium">Decisión</th>
                    <th className="p-4 font-medium">Detectado</th>
                  </tr>
                </thead>
                <tbody>
                  {decididos.map((producto) => {
                    const etiqueta = ETIQUETA_DECISION[producto.estado] ?? {
                      texto: producto.estado,
                      estilo: "bg-[#1C2029] text-[#7C8699] border border-[#242938]",
                    };
                    return (
                      <tr
                        key={producto.id}
                        className="border-t border-[#1F2430] hover:bg-[#161922] transition-colors"
                      >
                        <td className="p-0 font-medium">
                          <Link
                            href={`/productos/${producto.id}`}
                            className="block p-4 text-[#F5F7FA] hover:text-[#3D7DD8] transition-colors"
                          >
                            {producto.nombre_producto}
                          </Link>
                        </td>
                        <td className="p-4 text-[#7C8699]">{producto.categoria}</td>
                        <td className="p-4">
                          <span
                            className={`px-2.5 py-1 rounded-md text-xs font-medium ${etiqueta.estilo}`}
                          >
                            {etiqueta.texto}
                          </span>
                        </td>
                        <td className="p-4 text-[#7C8699] text-xs">
                          {formatearFecha(producto.creado_en)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}