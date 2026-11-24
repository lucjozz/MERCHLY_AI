"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Loader2, Sparkles } from "lucide-react";
import { investigarProductos } from "@/lib/api/investigador";
import { MERCADOS } from "@/lib/etiquetas";
import { BOTON_PRIMARIO, CAMPO } from "@/components/ui/estilos";

const EJEMPLOS = [
  "mochilas antirrobo",
  "lámparas de escritorio",
  "accesorios para mascotas",
  "botellas térmicas",
];

export default function BuscarProductos({ categoriaInicial = "", mercadoInicial = "MX" }: { categoriaInicial?: string; mercadoInicial?: string }) {
  const router = useRouter();
  const [categoria, setCategoria] = useState(categoriaInicial);
  const [mercado, setMercado] = useState(mercadoInicial);
  const [buscando, setBuscando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState<string | null>(null);

  async function buscar(e: React.FormEvent) {
    e.preventDefault();

    if (categoria.trim().length === 0) {
      setError("Escribí una categoría para buscar.");
      return;
    }

    setError(null);
    setExito(null);
    setBuscando(true);

    try {
      await investigarProductos(categoria, mercado);
      setExito(`Listo: la IA terminó de investigar “${categoria.trim()}”. Revisá los resultados abajo.`);
      setCategoria("");
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo completar la búsqueda. Probá de nuevo en unos segundos.");
    } finally {
      setBuscando(false);
    }
  }

  return (
    <section
      aria-labelledby="titulo-buscador"
      className="relative mb-8 overflow-hidden rounded-3xl border border-acento-borde/70 bg-gradient-to-br from-acento-hondo/50 via-superficie to-superficie p-5 sm:p-7 animate-aparecer"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full bg-acento/10 blur-3xl"
      />
      <div className="relative">
        <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-acento-claro">
          <Sparkles className="h-3.5 w-3.5" aria-hidden="true" />
          Paso 1 · Buscá con IA
        </p>
        <h2 id="titulo-buscador" className="mt-1 text-lg font-bold text-texto sm:text-xl">
          ¿Qué te gustaría vender?
        </h2>
        <p className="mt-1 text-sm text-texto-2">
          Escribí una categoría y elegí el país. La IA te sugiere hasta 5 productos con su evidencia.
        </p>

        <form onSubmit={buscar} className="mt-5 flex flex-col gap-3 sm:flex-row">
          <label htmlFor="buscar-categoria" className="sr-only">
            Categoría a investigar
          </label>
          <input
            id="buscar-categoria"
            type="text"
            value={categoria}
            onChange={(e) => {
              setCategoria(e.target.value);
              if (error) setError(null);
            }}
            placeholder="Ej: mochilas antirrobo"
            disabled={buscando}
            aria-invalid={Boolean(error)}
            aria-describedby={error ? "buscar-error" : undefined}
            className={`${CAMPO} sm:flex-1 py-3 text-base sm:text-sm`}
          />
          <label htmlFor="buscar-mercado" className="sr-only">
            País donde vas a vender
          </label>
          <select
            id="buscar-mercado"
            value={mercado}
            onChange={(e) => setMercado(e.target.value)}
            disabled={buscando}
            className={`${CAMPO} py-3 sm:w-52`}
          >
            {Object.entries(MERCADOS).map(([codigo, m]) => (
              <option key={codigo} value={codigo}>
                {m.bandera} {m.nombre}
              </option>
            ))}
          </select>
          <button type="submit" disabled={buscando} className={`${BOTON_PRIMARIO} py-3`}>
            {buscando ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                Buscando...
              </>
            ) : (
              <>
                <Search className="h-4 w-4" aria-hidden="true" />
                Buscar productos
              </>
            )}
          </button>
        </form>

        {!buscando && (
          <div className="mt-4 flex flex-wrap items-center gap-2 text-xs">
            <span className="text-texto-2">Probá con:</span>
            {EJEMPLOS.map((ejemplo) => (
              <button
                key={ejemplo}
                type="button"
                onClick={() => setCategoria(ejemplo)}
                className="rounded-full border border-borde-fuerte bg-fondo/60 px-3 py-1 text-texto-2 transition-colors hover:border-acento-borde hover:text-texto"
              >
                {ejemplo}
              </button>
            ))}
          </div>
        )}

        <div aria-live="polite">
          {buscando && (
            <p className="mt-4 flex items-center gap-2 text-sm text-texto-2 animate-aparecer">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-acento opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-acento" />
              </span>
              La IA está investigando. Puede tardar unos segundos...
            </p>
          )}
          {exito && !buscando && (
            <p className="mt-4 text-sm text-verde animate-aparecer">{exito}</p>
          )}
        </div>
        {error && (
          <p id="buscar-error" role="alert" className="mt-4 text-sm text-rojo">
            {error}
          </p>
        )}
      </div>
    </section>
  );
}
