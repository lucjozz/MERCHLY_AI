"use client";

/** Pedir el link para restablecer la contraseña (DEC-036). Misma respuesta exista o no el email. */
import { useState } from "react";
import { Mail } from "lucide-react";
import PantallaPublica from "@/components/PantallaPublica";
import { MENSAJE_SIN_CONEXION, mensajeDeError } from "@/lib/api/errores";
import { BOTON_PRIMARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";

export default function OlvidePassword() {
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [enviado, setEnviado] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const r = await fetch("/api/auth/olvide-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim() }),
      });
      if (!r.ok) {
        const cuerpo = await r.json().catch(() => ({}));
        throw new Error(mensajeDeError(r.status, cuerpo?.detail, r.headers.get("retry-after")));
      }
      setEnviado(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : MENSAJE_SIN_CONEXION);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <PantallaPublica titulo="¿Olvidaste tu contraseña?">
      {enviado ? (
        <p role="status" className="mt-4 text-sm leading-relaxed text-texto-2">
          Si <span className="font-medium text-texto">{email}</span> está registrado, te mandamos un email con un link para
          elegir una contraseña nueva. Vence en 1 hora. Revisá también la carpeta de spam.
        </p>
      ) : (
        <form onSubmit={enviar} className="mt-4 space-y-4">
          <p className="text-sm text-texto-2">Escribí tu email y te mandamos un link para elegir una nueva.</p>
          <div>
            <label htmlFor="o-email" className={ETIQUETA_CAMPO}>Email</label>
            <input id="o-email" type="email" required maxLength={255} autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} className={CAMPO} />
          </div>
          {error && <p role="alert" className="rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">{error}</p>}
          <button type="submit" disabled={enviando} className={`w-full py-3 ${BOTON_PRIMARIO}`}>
            <Mail className="h-4 w-4" aria-hidden="true" /> {enviando ? "Enviando…" : "Mandarme el link"}
          </button>
        </form>
      )}
    </PantallaPublica>
  );
}
