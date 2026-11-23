"use client";

import { usePathname } from "next/navigation";
import { MessageCircle } from "lucide-react";

/** Número de soporte con código de país y sin "+" (ej.: 59170000000). Vacío = sin botón. */
const NUMERO = (process.env.NEXT_PUBLIC_SOPORTE_WHATSAPP ?? "").replace(/\D/g, "");
const OCULTO_EN = ["/login", "/invitacion", "/restablecer"];

/** Botón flotante de ayuda por WhatsApp (docs/004-Backend/03, sección 7). */
export default function BotonSoporte() {
  const pathname = usePathname();
  if (!NUMERO || OCULTO_EN.some((r) => pathname.startsWith(r))) return null;
  const mensaje = encodeURIComponent("Hola, necesito ayuda con MERCHLY AI.");
  return (
    <a
      href={`https://wa.me/${NUMERO}?text=${mensaje}`}
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Pedir ayuda por WhatsApp"
      className="fixed bottom-20 right-4 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-verde text-fondo shadow-lg shadow-black/40 transition-transform hover:scale-105 md:bottom-6 md:right-6"
    >
      <MessageCircle className="h-6 w-6" aria-hidden="true" />
    </a>
  );
}
