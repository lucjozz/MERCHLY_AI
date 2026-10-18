import Link from "next/link";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import PanelMarketing from "@/components/PanelMarketing";

export const dynamic = "force-dynamic";

export default async function Marketing() {
  let productos: { id: string; nombre_producto: string }[] = [];
  let error: string | null = null;

  try {
    const datos = await listarProductosCandidatos(1, 100, undefined, "en_catalogo");
    productos = datos.productos.map((p) => ({
      id: p.id,
      nombre_producto: p.nombre_producto,
    }));
  } catch {
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  return (
    <div className="px-10 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#F5F7FA]">Marketing IA</h1>
        <p className="text-[#7C8699] mt-1">
          Campañas generadas a partir de productos aprobados.
        </p>
      </header>

      {error && (
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {!error && productos.length === 0 && (
        <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-12 text-center">
          <p className="text-[#F5F7FA] text-sm mb-1">
            Todavía no hay productos aprobados.
          </p>
          <p className="text-[#7C8699] text-xs mb-4">
            Marketing solo trabaja sobre productos que un humano ya aprobó.
          </p>
          <Link
            href="/productos"
            className="text-[#3D7DD8] text-sm font-medium hover:underline"
          >
            Ir a Productos →
          </Link>
        </div>
      )}

      {productos.length > 0 && <PanelMarketing productos={productos} />}
    </div>
  );
}