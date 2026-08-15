import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import Link from "next/link";

interface PageProps {
  searchParams: Promise<{ categoria?: string; estado?: string }>;
}

const ESTILO_ESTADO: Record<string, string> = {
  candidato: "bg-[#3A2E12] text-[#E8B84B] border border-[#4A3A17]",
  en_catalogo: "bg-[#123420] text-[#4ADE80] border border-[#1B4A2C]",
  descartado: "bg-[#1C2029] text-[#7C8699] border border-[#242938]",
};

export default async function Home({ searchParams }: PageProps) {
  const filtros = await searchParams;
  let datos;
  let error: string | null = null;

  try {
    datos = await listarProductosCandidatos(
      1,
      20,
      filtros.categoria,
      filtros.estado
    );
  } catch {
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  return (
    <div className="min-h-screen bg-[#0B0D12]">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <header className="mb-10 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-[#F5F7FA] tracking-tight">
              Panel General
            </h1>
            <p className="text-[#7C8699] mt-1 text-sm">
              Productos candidatos descubiertos por el Investigador de Producto
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-[#7C8699] font-mono">
            <span className="w-2 h-2 rounded-full bg-[#3D7DD8]" />
            MERCHLY AI
          </div>
        </header>

        <form className="flex flex-wrap gap-3 mb-8 bg-[#12151C] border border-[#1F2430] p-4 rounded-lg">
          <input
            type="text"
            name="categoria"
            placeholder="Filtrar por categoría"
            defaultValue={filtros.categoria}
            className="bg-[#0B0D12] border border-[#242938] text-[#F5F7FA] placeholder-[#5B6272] rounded-md px-3 py-2 text-sm flex-1 min-w-[180px] outline-none focus:border-[#3D7DD8] focus:ring-1 focus:ring-[#3D7DD8] transition-colors"
          />
          <select
            name="estado"
            defaultValue={filtros.estado ?? ""}
            className="bg-[#0B0D12] border border-[#242938] text-[#F5F7FA] rounded-md px-3 py-2 text-sm outline-none focus:border-[#3D7DD8] focus:ring-1 focus:ring-[#3D7DD8] transition-colors"
          >
            <option value="">Todos los estados</option>
            <option value="candidato">Candidato</option>
            <option value="en_catalogo">En catálogo</option>
            <option value="descartado">Descartado</option>
          </select>
          <button
            type="submit"
            className="bg-[#1E3A5F] hover:bg-[#28507F] border border-[#2B4A73] text-white px-5 py-2 rounded-md text-sm font-medium transition-colors"
          >
            Filtrar
          </button>
        </form>

        {error && (
          <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm">
            {error}
          </div>
        )}

        {datos && datos.productos.length === 0 && (
          <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-12 text-center text-[#7C8699] text-sm">
            No hay productos candidatos todavía.
          </div>
        )}

        {datos && datos.productos.length > 0 && (
          <div className="bg-[#12151C] border border-[#1F2430] rounded-lg overflow-hidden">
            <table className="w-full border-collapse text-sm">
              <thead className="bg-[#0B0D12] border-b border-[#1F2430]">
                <tr className="text-left text-[#7C8699]">
                  <th className="p-3 font-medium">Producto</th>
                  <th className="p-3 font-medium">Categoría</th>
                  <th className="p-3 font-medium">Estado</th>
                  <th className="p-3 font-medium">Demanda</th>
                  <th className="p-3 font-medium">Competencia</th>
                </tr>
              </thead>
              <tbody>
                {datos.productos.map((producto) => (
                  <tr
                    key={producto.id}
                    className="border-t border-[#1F2430] hover:bg-[#161922] transition-colors"
                  >
                    <td className="p-3 font-medium">
                      <Link
                        href={`/productos/${producto.id}`}
                        className="text-[#F5F7FA] hover:text-[#3D7DD8] transition-colors"
                      >
                        {producto.nombre_producto}
                      </Link>
                    </td>
                    <td className="p-3 text-[#7C8699] font-mono text-xs">
                      {producto.categoria}
                    </td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          ESTILO_ESTADO[producto.estado] ??
                          "bg-[#1C2029] text-[#7C8699] border border-[#242938]"
                        }`}
                      >
                        {producto.estado}
                      </span>
                    </td>
                    <td className="p-3 text-[#7C8699]">
                      {producto.nivel_demanda_estimado}
                    </td>
                    <td className="p-3 text-[#7C8699]">
                      {producto.nivel_competencia_estimado}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}