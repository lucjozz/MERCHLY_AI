"use client";

import { useState } from "react";
import { Sparkles } from "lucide-react";
import { generarCampanaMarketing, type CampanaMarketing } from "@/lib/api/marketing";
import TextoAnimado from "@/components/TextoAnimado";

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
    } catch {
      setError("No se pudo generar la campaña. ¿Está corriendo el backend?");
    } finally {
      setGenerando(false);
    }
  }

  if (estado !== "en_catalogo") {
    return null;
  }

  return (
    <section className="rounded-lg border border-[#2D1F47] bg-[#1A1229] p-6 mt-8">
      <h2 className="text-sm font-medium uppercase tracking-widest text-[#A78BFA] mb-4 flex items-center gap-2">
        <Sparkles className="h-4 w-4" aria-hidden="true" />
        Agente de Marketing (IA)
      </h2>

      {!campana && (
        <button
          onClick={generar}
          disabled={generando}
          className="inline-flex items-center gap-2 bg-[#8B5CF6] hover:bg-[#7C3AED] text-white px-5 py-3 rounded-md text-sm font-semibold transition-all hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100"
        >
          <Sparkles className="h-4 w-4" aria-hidden="true" />
          {generando ? "Generando campaña..." : "Generar Campaña de Marketing"}
        </button>
      )}

      {error && <p className="mt-4 text-sm text-[#E88B8B]">{error}</p>}

      {campana && (
        <div className="space-y-6 animate-in fade-in duration-500">
          <div>
            <p className="text-[#A78BFA] text-xs mb-2">Ángulos de campaña</p>
            <ul className="space-y-1">
              {campana.angulos_de_campana.map((angulo, i) => (
                <li key={i} className="text-[#F5F7FA] text-sm">
                  <TextoAnimado texto={`• ${angulo}`} />
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="text-[#A78BFA] text-xs mb-2">Público objetivo sugerido</p>
            <p className="text-[#F5F7FA] text-sm">
              <TextoAnimado texto={campana.publico_objetivo_sugerido} />
            </p>
          </div>

          {Object.entries(campana.copy_por_canal).map(([canal, copies]) => (
            <div key={canal}>
              <p className="text-[#A78BFA] text-xs mb-2 font-mono">{canal}</p>
              {copies.map((copy, i) => (
                <div
                  key={i}
                  className="bg-[#0B0D12] border border-[#2D1F47] rounded-md p-4 mb-2"
                >
                  <p className="text-[#A78BFA] text-sm font-semibold mb-1">
                    <TextoAnimado texto={copy.titulo} />
                  </p>
                  <p className="text-[#7C8699] text-sm">
                    <TextoAnimado texto={copy.cuerpo} velocidad={8} />
                  </p>
                </div>
              ))}
            </div>
          ))}

          {campana.advertencias.length > 0 && (
            <div className="bg-[#3A2E12] border border-[#4A3A17] rounded-md p-3">
              {campana.advertencias.map((advertencia, i) => (
                <p key={i} className="text-[#E8B84B] text-xs">
                  ⚠ {advertencia}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}