import type { ReactNode } from "react";
import { FlaskConical } from "lucide-react";
import { infoEstado, type Tono } from "@/lib/etiquetas";

const ESTILO_TONO: Record<Tono, string> = {
  ambar: "bg-ambar-fondo text-ambar border-ambar-borde",
  verde: "bg-verde-fondo text-verde border-verde-borde",
  azul: "bg-acento-hondo/60 text-acento-claro border-acento-borde",
  gris: "bg-gris-fondo text-texto-2 border-borde-fuerte",
  rojo: "bg-rojo-fondo text-rojo border-rojo-borde",
};

const COLOR_PUNTO: Record<Tono, string> = {
  ambar: "bg-ambar",
  verde: "bg-verde",
  azul: "bg-acento-claro",
  gris: "bg-texto-2",
  rojo: "bg-rojo",
};

interface BadgeProps {
  tono?: Tono;
  children: ReactNode;
  punto?: boolean;
  title?: string;
  className?: string;
}

export default function Badge({
  tono = "gris",
  children,
  punto = false,
  title,
  className = "",
}: BadgeProps) {
  return (
    <span
      title={title}
      className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-0.5 text-xs font-medium ${ESTILO_TONO[tono]} ${className}`}
    >
      {punto && (
        <span
          className={`h-1.5 w-1.5 rounded-full ${COLOR_PUNTO[tono]}`}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
}

/** Badge del estado de un producto con su etiqueta humana. */
export function BadgeEstado({ estado }: { estado: string }) {
  const info = infoEstado(estado);
  return (
    <Badge tono={info.tono} punto title={info.descripcion || undefined}>
      {info.etiqueta}
    </Badge>
  );
}

/** Marca visible (pero no alarmante) para resultados de proveedores simulados. */
export function BadgeSimulado({ className = "" }: { className?: string }) {
  return (
    <span
      title="Dato de prueba generado por un proveedor simulado. No lo uses para decisiones reales."
      className={`inline-flex items-center gap-1 whitespace-nowrap rounded-full border border-dashed border-acento-borde bg-acento-hondo/30 px-2.5 py-0.5 text-xs font-medium text-acento-claro ${className}`}
    >
      <FlaskConical className="h-3 w-3" aria-hidden="true" />
      Simulado
    </span>
  );
}
