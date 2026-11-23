import type { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
  /** Agrega elevación sutil al pasar el mouse (para tarjetas clickeables). */
  interactiva?: boolean;
  as?: "div" | "section" | "article" | "li";
  "aria-label"?: string;
  id?: string;
  style?: React.CSSProperties;
}

export default function Card({
  children,
  className = "",
  interactiva = false,
  as: Etiqueta = "div",
  ...resto
}: CardProps) {
  return (
    <Etiqueta
      {...resto}
      className={`rounded-2xl border border-borde bg-superficie p-5 sm:p-6 ${
        interactiva
          ? "transition-all duration-200 hover:-translate-y-0.5 hover:border-borde-fuerte hover:bg-superficie-2 hover:shadow-lg hover:shadow-black/30"
          : ""
      } ${className}`}
    >
      {children}
    </Etiqueta>
  );
}

export function TituloCard({
  children,
  descripcion,
  accion,
}: {
  children: ReactNode;
  descripcion?: ReactNode;
  accion?: ReactNode;
}) {
  return (
    <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
      <div className="min-w-0">
        <h2 className="text-base font-semibold text-texto sm:text-lg">{children}</h2>
        {descripcion && (
          <p className="mt-1 text-sm leading-relaxed text-texto-2">{descripcion}</p>
        )}
      </div>
      {accion}
    </div>
  );
}
