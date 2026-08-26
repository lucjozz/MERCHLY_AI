import { obtenerProductoCandidato } from "@/lib/api/productos-candidatos";
import AccionesDecision from "@/components/AccionesDecision";
import Link from "next/link";
import { notFound } from "next/navigation";

interface PageProps {
  params: Promise<{ id: string }>;
}

const ESTILO_ESTADO: Record<string, string> = {
  candidato: "bg-[#3A2E12] text-[#E8B84B] border border-[#4A3A17]",
  en_catalogo: "bg-[#123420] text-[#4ADE80] border border-[#1B4A2C]",
  descartado: "bg-[#1C2029] text-[#7C8699] border border-[#242938]",
};

export default async function DetalleProducto({ params }: PageProps) {
  const { id } = await params;
  let producto;

  try {
    producto = await obtenerProductoCandidato(id);
  } catch {
    return (
      <div className="min-h-screen bg-[#0B0D12] flex items-center justify-center px-6">
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-6 max-w-md text-center text-sm">
          No se pudo conectar con el backend. ¿Está corriendo?
        </div>
      </div>
    );
  }

  if (producto === null) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-[#0B0D12]">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <Link
          href="/"
          className="text-[#3D7DD8] text-sm hover:underline mb-6 inline-block"
        >
          ← Volver al panel
        </Link>

        <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-[#F5F7FA]">
                {producto.nombre_producto}
              </h1>
              <p className="text-[#7C8699] text-sm font-mono mt-1">
                {producto.categoria} · {producto.mercado_objetivo}
              </p>
            </div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                ESTILO_ESTADO[producto.estado] ??
                "bg-[#1C2029] text-[#7C8699] border border-[#242938]"
              }`}
            >
              {producto.estado}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-8">
            <div>
              <p className="text-[#7C8699] text-xs mb-1">Precio estimado</p>
              <p className="text-[#F5F7FA] text-lg">
                {producto.precio_estimado_proveedor !== null
                  ? `$${producto.precio_estimado_proveedor}`
                  : "—"}
              </p>
            </div>
            <div>
              <p className="text-[#7C8699] text-xs mb-1">Precio sugerido</p>
              <p className="text-[#F5F7FA] text-lg">
                {producto.precio_sugerido_venta !== null
                  ? `$${producto.precio_sugerido_venta}`
                  : "—"}
              </p>
            </div>
            <div>
              <p className="text-[#7C8699] text-xs mb-1">Demanda estimada</p>
              <p className="text-[#F5F7FA] text-lg">
                {producto.nivel_demanda_estimado}
              </p>
            </div>
            <div>
              <p className="text-[#7C8699] text-xs mb-1">Competencia estimada</p>
              <p className="text-[#F5F7FA] text-lg">
                {producto.nivel_competencia_estimado}
              </p>
            </div>
          </div>

          {producto.fuentes_evidencia.length > 0 && (
            <div className="mb-6">
              <p className="text-[#7C8699] text-xs mb-2">Fuentes de evidencia</p>
              <ul className="space-y-1">
                {producto.fuentes_evidencia.map((fuente, i) => (
                  <li key={i} className="text-[#3D7DD8] text-sm truncate">
                    {fuente}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {producto.riesgos_identificados.length > 0 && (
            <div>
              <p className="text-[#7C8699] text-xs mb-2">Riesgos identificados</p>
              <ul className="space-y-1">
                {producto.riesgos_identificados.map((riesgo, i) => (
                  <li key={i} className="text-[#E8B84B] text-sm">
                    ⚠ {riesgo}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <AccionesDecision productoId={producto.id} />
        </div>
      </div>
    </div>
  );
}