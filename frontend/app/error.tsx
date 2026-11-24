"use client"; // Los límites de error tienen que ser componentes cliente

/**
 * Error inesperado en una pantalla. Nunca muestra el detalle técnico (podría
 * filtrar información interna): solo un código de referencia para soporte.
 */
import Link from "next/link";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO } from "@/components/ui/estilos";

export default function ErrorDePagina({ error, retry }: { error: unknown; retry: () => void }) {
  const referencia = typeof error === "object" && error !== null && "digest" in error ? String((error as { digest?: string }).digest ?? "") : "";
  return (
    <div className="mx-auto max-w-lg py-16 text-center">
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-ambar-borde bg-ambar-fondo">
        <AlertTriangle className="h-5 w-5 text-ambar" aria-hidden="true" />
      </div>
      <h1 className="text-lg font-semibold text-texto">Algo falló al cargar esta pantalla</h1>
      <p className="mt-2 text-sm text-texto-2">Probá de nuevo en unos segundos. Si sigue pasando, escribinos por la ayuda.</p>
      {referencia && <p className="mt-2 text-xs text-texto-3">Referencia: {referencia}</p>}
      <div className="mt-6 flex justify-center gap-2">
        <button type="button" onClick={() => retry()} className={BOTON_PRIMARIO}>
          <RotateCcw className="h-4 w-4" aria-hidden="true" /> Reintentar
        </button>
        <Link href="/" className={BOTON_SECUNDARIO}>Ir al inicio</Link>
      </div>
    </div>
  );
}
