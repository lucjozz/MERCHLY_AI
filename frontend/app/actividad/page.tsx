import Link from "next/link";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";

export const dynamic = "force-dynamic";

const COLOR_PUNTO: Record<string, string> = {
  candidato: "bg-[#E8B84B]",
  en_catalogo: "bg-[#4ADE80]",
  descartado: "bg-[#7C8699]",
};

const TEXTO_ESTADO: Record<string, string> = {
  candidato: "Pendiente de decisión",
  en_catalogo: "Aprobado",
  descartado: "Descartado",
};

function formatearFecha(iso: string): string {
  return new Date(iso).toLocaleString("es-BO", {
    timeZone: "America/La_Paz",
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function haceCuanto(iso: string): string {
  const minutos = Math.max(
    0,
    Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  );
  if (minutos < 1) return "hace un momento";
  if (minutos < 60) return `hace ${minutos} min`;
  const horas = Math.floor(minutos / 60);
  if (horas < 24) return `hace ${horas} h`;
  return `hace ${Math.floor(horas / 24)} d`;
}

export default async function Actividad() {
  let datos;
  let error: string | null = null;

  try {
    datos = await listarProductosCandidatos(1, 20);
  } catch {
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  return (
    <div className="px-10 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#F5F7FA]">Actividad</h1>
        <p className="text-[#7C8699] mt-1">
          Últimos productos descubiertos por el Investigador, del más reciente
          al más antiguo.
        </p>
      </header>

      {error && (
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {datos && datos.productos.length === 0 && (
        <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-12 text-center">
          <p className="text-[#F5F7FA] text-sm mb-1">Todavía no hay actividad.</p>
          <p className="text-[#7C8699] text-xs mb-4">
            Cuando el Investigador descubra productos, van a aparecer acá.
          </p>
          <Link
            href="/productos"
            className="text-[#3D7DD8] text-sm font-medium hover:underline"
          >
            Ir a Productos →
          </Link>
        </div>
      )}

      {datos && datos.productos.length > 0 && (
        <div className="bg-[#12151C] border border-[#1F2430] rounded-lg divide-y divide-[#1F2430] max-w-4xl">
          {datos.productos.map((producto) => (
            <div key={producto.id} className="flex items-start gap-4 p-5">
              <span
                className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${
                  COLOR_PUNTO[producto.estado] ?? "bg-[#7C8699]"
                }`}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm">
                  <span className="text-[#7C8699]">El Investigador descubrió </span>
                  <Link
                    href={`/productos/${producto.id}`}
                    className="text-[#F5F7FA] font-medium hover:text-[#3D7DD8] transition-colors"
                  >
                    {producto.nombre_producto}
                  </Link>
                </p>
                <p className="text-xs text-[#5B6272] mt-1 font-mono">
                  {producto.categoria} · {producto.mercado_objetivo} ·{" "}
                  {TEXTO_ESTADO[producto.estado] ?? producto.estado}
                </p>
              </div>
              <time
                className="text-xs text-[#7C8699] whitespace-nowrap"
                title={formatearFecha(producto.creado_en)}
              >
                {haceCuanto(producto.creado_en)}
              </time>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}