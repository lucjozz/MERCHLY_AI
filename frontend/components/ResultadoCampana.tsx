import { Lightbulb, Users, AlertTriangle, Mail, Share2, Search } from "lucide-react";
import type { CampanaMarketing } from "@/lib/api/marketing";
import TextoAnimado from "@/components/TextoAnimado";
import { BadgeSimulado } from "@/components/ui/Badge";
import { esCampanaSimulada, etiquetaCanal } from "@/lib/etiquetas";

const ICONO_CANAL = {
  email: Mail,
  redes_sociales: Share2,
  busqueda_paga: Search,
} as const;

/** Muestra una campaña generada por la IA. Todo el texto se renderiza como texto plano. */
export default function ResultadoCampana({ campana }: { campana: CampanaMarketing }) {
  const simulada = esCampanaSimulada(campana);

  return (
    <div className="space-y-6 animate-aparecer">
      {simulada && (
        <div className="flex flex-wrap items-center gap-2 rounded-xl border border-dashed border-acento-borde bg-acento-hondo/20 px-4 py-3 text-sm text-texto-2">
          <BadgeSimulado />
          Contenido de prueba: el agente de Marketing todavía usa un proveedor simulado.
        </div>
      )}

      <div>
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold text-texto">
          <Lightbulb className="h-4 w-4 text-ambar" aria-hidden="true" />
          Ideas para la campaña
        </p>
        <ol className="space-y-2">
          {campana.angulos_de_campana.map((angulo, i) => (
            <li key={i} className="flex gap-3 rounded-xl bg-fondo/60 px-4 py-3 text-sm text-texto">
              <span className="font-mono text-acento-claro">{String(i + 1).padStart(2, "0")}</span>
              <span className="min-w-0 break-words">
                <TextoAnimado texto={angulo} />
              </span>
            </li>
          ))}
        </ol>
      </div>

      <div>
        <p className="mb-2 flex items-center gap-2 text-sm font-semibold text-texto">
          <Users className="h-4 w-4 text-acento-claro" aria-hidden="true" />
          A quién le hablás
        </p>
        <p className="break-words rounded-xl bg-fondo/60 px-4 py-3 text-sm leading-relaxed text-texto">
          <TextoAnimado texto={campana.publico_objetivo_sugerido} />
        </p>
      </div>

      {Object.entries(campana.copy_por_canal).map(([canal, copies]) => {
        const Icono = ICONO_CANAL[canal as keyof typeof ICONO_CANAL] ?? Share2;
        return (
          <div key={canal}>
            <p className="mb-2 flex items-center gap-2 text-sm font-semibold text-texto">
              <Icono className="h-4 w-4 text-acento-claro" aria-hidden="true" />
              Textos para {etiquetaCanal(canal)}
            </p>
            <div className="space-y-2">
              {copies.map((copy, i) => (
                <div key={i} className="rounded-xl border border-borde bg-fondo p-4">
                  <p className="break-words text-sm font-semibold text-texto">
                    <TextoAnimado texto={copy.titulo} />
                  </p>
                  <p className="mt-1 break-words text-sm leading-relaxed text-texto-2">
                    <TextoAnimado texto={copy.cuerpo} velocidad={8} />
                  </p>
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {campana.advertencias.length > 0 && (
        <div className="space-y-1.5 rounded-xl border border-ambar-borde bg-ambar-fondo/60 p-4">
          <p className="flex items-center gap-2 text-sm font-semibold text-ambar">
            <AlertTriangle className="h-4 w-4" aria-hidden="true" />
            Antes de publicar
          </p>
          {campana.advertencias.map((advertencia, i) => (
            <p key={i} className="break-words text-sm text-texto">
              {advertencia}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
