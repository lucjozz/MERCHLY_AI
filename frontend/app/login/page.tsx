"use client";

import { Suspense, useCallback, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  Sparkles,
  Loader2,
  Search,
  FileSearch,
  Scale,
  Megaphone,
  ShieldCheck,
} from "lucide-react";
import { iniciarSesion, verificarCodigo } from "@/lib/api/auth";
import { rutaInternaSegura } from "@/lib/sesion/config";
import { BOTON_PRIMARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";
import BotonGoogle from "@/components/BotonGoogle";

const PASOS = [
  {
    icono: Search,
    titulo: "Buscá productos con IA",
    texto: "Escribí una categoría y la IA te sugiere qué vender en tu país.",
  },
  {
    icono: FileSearch,
    titulo: "Revisá la evidencia",
    texto: "Demanda, competencia, precios y riesgos, todo en un solo lugar.",
  },
  {
    icono: Scale,
    titulo: "Decidí vos",
    texto: "Aprobás o descartás. La IA nunca aprueba nada por su cuenta.",
  },
  {
    icono: Megaphone,
    titulo: "Generá la campaña",
    texto: "Ideas y textos para redes, email y anuncios, listos para usar.",
  },
];

function Login() {
  const router = useRouter();
  const parametros = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pideCodigo, setPideCodigo] = useState(false);
  const [codigo, setCodigo] = useState("");

  // Solo rutas internas: evita usar el login para redirigir a otro sitio.
  const irAlDestino = useCallback(() => {
    router.push(rutaInternaSegura(parametros.get("siguiente")));
    router.refresh();
  }, [router, parametros]);

  async function entrar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setCargando(true);

    try {
      if (pideCodigo) {
        await verificarCodigo(codigo.trim());
        irAlDestino();
        return;
      }
      if (await iniciarSesion(email.trim(), password)) {
        setPideCodigo(true);
        setPassword("");
        setCargando(false);
        return;
      }
      irAlDestino();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo iniciar sesión."
      );
      setCargando(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-fondo">
      {/* Halo de color sutil derivado del acento. */}
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(61,125,216,0.18),transparent_55%),radial-gradient(ellipse_at_bottom_right,rgba(232,184,75,0.08),transparent_50%)]"
      />

      <div className="relative mx-auto grid min-h-full max-w-6xl items-center gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.1fr_1fr] lg:gap-16 lg:px-10">
        {/* Propuesta de valor */}
        <section className="animate-aparecer" aria-labelledby="titulo-propuesta">
          <div className="mb-8 flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-acento to-acento-hondo shadow-lg shadow-acento/25">
              <Sparkles className="h-5 w-5 text-white" aria-hidden="true" />
            </span>
            <div>
              <p className="text-lg font-bold leading-tight text-texto">MERCHLY AI</p>
              <p className="text-[11px] font-medium tracking-widest text-texto-2">
                AI COMMERCE OS
              </p>
            </div>
          </div>

          <h1
            id="titulo-propuesta"
            className="text-3xl font-bold leading-tight tracking-tight text-texto sm:text-4xl lg:text-5xl"
          >
            Descubrí qué vender.{" "}
            <span className="bg-gradient-to-r from-acento-claro to-ambar bg-clip-text text-transparent">
              Vos decidís.
            </span>
          </h1>
          <p className="mt-4 max-w-lg text-base leading-relaxed text-texto-2">
            Un equipo de agentes de IA investiga productos y arma campañas para
            tu tienda online. Vos tenés siempre la última palabra.
          </p>

          <ol className="mt-8 hidden gap-3 sm:grid sm:grid-cols-2">
            {PASOS.map((paso, i) => {
              const Icono = paso.icono;
              return (
                <li
                  key={paso.titulo}
                  className="rounded-2xl border border-borde bg-superficie/70 p-4 animate-aparecer"
                  style={{ animationDelay: `${120 + i * 80}ms` }}
                >
                  <div className="flex items-center gap-2.5">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-acento-hondo text-acento-claro">
                      <Icono className="h-4 w-4" aria-hidden="true" />
                    </span>
                    <span className="text-xs font-semibold text-texto-2">Paso {i + 1}</span>
                  </div>
                  <p className="mt-3 text-sm font-semibold text-texto">{paso.titulo}</p>
                  <p className="mt-1 text-sm leading-relaxed text-texto-2">{paso.texto}</p>
                </li>
              );
            })}
          </ol>

          <p className="mt-6 flex items-center gap-2 text-sm text-texto-2">
            <ShieldCheck className="h-4 w-4 text-verde" aria-hidden="true" />
            Cada decisión queda registrada con su motivo.
          </p>
        </section>

        {/* Formulario (misma lógica de siempre) */}
        <div className="animate-aparecer [animation-delay:150ms]">
          <form
            onSubmit={entrar}
            className="mx-auto w-full max-w-md rounded-3xl border border-borde bg-superficie/90 p-6 shadow-2xl shadow-black/40 backdrop-blur sm:p-8"
          >
            <h2 className="text-xl font-bold text-texto">{pideCodigo ? "Verificación en dos pasos" : "Entrá a tu cuenta"}</h2>
            <p className="mt-1 text-sm text-texto-2">
              {pideCodigo
                ? "Abrí la app de autenticación de tu celular y escribí el código de 6 dígitos de MERCHLY AI. Si no tenés el celular, usá un código de respaldo."
                : "Usá el email y la contraseña que te dio tu administrador."}
            </p>

            {pideCodigo && (
              <div className="mt-7">
                <label htmlFor="codigo" className={ETIQUETA_CAMPO}>Código</label>
                <input
                  id="codigo"
                  value={codigo}
                  onChange={(e) => setCodigo(e.target.value)}
                  autoComplete="one-time-code"
                  inputMode="text"
                  maxLength={12}
                  placeholder="123456"
                  required
                  autoFocus
                  className={`${CAMPO} text-center text-lg tracking-[0.3em]`}
                />
                <button type="button" onClick={() => { setPideCodigo(false); setCodigo(""); setError(null); }} className="mt-2 text-xs text-acento-claro hover:underline">
                  Volver a ingresar la contraseña
                </button>
              </div>
            )}

            <div className={pideCodigo ? "hidden" : ""}>

            <div className="mt-7">
              <label htmlFor="email" className={ETIQUETA_CAMPO}>
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="username"
                placeholder="vos@tutienda.com"
                required={!pideCodigo}
                className={CAMPO}
              />
            </div>

            <div className="mt-5">
              <label htmlFor="password" className={ETIQUETA_CAMPO}>
                Contraseña
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required={!pideCodigo}
                className={CAMPO}
              />
              <div className="mt-2 text-right">
                <a href="/olvide" className="text-xs text-acento-claro hover:underline">
                  ¿Olvidaste tu contraseña?
                </a>
              </div>
            </div>
            </div>

            {error && (
              <p
                role="alert"
                className="mt-5 rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo"
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={cargando}
              className={`mt-6 w-full py-3 ${BOTON_PRIMARIO}`}
            >
              {cargando && (
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              )}
              {cargando ? "Entrando..." : pideCodigo ? "Verificar" : "Entrar"}
            </button>

            {/* El botón de Google no envía este formulario: abre su propia ventana. */}
            {!pideCodigo && (
              <BotonGoogle onSesion={(requiere2fa) => (requiere2fa ? setPideCodigo(true) : irAlDestino())} />
            )}
          </form>
        </div>
      </div>
    </div>
  );
}

// useSearchParams (para volver a la página de origen) necesita Suspense.
export default function PaginaLogin() {
  return (
    <Suspense fallback={null}>
      <Login />
    </Suspense>
  );
}
