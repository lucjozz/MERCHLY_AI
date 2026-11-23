import type { LucideIcon } from "lucide-react";

const COLOR = {
  texto: { texto: "text-texto", icono: "text-texto-2 bg-superficie-2" },
  azul: { texto: "text-acento-claro", icono: "text-acento-claro bg-acento-hondo/50" },
  ambar: { texto: "text-ambar", icono: "text-ambar bg-ambar-fondo" },
  verde: { texto: "text-verde", icono: "text-verde bg-verde-fondo" },
  gris: { texto: "text-texto-2", icono: "text-texto-2 bg-gris-fondo" },
};

interface MetricaProps {
  etiqueta: string;
  valor: string | number;
  icono: LucideIcon;
  color?: keyof typeof COLOR;
  detalle?: string;
  retraso?: number;
}

/** Tarjeta de número grande con explicación corta debajo. */
export default function Metrica({
  etiqueta,
  valor,
  icono: Icono,
  color = "texto",
  detalle,
  retraso = 0,
}: MetricaProps) {
  const estilo = COLOR[color];
  return (
    <div
      className="rounded-2xl border border-borde bg-superficie p-4 transition-colors hover:border-borde-fuerte animate-aparecer sm:p-5"
      style={{ animationDelay: `${retraso}ms` }}
    >
      <div className="flex items-center gap-2.5">
        <span
          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${estilo.icono}`}
        >
          <Icono className="h-4 w-4" aria-hidden="true" />
        </span>
        <span className="text-xs font-medium text-texto-2 sm:text-sm">{etiqueta}</span>
      </div>
      <p className={`mt-3 text-3xl font-bold tabular-nums tracking-tight ${estilo.texto}`}>
        {valor}
      </p>
      {detalle && <p className="mt-1 text-xs leading-relaxed text-texto-2">{detalle}</p>}
    </div>
  );
}
