import { etiquetaNivel, valorNivel } from "@/lib/etiquetas";

interface MedidorProps {
  etiqueta: string;
  nivel: string;
  /** "favorable-alto": más es mejor (demanda). "favorable-bajo": menos es mejor (competencia). */
  sentido: "favorable-alto" | "favorable-bajo";
  compacto?: boolean;
}

/** Medidor de 3 barras para niveles bajo / medio / alto. */
export default function Medidor({ etiqueta, nivel, sentido, compacto = false }: MedidorProps) {
  const valor = valorNivel(nivel);
  const bueno = sentido === "favorable-alto" ? valor === 3 : valor === 1;
  const malo = sentido === "favorable-alto" ? valor === 1 : valor === 3;
  const color = bueno ? "bg-verde" : malo ? "bg-ambar" : "bg-acento";

  return (
    <div>
      <p className="text-xs text-texto-2">{etiqueta}</p>
      <div className="mt-1.5 flex items-center gap-2">
        <div className="flex gap-1" aria-hidden="true">
          {[1, 2, 3].map((i) => (
            <span
              key={i}
              className={`h-1.5 rounded-full ${compacto ? "w-3" : "w-5"} ${
                i <= valor ? color : "bg-borde-fuerte"
              }`}
            />
          ))}
        </div>
        <span className={`font-medium text-texto ${compacto ? "text-xs" : "text-sm"}`}>
          {etiquetaNivel(nivel)}
        </span>
      </div>
    </div>
  );
}
