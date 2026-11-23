import type { ReactNode } from "react";
import { Sparkles } from "lucide-react";

/** Marco común de las pantallas públicas (sin sesión): olvidé mi contraseña, restablecer. */
export default function PantallaPublica({ titulo, children }: { titulo: string; children: ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-fondo">
      <div className="mx-auto flex min-h-full max-w-md flex-col justify-center px-4 py-10">
        <div className="mb-6 flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-acento to-acento-hondo">
            <Sparkles className="h-5 w-5 text-white" aria-hidden="true" />
          </span>
          <p className="font-bold text-texto">MERCHLY AI</p>
        </div>
        <div className="rounded-2xl border border-borde bg-superficie p-6 animate-aparecer">
          <h1 className="text-xl font-bold text-texto">{titulo}</h1>
          {children}
        </div>
        <a href="/login" className="mt-4 text-center text-sm text-texto-2 hover:text-texto">
          Volver a iniciar sesión
        </a>
      </div>
    </div>
  );
}
