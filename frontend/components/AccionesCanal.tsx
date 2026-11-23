"use client";

/**
 * Canales de venta reales sin publicación automática (docs/004-Backend/03, sección 2):
 * copiar, compartir por WhatsApp y enviar por email. La persona decide dónde
 * y cuándo publicar: la IA nunca publica sola.
 */
import { useState } from "react";
import { Check, Copy, Mail, MessageCircle } from "lucide-react";

interface AccionesCanalProps {
  titulo: string;
  cuerpo: string;
}

const BOTON =
  "inline-flex items-center gap-1.5 rounded-lg border border-borde px-2.5 py-1.5 text-xs font-medium text-texto-2 transition-colors hover:border-borde-fuerte hover:text-texto focus-visible:outline-2";

export default function AccionesCanal({ titulo, cuerpo }: AccionesCanalProps) {
  const [copiado, setCopiado] = useState(false);
  const texto = titulo ? `${titulo}\n\n${cuerpo}` : cuerpo;

  async function copiar() {
    try {
      await navigator.clipboard.writeText(texto);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      window.prompt("Copiá el texto:", texto);
    }
  }

  // Límite prudente para que el link no sea gigante.
  const corto = texto.slice(0, 1800);
  const whatsapp = `https://wa.me/?text=${encodeURIComponent(corto)}`;
  const email = `mailto:?subject=${encodeURIComponent(titulo.slice(0, 150))}&body=${encodeURIComponent(cuerpo.slice(0, 1800))}`;

  return (
    <div className="mt-3 flex flex-wrap gap-2">
      <button type="button" onClick={copiar} className={BOTON} aria-live="polite">
        {copiado ? <Check className="h-3.5 w-3.5 text-verde" aria-hidden="true" /> : <Copy className="h-3.5 w-3.5" aria-hidden="true" />}
        {copiado ? "¡Copiado!" : "Copiar"}
      </button>
      <a href={whatsapp} target="_blank" rel="noopener noreferrer" className={BOTON}>
        <MessageCircle className="h-3.5 w-3.5 text-verde" aria-hidden="true" />
        WhatsApp
      </a>
      <a href={email} className={BOTON}>
        <Mail className="h-3.5 w-3.5" aria-hidden="true" />
        Email
      </a>
    </div>
  );
}
