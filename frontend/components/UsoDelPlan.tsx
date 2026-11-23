import { Gauge } from "lucide-react";
import type { UsoPlan } from "@/lib/api/organizacion";

const NOMBRE: Record<string, string> = { investigador: "Búsquedas de productos", marketing: "Campañas de marketing" };
const PLAN: Record<string, string> = { beta: "Beta gratuita", emprendedor: "Emprendedor", negocio: "Negocio" };

function minutos(segundos: number): string {
  const m = Math.max(1, Math.ceil(segundos / 60));
  return m === 1 ? "1 minuto" : `${m} minutos`;
}

/** Cuánto le queda al negocio de cada cuota (docs/004-Backend/03, sección 6). */
export default function UsoDelPlan({ uso }: { uso: UsoPlan }) {
  return (
    <div className="rounded-2xl border border-borde bg-superficie p-5">
      <p className="flex items-center gap-2 font-semibold text-texto">
        <Gauge className="h-4 w-4 text-acento-claro" aria-hidden="true" />
        Uso de tu plan · {PLAN[uso.plan] ?? uso.plan}
      </p>
      {!uso.disponible ? (
        <p className="mt-3 text-sm text-texto-2">No pudimos medir el uso en este momento.</p>
      ) : (
        <ul className="mt-4 space-y-4">
          {uso.cuotas.map((c) => {
            const pct = c.limite_por_hora ? Math.round((c.usadas / c.limite_por_hora) * 100) : 0;
            const color = pct >= 90 ? "bg-rojo" : pct >= 70 ? "bg-ambar" : "bg-acento";
            return (
              <li key={c.agente}>
                <div className="flex items-baseline justify-between gap-2 text-sm">
                  <span className="text-texto">{NOMBRE[c.agente] ?? c.agente}</span>
                  <span className="tabular-nums text-texto-2">
                    te quedan <span className="font-semibold text-texto">{c.restantes}</span> de {c.limite_por_hora} esta hora
                  </span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-fondo" role="progressbar" aria-valuenow={c.usadas} aria-valuemin={0} aria-valuemax={c.limite_por_hora} aria-label={NOMBRE[c.agente]}>
                  <div className={`h-2 rounded-full ${color}`} style={{ width: `${Math.min(100, pct)}%` }} />
                </div>
                {c.usadas > 0 && <p className="mt-1 text-xs text-texto-3">Se renueva en {minutos(c.se_renueva_en_segundos)}.</p>}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
