"use client";

import { useState } from "react";
import { Loader2, Megaphone, Sparkles } from "lucide-react";
import { generarCampanaMarketing, type CampanaMarketing } from "@/lib/api/marketing";
import ResultadoCampana from "@/components/ResultadoCampana";
import Skeleton from "@/components/ui/Skeleton";
import { BOTON_PRIMARIO } from "@/components/ui/estilos";

interface CampanaMarketingProps {
  productoId: string;
  estado: string;
}

export default function CampanaMarketingPanel({
  productoId,
  estado,
}: CampanaMarketingProps) {
  const [campana, setCampana] = useState<CampanaMarketing | null>(null);
  const [generando, setGenerando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generar() {
    setGenerando(true);
    setError(null);

    try {
      const resultado = await generarCampanaMarketing(productoId);
      setCampana(resultado);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo generar la campaña. Probá de nuevo en unos segundos.");
    } finally {
      setGenerando(false);
    }
  }

  if (estado !== "en_catalogo") {
    return null;
  }

  return (
    <section
      aria-labelledby="titulo-campana"
      className="relative mt-8 overflow-hidden rounded-3xl border border-acento-borde/70 bg-gradient-to-br from-acento-hondo/40 via-superficie to-superficie p-5 sm:p-7 animate-aparecer"
    >
      <p className="text-xs font-semibold uppercase tracking-wider text-acento-claro">
        Paso 4 · Generá la campaña
      </p>
      <h2
        id="titulo-campana"
        className="mt-1 flex items-center gap-2 text-lg font-bold text-texto sm:text-xl"
      >
        <Megaphone className="h-5 w-5 text-acento-claro" aria-hidden="true" />
        Campaña de marketing con IA
      </h2>
      <p className="mt-2 text-sm leading-relaxed text-texto-2">
        La IA propone ideas y textos para email. No publica ni gasta nada: vos
        elegís qué usar. Para más canales y tonos, usá la sección Marketing.
      </p>

      {!campana && (
        <button onClick={generar} disabled={generando} className={`mt-5 ${BOTON_PRIMARIO}`}>
          {generando ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Sparkles className="h-4 w-4" aria-hidden="true" />
          )}
          {generando ? "Generando campaña..." : "Generar campaña"}
        </button>
      )}

      {generando && (
        <div className="mt-6 space-y-3" role="status">
          <span className="sr-only">Generando campaña...</span>
          <Skeleton className="h-10 w-full" />
          <Skeleton className="h-10 w-5/6" />
          <Skeleton className="h-24 w-full" />
        </div>
      )}

      {error && (
        <p role="alert" className="mt-4 text-sm text-rojo">
          {error}
        </p>
      )}

      {campana && (
        <div className="mt-6">
          <ResultadoCampana campana={campana} />
        </div>
      )}
    </section>
  );
}
