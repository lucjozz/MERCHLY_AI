import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import Link from "next/link";
import BuscarProductos from "@/components/BuscarProductos";
import BotonEliminar from "@/components/BotonEliminar";

interface PageProps {
  searchParams: Promise<{ categoria?: string; estado?: string }>;
}

const ESTILO_ESTADO: Record<string, string> = {
  candidato: "bg-[#3A2E12] text-[#E8B84B] border border-[#4A3A17]",
  en_catalogo: "bg-[#123420] text-[#4ADE80] border border-[#1B4A2C]",
  descartado: "bg-[#1C2029] text-[#7C8699] border border-[#242938]",
};

export default async function Productos({ searchParams }: PageProps) {
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
    <div className="px-10 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#F5F7FA]">Productos</h1>
        <p className="text-[#7C8699] mt-1">
          Oportunidades descubiertas por el Investigador de Producto.
        </p>
      </header>

      <BuscarProductos />

      <form className="flex flex-wrap gap-3 mb-6 bg-[#12151C] border border-[#1F2430] p-4 rounded-lg">
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
          className="bg-[#1E3A5F] hover:bg-[#28507F] border border-[#2B4A73] text-white px-5 py-2 rounded-md text-sm font-medium transition-all hover:scale-[1.02]"
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
        <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-12 text-center">
          <p className="text-[#7C8699] text-sm">
            No hay productos candidatos todavía.
          </p>
          <p className="text-[#5B6272] text-xs mt-1">
            Usá el buscador de arriba para investigar tu primera categoría.
          </p>
        </div>
      )}

      {datos && datos.productos.length > 0 && (
        <>
          <div className="bg-[#12151C] border border-[#1F2430] rounded-lg overflow-hidden">
            <table className="w-full border-collapse text-sm">
              <thead className="border-b border-[#1F2430]">
                <tr className="text-left text-[#7C8699] text-xs uppercase tracking-wide">
                  <th className="p-4 font-medium">Producto</th>
                  <th className="p-4 font-medium">Categoría</th>
                  <th className="p-4 font-medium">Estado</th>
                  <th className="p-4 font-medium">Demanda</th>
                  <th className="p-4 font-medium">Competencia</th>
                  <th className="p-4 font-medium w-12"></th>
                </tr>
              </thead>
              <tbody>
                {datos.productos.map((producto) => (
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
                        className={`px-2.5 py-1 rounded-md text-xs font-medium ${
                          ESTILO_ESTADO[producto.estado] ??
                          "bg-[#1C2029] text-[#7C8699] border border-[#242938]"
                        }`}
                      >
                        {producto.estado}
                      </span>
                    </td>
                    <td className="p-4 text-[#F5F7FA]">
                      {producto.nivel_demanda_estimado}
                    </td>
                    <td className="p-4 text-[#7C8699]">
                      {producto.nivel_competencia_estimado}
                    </td>
                    <td className="p-4">
                      <BotonEliminar
                        productoId={producto.id}
                        nombreProducto={producto.nombre_producto}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-[#5B6272] text-xs mt-3 font-mono">
            {datos.total} producto{datos.total !== 1 ? "s" : ""} · filtros por
            categoría y estado
          </p>
        </>
      )}
    </div>
  );
}