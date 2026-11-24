"use client";

/**
 * "Continuar con Google" (Google Identity Services). Google nos da un ID
 * token firmado; lo mandamos al BFF (/api/auth/google), que lo verifica en el
 * backend y guarda la sesión en cookies HttpOnly. Si el usuario es nuevo, el
 * backend crea su negocio y lo deja como admin (docs/013-Seguridad/04, 3.1).
 */
import { useEffect, useRef, useState } from "react";
import { mensajeDeError, MENSAJE_SIN_CONEXION } from "@/lib/api/errores";

const CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
const SCRIPT_GIS = "https://accounts.google.com/gsi/client";

// Google pide inicializar una sola vez por página. El callback se lee de una
// referencia, así el último componente montado es el que recibe la respuesta.
let inicializado = false;
let callbackActual: ((r: RespuestaGoogle) => void) | null = null;

interface RespuestaGoogle {
  credential?: string;
}

interface GoogleId {
  initialize(opciones: {
    client_id: string;
    callback: (r: RespuestaGoogle) => void;
    ux_mode?: "popup";
    use_fedcm_for_prompt?: boolean;
  }): void;
  renderButton(elemento: HTMLElement, opciones: Record<string, unknown>): void;
}

declare global {
  interface Window {
    google?: { accounts: { id: GoogleId } };
  }
}

function cargarScript(): Promise<void> {
  if (window.google?.accounts?.id) return Promise.resolve();
  return new Promise((resolver, rechazar) => {
    const existente = document.querySelector<HTMLScriptElement>(`script[src="${SCRIPT_GIS}"]`);
    const script = existente ?? document.createElement("script");
    script.addEventListener("load", () => resolver());
    script.addEventListener("error", () => rechazar(new Error("No se pudo cargar Google.")));
    if (!existente) {
      script.src = SCRIPT_GIS;
      script.async = true;
      document.head.appendChild(script);
    }
  });
}

interface BotonGoogleProps {
  /** requiere2fa: falta el código de la verificación en dos pasos. */
  onSesion: (requiere2fa: boolean) => void;
}

export default function BotonGoogle({ onSesion }: BotonGoogleProps) {
  const contenedor = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [entrando, setEntrando] = useState(false);

  useEffect(() => {
    if (!CLIENT_ID) return;
    let cancelado = false;

    async function alResponder(respuesta: RespuestaGoogle) {
      if (!respuesta.credential) return;
      setError(null);
      setEntrando(true);
      try {
        const r = await fetch("/api/auth/google", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "same-origin",
          body: JSON.stringify({ id_token: respuesta.credential }),
        });
        if (!r.ok) {
          const cuerpo = await r.json().catch(() => ({}));
          throw new Error(
            r.status === 401
              ? "No pudimos validar tu cuenta de Google. Probá de nuevo."
              : mensajeDeError(r.status, cuerpo?.detail, r.headers.get("retry-after"))
          );
        }
        const cuerpo = await r.json().catch(() => ({}));
        onSesion(cuerpo?.requiere_2fa === true);
      } catch (e) {
        setError(e instanceof Error ? e.message : MENSAJE_SIN_CONEXION);
        setEntrando(false);
      }
    }

    cargarScript()
      .then(() => {
        if (cancelado || !contenedor.current || !window.google) return;
        callbackActual = alResponder;
        if (!inicializado) {
          window.google.accounts.id.initialize({
            client_id: CLIENT_ID,
            callback: (r) => callbackActual?.(r),
            ux_mode: "popup",
          });
          inicializado = true;
        }
        window.google.accounts.id.renderButton(contenedor.current, {
          theme: "filled_black",
          size: "large",
          shape: "pill",
          text: "continue_with",
          locale: "es",
          width: contenedor.current.offsetWidth || 320,
        });
      })
      .catch(() => {
        if (!cancelado) setError("No se pudo cargar el inicio de sesión con Google.");
      });

    return () => {
      cancelado = true;
    };
  }, [onSesion]);

  if (!CLIENT_ID) return null;

  return (
    <div className="mt-6">
      <div className="flex items-center gap-3 text-xs text-texto-3" aria-hidden="true">
        <span className="h-px flex-1 bg-borde" />o<span className="h-px flex-1 bg-borde" />
      </div>
      <div ref={contenedor} className="mt-4 flex min-h-11 w-full justify-center" />
      {entrando && <p className="mt-2 text-center text-sm text-texto-2">Entrando con Google…</p>}
      {error && (
        <p role="alert" className="mt-2 text-center text-sm text-rojo">
          {error}
        </p>
      )}
      <p className="mt-3 text-center text-xs text-texto-3">
        Si es tu primera vez, creamos tu cuenta y tu negocio automáticamente.
      </p>
    </div>
  );
}
