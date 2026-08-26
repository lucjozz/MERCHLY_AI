"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, Check, X } from "lucide-react";
import { registrarDecision } from "@/lib/api/decisiones";

interface AccionesDecisionProps {
  productoId: string;
}

export default function AccionesDecision({ productoId }: AccionesDecisionProps) {
  const router = useRouter();
  const [motivo, setMotivo] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState<"aprobado" | "descartado" | null>(
    null
  );

  async function decidir(decision: "aprobado" | "descartado") {
    if (motivo.trim().length < 8) {
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
        user_id: "daniel",
        reason: motivo,
      });
      setResultado(decision);
      router.refresh();
    } catch {
      setError("No se pudo registrar la decisión. ¿Está corriendo el backend?");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section
      className="rounded-lg border border-[#1F2430] bg-[#12151C] p-6 mt-8"
      aria-label="Decisión sobre el producto"
    >
      <h2 className="text-sm font-medium uppercase tracking-widest text-[#7C8699]">
        Decisión
      </h2>
      <p className="mt-2 text-sm leading-relaxed text-[#7C8699]">
        Esta acción cambia el estado del producto{" "}
        <span className="font-mono text-[#F5F7FA]">{productoId}</span> y
        queda registrada en la bitácora de auditoría.
      </p>

      <div className="mt-5 flex flex-col gap-2">
        <label
          htmlFor="motivo"
          className="text-xs font-medium uppercase tracking-widest text-[#7C8699]"
        >
          Motivo de la decisión
        </label>
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
          className="resize-y rounded-md border border-[#1F2430] bg-[#0B0D12] p-3 text-sm leading-relaxed text-[#F5F7FA] placeholder:text-[#7C8699] outline-none focus:border-[#3D7DD8] focus:ring-2 focus:ring-[#1E3A5F]"
        />
      </div>

      {error && (
        <p
          id="motivo-error"
          role="alert"
          className="mt-4 flex items-start gap-2 rounded-md border border-[#4A2020] bg-[#2A1414] px-3 py-2.5 text-sm text-[#E88B8B]"
        >
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          {error}
        </p>
      )}

      {resultado && (
        <p
          role="status"
          className={`mt-4 rounded-md px-3 py-2.5 text-sm ${
            resultado === "aprobado"
              ? "bg-[#123420] text-[#4ADE80]"
              : "bg-[#1C2029] text-[#7C8699]"
          }`}
        >
          {resultado === "aprobado"
            ? "Producto aprobado y enviado al catálogo."
            : "Producto descartado. El agente no volverá a proponerlo."}
        </p>
      )}

      <div className="mt-6 grid gap-3 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => decidir("aprobado")}
          disabled={enviando}
          className="inline-flex h-14 items-center justify-center gap-2.5 rounded-md bg-[#123420] text-base font-semibold text-[#4ADE80] ring-1 ring-inset ring-[#4ADE80]/25 transition-colors hover:bg-[#4ADE80] hover:text-[#0B0D12] focus:outline-none focus:ring-2 focus:ring-[#4ADE80] focus:ring-offset-2 focus:ring-offset-[#12151C] disabled:opacity-50"
        >
          <Check className="h-5 w-5" aria-hidden="true" />
          {enviando ? "Enviando..." : "Aprobar"}
        </button>
        <button
          type="button"
          onClick={() => decidir("descartado")}
          disabled={enviando}
          className="inline-flex h-14 items-center justify-center gap-2.5 rounded-md bg-[#2A1414] text-base font-semibold text-[#E88B8B] ring-1 ring-inset ring-[#4A2020] transition-colors hover:bg-[#4A2020] hover:text-[#F5F7FA] focus:outline-none focus:ring-2 focus:ring-[#E88B8B] focus:ring-offset-2 focus:ring-offset-[#12151C] disabled:opacity-50"
        >
          <X className="h-5 w-5" aria-hidden="true" />
          {enviando ? "Enviando..." : "Descartar"}
        </button>
      </div>
    </section>
  );
}