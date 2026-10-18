"use client";

import { useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import {
  generarCampanaMarketing,
  type CampanaMarketing,
  type CanalMarketing,
  type TonoMarketing,
} from "@/lib/api/marketing";
import TextoAnimado from "@/components/TextoAnimado";

interface ProductoAprobado {
  id: string;
  nombre_producto: string;
}

const CANALES: { valor: CanalMarketing; etiqueta: string }[] = [
  { valor: "redes_sociales", etiqueta: "Redes sociales" },
  { valor: "busqueda_paga", etiqueta: "Búsqueda paga" },
  { valor: "email", etiqueta: "Email" },
];

const TONOS: { valor: TonoMarketing; etiqueta: string }[] = [
  { valor: "neutral", etiqueta: "Neutral" },
  { valor: "entusiasta", etiqueta: "Entusiasta" },
  { valor: "tecnico", etiqueta: "Técnico" },
  { valor: "premium", etiqueta: "Premium" },
];

const ETIQUETA_CANAL: Record<string, string> = {
  redes_sociales: "Redes sociales",
  busqueda_paga: "Búsqueda paga",
  email: "Email",
};

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
    } catch {
      setError("No se pudo generar la campaña. ¿Está corriendo el backend?");
    } finally {
      setGenerando(false);
    }
  }

  const totalCopys = campana
    ? Object.values(campana.copy_por_canal).reduce((n, v) => n + v.length, 0)
    : 0;
  const nombreProducto = productos.find((p) => p.id === productoId)?.nombre_producto;

  return (
    <div className="grid grid-cols-[1fr_320px] gap-6">
      <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6">
        <label className="text-[#7C8699] text-xs uppercase tracking-wide block mb-2">
          Producto aprobado
        </label>
        <select
          value={productoId}
          onChange={(e) => setProductoId(e.target.value)}
          className="w-full bg-[#0B0D12] border border-[#242938] text-[#F5F7FA] rounded-md px-3 py-2.5 text-sm outline-none focus:border-[#8B5CF6] mb-6"
        >
          {productos.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nombre_producto}
            </option>
          ))}
        </select>

        <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-2">Canales</p>
        <div className="flex flex-wrap gap-2 mb-6">
          {CANALES.map((c) => {
            const activo = canales.includes(c.valor);
            return (
              <button
                key={c.valor}
                type="button"
                onClick={() => alternarCanal(c.valor)}
                className={`px-4 py-2 rounded-md text-sm border transition-colors ${
                  activo
                    ? "bg-[#1A1229] border-[#8B5CF6] text-[#A78BFA]"
                    : "bg-[#0B0D12] border-[#242938] text-[#7C8699] hover:text-[#F5F7FA]"
                }`}
              >
                {c.etiqueta}
              </button>
            );
          })}
        </div>

        <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-2">Tono</p>
        <div className="flex flex-wrap gap-2 mb-6">
          {TONOS.map((t) => (
            <button
              key={t.valor}
              type="button"
              onClick={() => setTono(t.valor)}
              className={`px-4 py-2 rounded-md text-sm border transition-colors ${
                tono === t.valor
                  ? "bg-[#1E3A5F] border-[#3D7DD8] text-[#F5F7FA]"
                  : "bg-[#0B0D12] border-[#242938] text-[#7C8699] hover:text-[#F5F7FA]"
              }`}
            >
              {t.etiqueta}
            </button>
          ))}
        </div>

        <button
          onClick={generar}
          disabled={generando}
          className="inline-flex items-center gap-2 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white px-5 py-3 rounded-md text-sm font-semibold transition-all hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100"
        >
          {generando ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Sparkles className="h-4 w-4" aria-hidden="true" />
          )}
          {generando ? "Generando campaña..." : "Generar campaña"}
        </button>

        {error && <p className="mt-4 text-sm text-[#E88B8B]">{error}</p>}

        {campana && (
          <div className="mt-8 pt-6 border-t border-[#1F2430] space-y-6">
            <h2 className="text-lg font-semibold text-[#F5F7FA]">
              Campaña: {nombreProducto}
            </h2>

            <div>
              <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-3">
                Ángulos creativos
              </p>
              <div className="space-y-2">
                {campana.angulos_de_campana.map((angulo, i) => (
                  <div key={i} className="flex gap-3 text-sm">
                    <span className="text-[#3D7DD8] font-mono">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span className="text-[#F5F7FA]">
                      <TextoAnimado texto={angulo} />
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {Object.entries(campana.copy_por_canal).map(([canal, copies]) => (
              <div key={canal}>
                <p className="text-[#A78BFA] text-xs uppercase tracking-wide mb-2">
                  {ETIQUETA_CANAL[canal] ?? canal}
                </p>
                {copies.map((copy, i) => (
                  <div
                    key={i}
                    className="bg-[#0B0D12] border border-[#2D1F47] rounded-md p-4 mb-2"
                  >
                    <p className="text-[#F5F7FA] text-sm font-semibold mb-1">
                      <TextoAnimado texto={copy.titulo} />
                    </p>
                    <p className="text-[#7C8699] text-sm">
                      <TextoAnimado texto={copy.cuerpo} velocidad={8} />
                    </p>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-[#1A1229] border border-[#2D1F47] rounded-lg p-6 h-fit">
        <p className="text-[#A78BFA] text-xs uppercase tracking-wide mb-5">
          Salida IA
        </p>
        <div className="space-y-5">
          <div>
            <p className="text-4xl font-bold text-[#F5F7FA]">
              {campana ? campana.angulos_de_campana.length : 0}
            </p>
            <p className="text-[#7C8699] text-sm">ángulos</p>
          </div>
          <div>
            <p className="text-4xl font-bold text-[#F5F7FA]">{totalCopys}</p>
            <p className="text-[#7C8699] text-sm">copys</p>
          </div>
          <div>
            <p className="text-4xl font-bold text-[#F5F7FA]">
              {campana ? Object.keys(campana.copy_por_canal).length : 0}
            </p>
            <p className="text-[#7C8699] text-sm">canales</p>
          </div>
        </div>

        {campana && (
          <div className="border-t border-[#2D1F47] mt-6 pt-5">
            <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-2">
              Público sugerido
            </p>
            <p className="text-[#F5F7FA] text-sm">
              {campana.publico_objetivo_sugerido}
            </p>
            {campana.advertencias.length > 0 && (
              <div className="mt-4 bg-[#3A2E12] border border-[#4A3A17] rounded-md p-3 space-y-1">
                {campana.advertencias.map((a, i) => (
                  <p key={i} className="text-[#E8B84B] text-xs">
                    ⚠ {a}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}