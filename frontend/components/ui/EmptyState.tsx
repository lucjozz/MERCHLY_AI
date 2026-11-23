import type { ReactNode } from "react";
import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { ArrowRight } from "lucide-react";
import { BOTON_PRIMARIO } from "@/components/ui/estilos";

interface EmptyStateProps {
  icono: LucideIcon;
  titulo: string;
  descripcion: ReactNode;
  accion?: { href: string; texto: string };
  compacto?: boolean;
}

export default function EmptyState({
  icono: Icono,
  titulo,
  descripcion,
  accion,
  compacto = false,
}: EmptyStateProps) {
  return (
    <div
      className={`flex flex-col items-center rounded-2xl border border-dashed border-borde-fuerte bg-superficie/50 text-center animate-aparecer ${
        compacto ? "px-4 py-8" : "px-6 py-14"
      }`}
    >
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full border border-borde bg-superficie-2">
        <Icono className="h-5 w-5 text-acento-claro" aria-hidden="true" />
      </div>
      <p className="font-semibold text-texto">{titulo}</p>
      <div className="mt-1.5 max-w-md text-sm leading-relaxed text-texto-2">
        {descripcion}
      </div>
      {accion && (
        <Link href={accion.href} className={`group mt-5 ${BOTON_PRIMARIO}`}>
          {accion.texto}
          <ArrowRight
            className="h-4 w-4 transition-transform group-hover:translate-x-0.5"
            aria-hidden="true"
          />
        </Link>
      )}
    </div>
  );
}
