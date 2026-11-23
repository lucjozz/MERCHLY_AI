"use client";

import { useState } from "react";
import { Building2, KeyRound, LogOut, RefreshCw, ShieldCheck } from "lucide-react";
import { cerrarSesion } from "@/lib/api/auth";

interface SesionInfoProps {
  organizacion?: string | null;
}

/**
 * Información de la sesión. El token vive en una cookie HttpOnly que
 * JavaScript NO puede leer (protección contra robo por XSS), así que acá
 * se explica cómo funciona la sesión en vez de mostrar el token.
 */
export default function SesionInfo({ organizacion }: SesionInfoProps) {
  const [cerrando, setCerrando] = useState(false);

  async function cerrarTodas() {
    if (!window.confirm("Se va a cerrar tu sesión en todos tus dispositivos (también en este). ¿Seguimos?")) return;
    setCerrando(true);
    await cerrarSesion(true);
  }

  const filas = [
    { icono: Building2, titulo: "Negocio", texto: organizacion ?? "—" },
    {
      icono: RefreshCw,
      titulo: "Renovación automática",
      texto: "Tu acceso se renueva solo cada 15 minutos mientras usás la app.",
    },
    {
      icono: KeyRound,
      titulo: "Vencimiento",
      texto: "Si no entrás durante 14 días, vas a tener que iniciar sesión de nuevo.",
    },
    {
      icono: ShieldCheck,
      titulo: "Protección",
      texto: "Tu sesión está guardada de forma que ningún script de la página puede leerla.",
    },
  ];

  return (
    <div className="space-y-4 text-sm">
      <ul className="space-y-3">
        {filas.map(({ icono: Icono, titulo, texto }) => (
          <li key={titulo} className="flex gap-3">
            <Icono className="mt-0.5 h-4 w-4 shrink-0 text-acento-claro" aria-hidden="true" />
            <div>
              <p className="font-medium text-texto">{titulo}</p>
              <p className="text-texto-2">{texto}</p>
            </div>
          </li>
        ))}
      </ul>
      <button
        type="button"
        onClick={cerrarTodas}
        disabled={cerrando}
        className="inline-flex items-center gap-2 rounded-lg border border-borde px-4 py-2 text-sm text-texto-2 transition-colors hover:border-rojo-borde hover:text-rojo disabled:opacity-60"
      >
        <LogOut className="h-4 w-4" aria-hidden="true" />
        {cerrando ? "Cerrando sesiones…" : "Cerrar sesión en todos mis dispositivos"}
      </button>
    </div>
  );
}
