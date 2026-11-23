"use client";

import { useState } from "react";
import { LogOut } from "lucide-react";
import { cerrarSesion } from "@/lib/api/auth";

/** Cierra la sesión de verdad: revoca los tokens en el backend, no solo borra cookies. */
export default function BotonCerrarSesion() {
  const [cerrando, setCerrando] = useState(false);

  async function salir() {
    setCerrando(true);
    await cerrarSesion();
  }

  return (
    <button
      onClick={salir}
      disabled={cerrando}
      type="button"
      className="inline-flex items-center gap-2 rounded-lg border border-rojo-borde bg-rojo-fondo px-5 py-2.5 text-sm font-semibold text-rojo transition-colors hover:bg-rojo-borde hover:text-texto disabled:opacity-60"
    >
      <LogOut className="h-4 w-4" aria-hidden="true" />
      {cerrando ? "Cerrando sesión…" : "Cerrar sesión"}
    </button>
  );
}
