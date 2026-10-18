import { CircleCheck, Clock, ShieldCheck } from "lucide-react";
import {
  listarProductosCandidatos,
  type ProductoCandidato,
} from "@/lib/api/productos-candidatos";

export const dynamic = "force-dynamic";

const MUESTRA_MINIMA = 3;
const DECISIONES_MINIMAS = 5;

type Atributo = "nivel_demanda_estimado" | "nivel_competencia_estimado";

const ATRIBUTOS: { clave: Atributo; etiqueta: string }[] = [
  { clave: "nivel_demanda_estimado", etiqueta: "demanda" },
  { clave: "nivel_competencia_estimado", etiqueta: "competencia" },
];

const PASOS = [
  { titulo: "Decisión humana", activo: true },
  { titulo: "Registro con motivo y evidencia", activo: true },
  { titulo: "Detección de patrones", activo: true },
  { titulo: "Medición de resultados reales", activo: false },
  { titulo: "Regla aprobada por una persona", activo: false },
];

interface Patron {
  etiqueta: string;
  nivel: string;
  muestra: number;
  aprobados: number;
  tasa: number;
}

function detectarPatrones(decididos: ProductoCandidato[]): Patron[] {
  const patrones: Patron[] = [];
  for (const { clave, etiqueta } of ATRIBUTOS) {
    for (const nivel of ["alto", "medio", "bajo"]) {
      const grupo = decididos.filter((p) => p[clave] === nivel);
      if (grupo.length < MUESTRA_MINIMA) continue;
      const aprobados = grupo.filter((p) => p.estado === "en_catalogo").length;
      patrones.push({
        etiqueta,
        nivel,
        muestra: grupo.length,
        aprobados,
        tasa: Math.round((aprobados / grupo.length) * 100),
      });
    }
  }
  return patrones.sort((a, b) => b.tasa - a.tasa);
}

export default async function Automatizacion() {
  let decididos: ProductoCandidato[] = [];
  let error: string | null = null;

  try {
    const [aprobados, descartados] = await Promise.all([
      listarProductosCandidatos(1, 100, undefined, "en_catalogo"),
      listarProductosCandidatos(1, 100, undefined, "descartado"),
    ]);
    decididos = [...aprobados.productos, ...descartados.productos];
  } catch {
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  const patrones = detectarPatrones(decididos);

  return (
    <div className="px-10 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#F5F7FA]">Automatización</h1>
        <p className="text-[#7C8699] mt-1">
          Qué está aprendiendo el sistema de las decisiones humanas.
        </p>
      </header>

      {error && (
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-[320px_1fr] gap-6 max-w-5xl mb-6">
        <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6 h-fit">
          <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-5">
            Flujo
          </p>
          <ol className="space-y-4">
            {PASOS.map((paso, i) => (
              <li key={paso.titulo} className="flex items-center gap-3 text-sm">
                {paso.activo ? (
                  <CircleCheck className="h-4 w-4 text-[#4ADE80]" aria-hidden="true" />
                ) : (
                  <Clock className="h-4 w-4 text-[#5B6272]" aria-hidden="true" />
                )}
                <span className={paso.activo ? "text-[#F5F7FA]" : "text-[#5B6272]"}>
                  {i + 1}. {paso.titulo}
                </span>
              </li>
            ))}
          </ol>
        </div>

        <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold text-[#F5F7FA]">
              Patrones detectados
            </h2>
            <span className="text-xs text-[#A78BFA] font-medium">
              PROPUESTAS · REQUIEREN REVISIÓN HUMANA
            </span>
          </div>

          {!error && decididos.length < DECISIONES_MINIMAS && (
            <p className="text-[#7C8699] text-sm">
              Hay {decididos.length} decisiones. Hacen falta al menos{" "}
              {DECISIONES_MINIMAS} para detectar patrones.
            </p>
          )}

          {decididos.length >= DECISIONES_MINIMAS && patrones.length === 0 && (
            <p className="text-[#7C8699] text-sm">
              Ningún grupo alcanza la muestra mínima de {MUESTRA_MINIMA}.
            </p>
          )}

          <div className="space-y-5">
            {patrones.map((p) => (
              <div key={`${p.etiqueta}-${p.nivel}`}>
                <div className="flex justify-between text-sm mb-1.5">
                  <span className="text-[#F5F7FA]">
                    {p.etiqueta.charAt(0).toUpperCase() + p.etiqueta.slice(1)}{" "}
                    {p.nivel}
                  </span>
                  <span className="text-[#7C8699]">
                    {p.aprobados} de {p.muestra} aprobados · {p.tasa}%
                  </span>
                </div>
                <div className="h-2 rounded-full bg-[#0B0D12]">
                  <div
                    className="h-2 rounded-full bg-[#A78BFA] transition-all duration-700"
                    style={{ width: `${p.tasa}%` }}
                  />
                </div>
                {p.muestra < 10 && (
                  <p className="text-[#5B6272] text-xs mt-1">
                    Muestra chica: tomalo como orientativo.
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-[#1A1229] border border-[#2D1F47] rounded-lg p-5 max-w-5xl flex items-start gap-3">
        <ShieldCheck className="h-5 w-5 mt-0.5 shrink-0 text-[#A78BFA]" aria-hidden="true" />
        <p className="text-sm text-[#F5F7FA]">
          La IA aprende de las decisiones humanas, pero no convierte ese
          aprendizaje en política operativa sin aprobación humana.
        </p>
      </div>
    </div>
  );
}