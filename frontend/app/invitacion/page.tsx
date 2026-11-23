"use client";

/**
 * Aceptar una invitación (pública). El token llega en el fragmento de la URL
 * (/invitacion#token): el navegador no lo envía al servidor, así que no queda
 * en logs ni en el header Referer.
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, UserPlus } from "lucide-react";
import { aceptarInvitacion } from "@/lib/api/acciones";
import { BOTON_PRIMARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";

export default function AceptarInvitacion() {
  const router = useRouter();
  const [token, setToken] = useState<string | null>(null);
  const [nombre, setNombre] = useState("");
  const [password, setPassword] = useState("");
  const [repetida, setRepetida] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const valor = window.location.hash.slice(1);
    // Se saca el token de la barra de direcciones apenas se lee.
    window.history.replaceState(null, "", window.location.pathname);
    // eslint-disable-next-line react-hooks/set-state-in-effect -- leer el fragmento solo es posible en el cliente
    setToken(valor || "");
  }, []);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password !== repetida) {
      setError("Las contraseñas no coinciden.");
      return;
    }
    if (!token) return;
    setEnviando(true);
    try {
      await aceptarInvitacion(token, nombre.trim(), password);
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo aceptar la invitación.");
      setEnviando(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-fondo">
      <div className="mx-auto flex min-h-full max-w-md flex-col justify-center px-4 py-10">
        <div className="mb-6 flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-acento to-acento-hondo">
            <Sparkles className="h-5 w-5 text-white" aria-hidden="true" />
          </span>
          <p className="font-bold text-texto">MERCHLY AI</p>
        </div>
        <div className="rounded-2xl border border-borde bg-superficie p-6">
          <h1 className="text-xl font-bold text-texto">Te invitaron a un negocio</h1>
          {token === "" ? (
            <p className="mt-3 text-sm text-rojo">Este link no tiene una invitación. Pedile al admin de tu negocio que te mande uno nuevo.</p>
          ) : (
            <form onSubmit={enviar} className="mt-5 space-y-4">
              <div>
                <label htmlFor="i-nombre" className={ETIQUETA_CAMPO}>Tu nombre</label>
                <input id="i-nombre" required minLength={2} maxLength={120} value={nombre} onChange={(e) => setNombre(e.target.value)} className={CAMPO} />
              </div>
              <div>
                <label htmlFor="i-pass" className={ETIQUETA_CAMPO}>Elegí una contraseña (mínimo 12 caracteres)</label>
                <input id="i-pass" type="password" required minLength={12} maxLength={72} autoComplete="new-password" value={password} onChange={(e) => setPassword(e.target.value)} className={CAMPO} />
              </div>
              <div>
                <label htmlFor="i-pass2" className={ETIQUETA_CAMPO}>Repetila</label>
                <input id="i-pass2" type="password" required minLength={12} maxLength={72} autoComplete="new-password" value={repetida} onChange={(e) => setRepetida(e.target.value)} className={CAMPO} />
              </div>
              {error && <p role="alert" className="rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">{error}</p>}
              <button type="submit" disabled={enviando || token === null} className={`w-full py-3 ${BOTON_PRIMARIO}`}>
                <UserPlus className="h-4 w-4" aria-hidden="true" /> {enviando ? "Creando tu cuenta…" : "Crear mi cuenta"}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
