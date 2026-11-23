"use client";

/**
 * Elegir una contraseña nueva con el link del email (DEC-036). El token viene
 * en el fragmento (#): no llega al servidor ni queda en logs. Al cambiarla se
 * cierran todas las sesiones abiertas.
 */
import { useEffect, useState } from "react";
import { KeyRound } from "lucide-react";
import PantallaPublica from "@/components/PantallaPublica";
import { MENSAJE_SIN_CONEXION, mensajeDeError } from "@/lib/api/errores";
import { BOTON_PRIMARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";

export default function Restablecer() {
  const [token, setToken] = useState<string | null>(null);
  const [password, setPassword] = useState("");
  const [repetida, setRepetida] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [listo, setListo] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const valor = window.location.hash.slice(1);
    window.history.replaceState(null, "", window.location.pathname);
    // eslint-disable-next-line react-hooks/set-state-in-effect -- el fragmento solo se lee en el cliente
    setToken(valor);
  }, []);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== repetida) return setError("Las contraseñas no coinciden.");
    setEnviando(true);
    try {
      const r = await fetch("/api/auth/restablecer-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      });
      if (!r.ok) {
        const cuerpo = await r.json().catch(() => ({}));
        const detalle = typeof cuerpo?.detail === "string" ? cuerpo.detail : undefined;
        throw new Error(r.status === 400 || r.status === 422 ? detalle ?? mensajeDeError(r.status) : mensajeDeError(r.status, detalle, r.headers.get("retry-after")));
      }
      setListo(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : MENSAJE_SIN_CONEXION);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <PantallaPublica titulo="Elegí una contraseña nueva">
      {listo ? (
        <div role="status" className="mt-4 space-y-4">
          <p className="text-sm text-texto-2">Listo: tu contraseña cambió y cerramos tu sesión en todos los dispositivos.</p>
          <a href="/login" className={`w-full py-3 ${BOTON_PRIMARIO}`}>Iniciar sesión</a>
        </div>
      ) : token === "" ? (
        <p className="mt-4 text-sm text-rojo">Este link no es válido. Pedí uno nuevo desde “¿Olvidaste tu contraseña?”.</p>
      ) : (
        <form onSubmit={enviar} className="mt-4 space-y-4">
          <div>
            <label htmlFor="r-pass" className={ETIQUETA_CAMPO}>Contraseña nueva (mínimo 12 caracteres)</label>
            <input id="r-pass" type="password" required minLength={12} maxLength={72} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} className={CAMPO} />
          </div>
          <div>
            <label htmlFor="r-pass2" className={ETIQUETA_CAMPO}>Repetila</label>
            <input id="r-pass2" type="password" required minLength={12} maxLength={72} autoComplete="new-password" value={repetida} onChange={(e) => setRepetida(e.target.value)} className={CAMPO} />
          </div>
          {error && <p role="alert" className="rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">{error}</p>}
          <button type="submit" disabled={enviando || token === null} className={`w-full py-3 ${BOTON_PRIMARIO}`}>
            <KeyRound className="h-4 w-4" aria-hidden="true" /> {enviando ? "Guardando…" : "Cambiar contraseña"}
          </button>
        </form>
      )}
    </PantallaPublica>
  );
}
