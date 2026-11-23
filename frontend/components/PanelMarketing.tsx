"use client";

import { useState } from "react";
import { Sparkles, Loader2, Check, Wand2 } from "lucide-react";
import {
  generarCampanaMarketing,
  type CampanaMarketing,
  type CanalMarketing,
  type TonoMarketing,
} from "@/lib/api/marketing";
import ResultadoCampana from "@/components/ResultadoCampana";
import Skeleton from "@/components/ui/Skeleton";
import { BOTON_PRIMARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";
import { nombreLimpio } from "@/lib/etiquetas";

interface ProductoAprobado {
  id: string;
  nombre_producto: string;
}

const CANALES: { valor: CanalMarketing; etiqueta: string; ayuda: string }[] = [
  { valor: "redes_sociales", etiqueta: "Redes sociales", ayuda: "Instagram, Facebook, TikTok" },
  { valor: "busqueda_paga", etiqueta: "Búsqueda paga", ayuda: "Anuncios en Google" },
  { valor: "email", etiqueta: "Email", ayuda: "Correos a tus clientes" },
];

const TONOS: { valor: TonoMarketing; etiqueta: string }[] = [
  { valor: "neutral", etiqueta: "Neutral" },
  { valor: "entusiasta", etiqueta: "Entusiasta" },
  { valor: "tecnico", etiqueta: "Técnico" },
  { valor: "premium", etiqueta: "Premium" },
];

export default function PanelMarketing({
  productos,
}: {
  productos: ProductoAprobado[];
}) {
  const [productoId, setProductoId] = useState(productos[0]?.id ?? "");
  const [canales, setCanales] = useState<CanalMarketing[]>(["redes_sociales"]);
  const [tono, setTono] = useState<TonoMarketing>("neutral");
  const [generando, setGenerando] = useState(false);
  const [campana, setCampana] = useState<CampanaMarketing | null>(null);
  const [error, setError] = useState<string | null>(null);

  function alternarCanal(canal: CanalMarketing) {
    setCanales((actuales) =>
      actuales.includes(canal)
        ? actuales.filter((c) => c !== canal)
        : [...actuales, canal]
    );
  }

  async function generar() {
    if (canales.length === 0) {
      setError("Elegí al menos un canal.");
      return;
    }
    setError(null);
    setGenerando(true);
    setCampana(null);

    try {
      setCampana(await generarCampanaMarketing(productoId, canales, tono));
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo generar la campaña. Probá de nuevo en unos segundos.");
    } finally {
      setGenerando(false);
    }
  }

  const totalCopys = campana
    ? Object.values(campana.copy_por_canal).reduce((n, v) => n + v.length, 0)
    : 0;
  const nombreProducto = productos.find((p) => p.id === productoId)?.nombre_producto;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
      <div className="min-w-0 rounded-3xl border border-borde bg-superficie p-5 sm:p-7">
        <div>
          <label htmlFor="producto-campana" className={ETIQUETA_CAMPO}>
            1. Elegí un producto aprobado
          </label>
          <select
            id="producto-campana"
            value={productoId}
            onChange={(e) => setProductoId(e.target.value)}
            className={CAMPO}
          >
            {productos.map((p) => (
              <option key={p.id} value={p.id}>
                {nombreLimpio(p.nombre_producto)}
              </option>
            ))}
          </select>
        </div>

        <fieldset className="mt-6">
          <legend className={ETIQUETA_CAMPO}>2. ¿Dónde lo vas a promocionar?</legend>
          <div className="grid gap-2 sm:grid-cols-3">
            {CANALES.map((c) => {
              const activo = canales.includes(c.valor);
              return (
                <button
                  key={c.valor}
                  type="button"
                  onClick={() => alternarCanal(c.valor)}
                  aria-pressed={activo}
                  className={`flex items-start gap-3 rounded-xl border p-3 text-left transition-all ${
                    activo
                      ? "border-acento bg-acento-hondo/50"
                      : "border-borde-fuerte bg-fondo hover:border-acento-borde"
                  }`}
                >
                  <span
                    className={`mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border ${
                      activo ? "border-acento bg-acento text-white" : "border-borde-fuerte"
                    }`}
                    aria-hidden="true"
                  >
                    {activo && <Check className="h-3 w-3" />}
                  </span>
                  <span>
                    <span className="block text-sm font-medium text-texto">{c.etiqueta}</span>
                    <span className="block text-xs text-texto-2">{c.ayuda}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </fieldset>

        <fieldset className="mt-6">
          <legend className={ETIQUETA_CAMPO}>3. ¿Con qué tono?</legend>
          <div className="flex flex-wrap gap-2">
            {TONOS.map((t) => (
              <button
                key={t.valor}
                type="button"
                onClick={() => setTono(t.valor)}
                aria-pressed={tono === t.valor}
                className={`rounded-full border px-4 py-2 text-sm transition-colors ${
                  tono === t.valor
                    ? "border-acento bg-acento-hondo text-texto"
                    : "border-borde-fuerte bg-fondo text-texto-2 hover:text-texto"
                }`}
              >
                {t.etiqueta}
              </button>
            ))}
          </div>
        </fieldset>

        <button onClick={generar} disabled={generando} className={`mt-7 w-full py-3 sm:w-auto ${BOTON_PRIMARIO}`}>
          {generando ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Sparkles className="h-4 w-4" aria-hidden="true" />
          )}
          {generando ? "Generando campaña..." : "Generar campaña"}
        </button>

        {error && (
          <p role="alert" className="mt-4 text-sm text-rojo">
            {error}
          </p>
        )}

        {generando && (
          <div className="mt-8 space-y-3 border-t border-borde pt-6" role="status">
            <span className="sr-only">Generando campaña...</span>
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-11/12" />
            <Skeleton className="h-28 w-full" />
          </div>
        )}

        {campana && (
          <div className="mt-8 border-t border-borde pt-6">
            <h2 className="mb-5 text-lg font-semibold text-texto">
              Campaña para {nombreProducto ? nombreLimpio(nombreProducto) : "tu producto"}
            </h2>
            <ResultadoCampana campana={campana} />
          </div>
        )}
      </div>

      <aside className="h-fit rounded-3xl border border-acento-borde/60 bg-gradient-to-b from-acento-hondo/40 to-superficie p-5 sm:p-6">
        <p className="flex items-center gap-2 text-sm font-semibold text-texto">
          <Wand2 className="h-4 w-4 text-acento-claro" aria-hidden="true" />
          Lo que generó la IA
        </p>
        {!campana ? (
          <p className="mt-3 text-sm leading-relaxed text-texto-2">
            Acá vas a ver un resumen cuando generes tu campaña. Las campañas no
            se guardan todavía: copiá lo que te sirva antes de salir.
          </p>
        ) : (
          <dl className="mt-5 grid grid-cols-3 gap-3 lg:grid-cols-1">
            {[
              { valor: campana.angulos_de_campana.length, etiqueta: "ideas" },
              { valor: totalCopys, etiqueta: "textos" },
              { valor: Object.keys(campana.copy_por_canal).length, etiqueta: "canales" },
            ].map((d) => (
              <div key={d.etiqueta} className="flex flex-col-reverse rounded-xl bg-fondo/60 p-3">
                <dt className="text-xs text-texto-2">{d.etiqueta}</dt>
                <dd className="text-2xl font-bold tabular-nums text-texto lg:text-3xl">{d.valor}</dd>
              </div>
            ))}
          </dl>
        )}
      </aside>
    </div>
  );
}
