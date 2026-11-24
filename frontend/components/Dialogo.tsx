"use client";

/** Ventana modal accesible con <dialog> nativo (foco atrapado, Escape cierra). */
import { useEffect, useRef, type ReactNode } from "react";
import { X } from "lucide-react";

interface Props {
  titulo: string;
  descripcion?: string;
  onCerrar: () => void;
  children: ReactNode;
  ancho?: string;
}

export default function Dialogo({ titulo, descripcion, onCerrar, children, ancho = "max-w-2xl" }: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialogo = ref.current;
    if (dialogo && !dialogo.open) dialogo.showModal();
  }, []);
  return (
    <dialog
      ref={ref}
      onCancel={(e) => {
        e.preventDefault();
        onCerrar();
      }}
      aria-labelledby="dialogo-titulo"
      className={`m-auto w-[calc(100%-2rem)] ${ancho} rounded-2xl border border-borde bg-superficie p-0 text-texto shadow-2xl backdrop:bg-black/60`}
    >
      <div className="flex items-start justify-between gap-4 border-b border-borde px-5 py-4">
        <div>
          <h2 id="dialogo-titulo" className="text-lg font-semibold">{titulo}</h2>
          {descripcion && <p className="mt-1 text-sm text-texto-2">{descripcion}</p>}
        </div>
        <button type="button" onClick={onCerrar} className="rounded-lg p-1.5 text-texto-2 hover:bg-superficie-2 hover:text-texto" aria-label="Cerrar">
          <X className="h-5 w-5" aria-hidden="true" />
        </button>
      </div>
      <div className="max-h-[75vh] overflow-y-auto px-5 py-4">{children}</div>
    </dialog>
  );
}
