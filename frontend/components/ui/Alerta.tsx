import type { ReactNode } from "react";
import { AlertCircle, Info } from "lucide-react";

interface AlertaProps {
  children: ReactNode;
  tipo?: "error" | "info";
  className?: string;
}

/** Mensaje de error o aviso. Los errores se anuncian a lectores de pantalla. */
export default function Alerta({ children, tipo = "error", className = "" }: AlertaProps) {
  const esError = tipo === "error";
  const Icono = esError ? AlertCircle : Info;
  return (
    <div
      role={esError ? "alert" : "status"}
      className={`flex items-start gap-3 rounded-xl border px-4 py-3 text-sm leading-relaxed animate-aparecer ${
        esError
          ? "border-rojo-borde bg-rojo-fondo text-rojo"
          : "border-borde bg-superficie text-texto-2"
      } ${className}`}
    >
      <Icono className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <div>{children}</div>
    </div>
  );
}

export const MENSAJE_SIN_BACKEND =
  "No pudimos conectarnos con el servidor de MERCHLY. Probá recargar la página en unos segundos.";
