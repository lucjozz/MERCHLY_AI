import { redirect } from "next/navigation";
import { Search, Sparkles, BarChart3, type LucideIcon } from "lucide-react";
import { obtenerReporteAnalitica } from "@/lib/api/analitica";
import { SesionInvalidaError } from "@/lib/api/errores";

export const dynamic = "force-dynamic";

const ROLES_NEGOCIO = [
  "Administrador principal",
  "Responsable técnico",
  "Responsable de negocio",
];

interface AgenteInfo {
  nombre: string;
  descripcion: string;
  icono: LucideIcon;
  color: string;
  nivel: string;
  proveedor: string;
  roles: string[];
  metricas: { valor: string; etiqueta: string }[];
  nota?: string;
}

export default async function Agentes() {
  let reporte;
  let error: string | null = null;

  try {
    reporte = await obtenerReporteAnalitica();
  } catch (e) {
    if (e instanceof SesionInvalidaError) redirect("/login");
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  const investigaciones = reporte
    ? String(reporte.actividad_agente_investigador.total_investigaciones)
    : "—";
  const productos = reporte
    ? String(reporte.resumen_catalogo.total_productos_candidatos)
    : "—";

  const agentes: AgenteInfo[] = [
    {
      nombre: "Investigador de Producto",
      descripcion:
        "Dado un nicho, identifica productos con potencial de venta y devuelve evidencia de demanda y competencia.",
      icono: Search,
      color: "#3D7DD8",
      nivel: "1 · Análisis y recomendación",
      proveedor: "Gemini si hay clave configurada; si no, simulado",
      roles: ROLES_NEGOCIO,
      metricas: [
        { valor: investigaciones, etiqueta: "investigaciones · últimos 30 días" },
        { valor: productos, etiqueta: "productos descubiertos · últimos 30 días" },
      ],
    },
    {
      nombre: "Marketing IA",
      descripcion:
        "Propone ángulos, copys y público objetivo para productos ya aprobados. Nunca publica ni gasta.",
      icono: Sparkles,
      color: "#A78BFA",
      nivel: "1 · Análisis y recomendación",
      proveedor: "Simulado (integración con ChatGPT pendiente)",
      roles: ROLES_NEGOCIO,
      metricas: [],
      nota: "Las campañas generadas no se guardan: el contrato no persiste nada.",
    },
    {
      nombre: "Analítica Básica",
      descripcion:
        "Resume el catálogo: distribución por categoría, estado y conversión a catálogo.",
      icono: BarChart3,
      color: "#4ADE80",
      nivel: "0 · Solo lectura",
      proveedor: "Sin IA: agregación de datos",
      roles: [...ROLES_NEGOCIO, "Usuario operativo"],
      metricas: [
        { valor: productos, etiqueta: "productos analizados · últimos 30 días" },
      ],
    },
  ];

  return (
    <div className="px-10 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#F5F7FA]">Agentes</h1>
        <p className="text-[#7C8699] mt-1">
          Tu organización digital. La IA recomienda; las personas deciden.
        </p>
      </header>

      {error && (
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm mb-6">
          {error}
        </div>
      )}

      <div className="space-y-4 max-w-4xl">
        {agentes.map((agente) => {
          const Icono = agente.icono;
          return (
            <div
              key={agente.nombre}
              className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6 flex items-start gap-5"
            >
              <div className="h-11 w-11 rounded-lg bg-[#0B0D12] border border-[#1F2430] flex items-center justify-center shrink-0">
                <Icono
                  className="h-5 w-5"
                  style={{ color: agente.color }}
                  aria-hidden="true"
                />
              </div>

              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-semibold text-[#F5F7FA]">
                    {agente.nombre}
                  </h2>
                  <span
                    className="flex items-center gap-2 text-xs font-medium"
                    style={{ color: agente.color }}
                  >
                    <span
                      className="h-2 w-2 rounded-full"
                      style={{ backgroundColor: agente.color }}
                    />
                    DISPONIBLE
                  </span>
                </div>
                <p className="text-[#7C8699] text-sm mt-1">{agente.descripcion}</p>

                <div className="grid grid-cols-3 gap-4 mt-5 text-xs">
                  <div>
                    <p className="text-[#5B6272] uppercase tracking-wide mb-1">
                      Nivel de permiso
                    </p>
                    <p className="text-[#F5F7FA]">{agente.nivel}</p>
                  </div>
                  <div>
                    <p className="text-[#5B6272] uppercase tracking-wide mb-1">
                      Proveedor
                    </p>
                    <p className="text-[#F5F7FA]">{agente.proveedor}</p>
                  </div>
                  <div>
                    <p className="text-[#5B6272] uppercase tracking-wide mb-1">
                      Pueden usarlo
                    </p>
                    <p className="text-[#F5F7FA]">{agente.roles.join(", ")}</p>
                  </div>
                </div>

                {agente.metricas.length > 0 && (
                  <div className="flex gap-10 mt-5 pt-5 border-t border-[#1F2430]">
                    {agente.metricas.map((metrica) => (
                      <div key={metrica.etiqueta}>
                        <p className="text-2xl font-bold text-[#F5F7FA]">
                          {metrica.valor}
                        </p>
                        <p className="text-[#7C8699] text-xs">{metrica.etiqueta}</p>
                      </div>
                    ))}
                  </div>
                )}

                {agente.nota && (
                  <p className="text-[#5B6272] text-xs mt-5 pt-5 border-t border-[#1F2430]">
                    {agente.nota}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}