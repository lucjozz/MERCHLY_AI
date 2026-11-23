"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Check, CircleCheck, X, ShieldCheck } from "lucide-react";
import { registrarDecision } from "@/lib/api/decisiones";
import { CAMPO } from "@/components/ui/estilos";

interface AccionesDecisionProps {
  productoId: string;
  /** Estado actual: si es final (en catálogo / descartado) ya no se decide. */
  estado?: string;
}

const ESTADOS_FINALES = ["en_catalogo", "descartado"];

const MINIMO_MOTIVO = 8;

export default function AccionesDecision({ productoId, estado }: AccionesDecisionProps) {
  const router = useRouter();
  const [motivo, setMotivo] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState<"aprobado" | "descartado" | null>(
    null
  );

  async function decidir(decision: "aprobado" | "descartado") {
    if (motivo.trim().length < MINIMO_MOTIVO) {
      setError(
        "Escribí el motivo de la decisión (mínimo 8 caracteres) antes de confirmar."
      );
      return;
    }

    setError(null);
    setEnviando(true);

    try {
      await registrarDecision({
        decision_type: "product_selection",
        entity_type: "product_candidate",
        entity_id: productoId,
        action: decision === "aprobado" ? "approve" : "discard",
        reason: motivo,
      });
      setResultado(decision);
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo registrar la decisión. Probá de nuevo en unos segundos.");
    } finally {
      setEnviando(false);
    }
  }

  const largo = motivo.trim().length;
  const decisionFinal = resultado ?? (estado && ESTADOS_FINALES.includes(estado)
    ? (estado === "en_catalogo" ? "aprobado" : "descartado")
    : null);

  if (decisionFinal && !resultado) {
    return (
      <section
        className="mt-8 rounded-3xl border border-borde bg-superficie p-5 sm:p-7 animate-aparecer"
        aria-labelledby="titulo-decision"
      >
        <p className="text-xs font-semibold uppercase tracking-wider text-acento-claro">Paso 3 · Decidí</p>
        <h2 id="titulo-decision" className="mt-1 flex items-center gap-2 text-lg font-bold text-texto sm:text-xl">
          <CircleCheck className={`h-5 w-5 ${decisionFinal === "aprobado" ? "text-verde" : "text-texto-2"}`} aria-hidden="true" />
          {decisionFinal === "aprobado" ? "Ya lo aprobaste" : "Ya lo descartaste"}
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-texto-2">
          Las decisiones finales no se cambian: quedan en el historial para que
          el equipo sepa qué se decidió y por qué. Si cambiaron las condiciones,
          investigá la categoría de nuevo y decidí sobre el resultado nuevo.
        </p>
      </section>
    );
  }

  return (
    <section
      className="mt-8 rounded-3xl border border-borde bg-superficie p-5 sm:p-7 animate-aparecer"
      aria-labelledby="titulo-decision"
    >
      <p className="text-xs font-semibold uppercase tracking-wider text-acento-claro">
        Paso 3 · Decidí
      </p>
      <h2 id="titulo-decision" className="mt-1 text-lg font-bold text-texto sm:text-xl">
        ¿Lo sumás a tu catálogo?
      </h2>
      <p className="mt-2 flex items-start gap-2 text-sm leading-relaxed text-texto-2">
        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-verde" aria-hidden="true" />
        La IA solo recomienda: la decisión es tuya. Queda registrada con tu
        motivo en el historial, para que el equipo sepa por qué se eligió.
      </p>

      <div className="mt-5 flex flex-col gap-2">
        <div className="flex items-baseline justify-between gap-2">
          <label htmlFor="motivo" className="text-sm font-medium text-texto">
            ¿Por qué decidís esto?
          </label>
          <span
            className={`text-xs tabular-nums ${
              largo >= MINIMO_MOTIVO ? "text-verde" : "text-texto-2"
            }`}
            aria-hidden="true"
          >
            {largo >= MINIMO_MOTIVO ? "✓ Listo" : `${largo}/${MINIMO_MOTIVO} mínimo`}
          </span>
        </div>
        <textarea
          id="motivo"
          rows={3}
          value={motivo}
          onChange={(e) => {
            setMotivo(e.target.value);
            if (error) setError(null);
          }}
          placeholder="Ej.: margen suficiente y competencia moderada, avanzamos con lote de prueba de 200 unidades."
          aria-invalid={Boolean(error)}
          aria-describedby={error ? "motivo-error" : undefined}
          className={`${CAMPO} resize-y leading-relaxed`}
        />
      </div>

      {error && (
        <p
          id="motivo-error"
          role="alert"
          className="mt-4 flex items-start gap-2 rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2.5 text-sm text-rojo animate-aparecer"
        >
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          {error}
        </p>
      )}

      {resultado && (
        <p
          role="status"
          className={`mt-4 flex items-start gap-2 rounded-lg border px-3 py-2.5 text-sm animate-aparecer ${
            resultado === "aprobado"
              ? "border-verde-borde bg-verde-fondo text-verde"
              : "border-borde-fuerte bg-gris-fondo text-texto-2"
          }`}
        >
          <CircleCheck className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          {resultado === "aprobado"
            ? "Producto aprobado y enviado al catálogo."
            : "Producto descartado. La decisión queda guardada en tu historial."}
        </p>
      )}

      {!resultado && (
      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => decidir("aprobado")}
          disabled={enviando}
          className="inline-flex h-14 items-center justify-center gap-2.5 rounded-xl border border-verde-borde bg-verde-fondo text-base font-semibold text-verde transition-all hover:bg-verde hover:text-fondo active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100"
        >
          <Check className="h-5 w-5" aria-hidden="true" />
          {enviando ? "Enviando..." : "Aprobar"}
        </button>
        <button
          type="button"
          onClick={() => decidir("descartado")}
          disabled={enviando}
          className="inline-flex h-14 items-center justify-center gap-2.5 rounded-xl border border-rojo-borde bg-rojo-fondo text-base font-semibold text-rojo transition-all hover:bg-rojo-borde hover:text-texto active:scale-[0.98] disabled:opacity-50 disabled:active:scale-100"
        >
          <X className="h-5 w-5" aria-hidden="true" />
          {enviando ? "Enviando..." : "Descartar"}
        </button>
      </div>
      )}
    </section>
  );
}
