import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { Lightbulb } from "lucide-react";

interface PageHeaderProps {
  titulo: string;
  descripcion: ReactNode;
  icono?: LucideIcon;
  /** Explicación corta de "qué hago acá" para usuarios nuevos. */
  ayuda?: ReactNode;
  acciones?: ReactNode;
}

export default function PageHeader({
  titulo,
  descripcion,
  icono: Icono,
  ayuda,
  acciones,
}: PageHeaderProps) {
  return (
    <header className="mb-8 animate-aparecer">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex min-w-0 items-start gap-4">
          {Icono && (
            <div className="hidden h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-acento-borde bg-gradient-to-br from-acento-hondo to-superficie sm:flex">
              <Icono className="h-6 w-6 text-acento-claro" aria-hidden="true" />
            </div>
          )}
          <div className="min-w-0">
            <h1 className="text-2xl font-bold tracking-tight text-texto sm:text-3xl">
              {titulo}
            </h1>
            <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-texto-2 sm:text-base">
              {descripcion}
            </p>
          </div>
        </div>
        {acciones && <div className="flex flex-wrap gap-2">{acciones}</div>}
      </div>

      {ayuda && (
        <div className="mt-5 flex max-w-3xl items-start gap-3 rounded-xl border border-borde bg-superficie/60 px-4 py-3 text-sm text-texto-2">
          <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-ambar" aria-hidden="true" />
          <div className="leading-relaxed">
            <span className="font-medium text-texto">¿Qué hago acá? </span>
            {ayuda}
          </div>
        </div>
      )}
    </header>
  );
}
