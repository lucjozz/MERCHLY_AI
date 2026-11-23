"use client";

/**
 * Onboarding pregunta por pregunta (docs/004-Backend/03, sección 3).
 * Una sola pregunta en pantalla, con animación al avanzar o volver, barra de
 * progreso, Enter para seguir y preguntas opcionales que se pueden saltear.
 */
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ArrowRight, Check, Loader2, Sparkles } from "lucide-react";
import { guardarPerfil } from "@/lib/api/acciones";
import type { Organizacion } from "@/lib/api/organizacion";
import { MERCADOS } from "@/lib/etiquetas";
import { BOTON_PRIMARIO, CAMPO } from "@/components/ui/estilos";

type Paso = "nombre" | "rubro" | "pais" | "moneda" | "cambio" | "presupuesto" | "costos" | "resumen";

const IDEAS_RUBRO = ["Ropa y accesorios", "Tecnología y celulares", "Hogar y cocina", "Belleza y cuidado personal", "Deportes y camping", "Mascotas"];

function numero(valor: string): number | null {
  const n = Number(valor.replace(",", "."));
  return valor.trim() === "" || !Number.isFinite(n) || n < 0 ? null : n;
}

export default function OnboardingPasoAPaso({
  organizacion,
  nombrePersona,
  dolarBcb,
}: {
  organizacion: Organizacion;
  nombrePersona: string;
  dolarBcb: number | null;
}) {
  const router = useRouter();
  const [paso, setPaso] = useState<Paso>("nombre");
  const [direccion, setDireccion] = useState<"adelante" | "atras">("adelante");
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [listo, setListo] = useState(false);

  const [nombre, setNombre] = useState(organizacion.nombre.startsWith("Negocio de ") ? "" : organizacion.nombre);
  const [rubro, setRubro] = useState(organizacion.rubro ?? "");
  const [pais, setPais] = useState(organizacion.pais || "BO");
  const [moneda, setMoneda] = useState<"BOB" | "USD">(organizacion.moneda);
  const [tipoCambio, setTipoCambio] = useState(organizacion.tipo_cambio?.toString() ?? "");
  // Por defecto, el dólar oficial del BCB (se actualiza solo). "propio" = el que paga el negocio.
  const [modoCambio, setModoCambio] = useState<"bcb" | "propio">(organizacion.tipo_cambio || !dolarBcb ? "propio" : "bcb");
  const [presupuesto, setPresupuesto] = useState(organizacion.presupuesto_mensual?.toString() ?? "");
  const [envio, setEnvio] = useState(organizacion.costo_envio_unitario_usd ? String(organizacion.costo_envio_unitario_usd) : "");
  const [impuestos, setImpuestos] = useState(organizacion.impuestos_importacion_pct ? String(organizacion.impuestos_importacion_pct) : "");

  // El paso del tipo de cambio solo aparece si eligió bolivianos.
  const pasos: Paso[] = ["nombre", "rubro", "pais", "moneda", ...(moneda === "BOB" ? (["cambio"] as Paso[]) : []), "presupuesto", "costos", "resumen"];
  const indice = pasos.indexOf(paso);
  const progreso = Math.round(((indice + 1) / pasos.length) * 100);

  const campo = useRef<HTMLInputElement>(null);
  const formulario = useRef<HTMLFormElement>(null);
  useEffect(() => {
    // En preguntas sin campo de texto, el foco va al formulario para que Enter funcione.
    (campo.current ?? formulario.current)?.focus();
  }, [paso]);

  // Se precarga la página siguiente mientras responde, así al terminar entra al instante.
  useEffect(() => {
    router.prefetch("/productos");
  }, [router]);

  function validar(): string | null {
    if (paso === "nombre" && nombre.trim().length < 2) return "Escribí el nombre de tu negocio.";
    if (paso === "rubro" && rubro.trim().length < 2) return "Contanos qué vendés (o elegí una opción).";
    if (paso === "cambio" && modoCambio === "propio" && !numero(tipoCambio))
      return "Escribí cuántos bolivianos pagás por 1 dólar, o usá el oficial del BCB.";
    if (paso === "presupuesto" && presupuesto.trim() && numero(presupuesto) === null) return "Escribí un número o salteá esta pregunta.";
    if (paso === "costos" && ((envio.trim() && numero(envio) === null) || (impuestos.trim() && (numero(impuestos) === null || (numero(impuestos) ?? 0) > 100))))
      return "Revisá los números (los impuestos van de 0 a 100) o salteá esta pregunta.";
    return null;
  }

  function siguiente() {
    const problema = validar();
    if (problema) {
      setError(problema);
      return;
    }
    setError(null);
    setDireccion("adelante");
    setPaso(pasos[Math.min(indice + 1, pasos.length - 1)]);
  }

  /** Opciones de un toque (país, moneda): eligen y avanzan solas. */
  function elegirYAvanzar(aplicar: () => void, proximo?: Paso) {
    aplicar();
    setError(null);
    setDireccion("adelante");
    setTimeout(() => setPaso((actual) => proximo ?? pasos[pasos.indexOf(actual) + 1]), 180);
  }

  function anterior() {
    setError(null);
    setDireccion("atras");
    setPaso(pasos[Math.max(indice - 1, 0)]);
  }

  function saltear() {
    if (paso === "presupuesto") setPresupuesto("");
    if (paso === "costos") {
      setEnvio("");
      setImpuestos("");
    }
    setError(null);
    setDireccion("adelante");
    setPaso(pasos[indice + 1]);
  }

  async function terminar() {
    setGuardando(true);
    setError(null);
    try {
      await guardarPerfil({
        nombre: nombre.trim(),
        pais,
        rubro: rubro.trim(),
        presupuesto_mensual: numero(presupuesto),
        moneda,
        tipo_cambio: moneda === "BOB" && modoCambio === "propio" ? numero(tipoCambio) : null,
        costo_envio_unitario_usd: numero(envio) ?? 0,
        impuestos_importacion_pct: numero(impuestos) ?? 0,
      });
      setListo(true);
      router.replace("/productos");
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo guardar.");
      setGuardando(false);
    }
  }

  function alEnviar(e: React.FormEvent) {
    e.preventDefault();
    if (paso === "resumen") terminar();
    else siguiente();
  }

  const opcional = paso === "presupuesto" || paso === "costos";
  const titulo = "text-2xl font-bold leading-tight text-texto sm:text-3xl";
  const ayuda = "mt-2 text-sm text-texto-2 sm:text-base";
  const opcion = (activa: boolean) =>
    `rounded-xl border px-4 py-3 text-left text-sm transition-all ${
      activa ? "border-acento bg-acento-hondo/40 text-texto ring-2 ring-acento/40" : "border-borde bg-fondo text-texto-2 hover:border-borde-fuerte hover:text-texto"
    }`;

  if (listo) {
    return (
      <div className="mx-auto flex min-h-[70vh] max-w-xl flex-col items-center justify-center py-8 text-center animate-aparecer" role="status">
        <Loader2 className="h-8 w-8 animate-spin text-acento-claro" aria-hidden="true" />
        <p className="mt-4 text-xl font-semibold text-texto">Preparando tu panel…</p>
        <p className="mt-1 text-sm text-texto-2">Ya guardamos los datos de {nombre.trim()}.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-xl flex-col justify-center py-8">
      <div className="mb-8">
        <div className="mb-2 flex items-center justify-between text-xs text-texto-3">
          <span className="flex items-center gap-1.5">
            <Sparkles className="h-3.5 w-3.5 text-acento-claro" aria-hidden="true" />
            Configurando tu negocio
          </span>
          <span>
            {indice + 1} de {pasos.length}
          </span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-superficie" role="progressbar" aria-valuenow={progreso} aria-valuemin={0} aria-valuemax={100} aria-label="Progreso">
          <div className="h-1.5 rounded-full bg-gradient-to-r from-acento to-acento-claro transition-all duration-500" style={{ width: `${progreso}%` }} />
        </div>
      </div>

      <form ref={formulario} tabIndex={-1} onSubmit={alEnviar} noValidate className="outline-none">
        {/* key = paso: cada pregunta se monta de nuevo y vuelve a animarse */}
        <div key={paso} className={direccion === "adelante" ? "animate-entrar-adelante" : "animate-entrar-atras"}>
          {paso === "nombre" && (
            <>
              <h1 className={titulo}>¡Hola{nombrePersona ? `, ${nombrePersona}` : ""}! ¿Cómo se llama tu negocio?</h1>
              <p className={ayuda}>Así lo vas a ver en MERCHLY y en tus campañas.</p>
              <input ref={campo} value={nombre} maxLength={120} onChange={(e) => setNombre(e.target.value)} placeholder="Ej.: Tienda Lucía" aria-label="Nombre del negocio" className={`${CAMPO} mt-6 py-3 text-lg`} />
            </>
          )}

          {paso === "rubro" && (
            <>
              <h1 className={titulo}>¿Qué vendés o querés vender?</h1>
              <p className={ayuda}>La IA va a buscar productos pensando en esto.</p>
              <input ref={campo} value={rubro} maxLength={120} onChange={(e) => setRubro(e.target.value)} placeholder="Ej.: accesorios para celulares" aria-label="Rubro" className={`${CAMPO} mt-6 py-3 text-lg`} />
              <div className="mt-4 flex flex-wrap gap-2">
                {IDEAS_RUBRO.map((idea) => (
                  <button key={idea} type="button" onClick={() => setRubro(idea)} className={`${opcion(rubro === idea)} !px-3 !py-1.5 !text-xs`}>
                    {idea}
                  </button>
                ))}
              </div>
            </>
          )}

          {paso === "pais" && (
            <>
              <h1 className={titulo}>¿En qué país vendés?</h1>
              <p className={ayuda}>Buscamos productos con demanda en tu mercado.</p>
              <div className="mt-6 grid grid-cols-2 gap-3">
                {Object.entries(MERCADOS).map(([codigo, m]) => (
                  <button key={codigo} type="button" onClick={() => elegirYAvanzar(() => setPais(codigo))} className={opcion(pais === codigo)} aria-pressed={pais === codigo}>
                    <span className="font-medium">{m.nombre}</span>
                  </button>
                ))}
              </div>
            </>
          )}

          {paso === "moneda" && (
            <>
              <h1 className={titulo}>¿En qué moneda querés ver los precios?</h1>
              <p className={ayuda}>La IA calcula en dólares; nosotros te lo mostramos en tu moneda.</p>
              <div className="mt-6 grid gap-3 sm:grid-cols-2">
                {([
                  ["BOB", "Bolivianos", "Bs 139,20"],
                  ["USD", "Dólares", "US$ 20,00"],
                ] as const).map(([valor, nombreMoneda, ejemplo]) => (
                  <button
                    key={valor}
                    type="button"
                    // Con dólares no hay pregunta de tipo de cambio: se salta directo al presupuesto.
                    onClick={() => elegirYAvanzar(() => setMoneda(valor), valor === "BOB" ? "cambio" : "presupuesto")}
                    className={`${opcion(moneda === valor)} !py-4`}
                    aria-pressed={moneda === valor}
                  >
                    <span className="block text-base font-semibold">{nombreMoneda}</span>
                    <span className="text-xs text-texto-3">Ej.: {ejemplo}</span>
                  </button>
                ))}
              </div>
            </>
          )}

          {paso === "cambio" && (
            <>
              <h1 className={titulo}>¿Qué dólar usamos para tus precios?</h1>
              <p className={ayuda}>El dólar sube y baja: podés usar el oficial del Banco Central (se actualiza solo) o el que pagás vos.</p>
              <div className="mt-6 grid gap-3">
                {dolarBcb && (
                  <button type="button" onClick={() => elegirYAvanzar(() => setModoCambio("bcb"), "presupuesto")} className={`${opcion(modoCambio === "bcb")} !py-4`} aria-pressed={modoCambio === "bcb"}>
                    <span className="block text-base font-semibold">Oficial del BCB · hoy Bs {dolarBcb.toLocaleString("es-BO")}</span>
                    <span className="text-xs text-texto-3">Se actualiza automáticamente todos los días.</span>
                  </button>
                )}
                <button type="button" onClick={() => setModoCambio("propio")} className={`${opcion(modoCambio === "propio")} !py-4`} aria-pressed={modoCambio === "propio"}>
                  <span className="block text-base font-semibold">El que pago yo</span>
                  <span className="text-xs text-texto-3">Si comprás dólares a otro precio, así tu margen da real.</span>
                </button>
              </div>
              {modoCambio === "propio" && (
                <div className="relative mt-4 animate-aparecer">
                  <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-texto-2">Bs</span>
                  <input ref={campo} inputMode="decimal" value={tipoCambio} onChange={(e) => setTipoCambio(e.target.value)} placeholder={dolarBcb ? String(dolarBcb).replace(".", ",") : "Ej.: 11,75"} aria-label="Tipo de cambio propio" className={`${CAMPO} py-3 pl-12 text-lg`} autoFocus />
                </div>
              )}
            </>
          )}

          {paso === "presupuesto" && (
            <>
              <h1 className={titulo}>¿Cuánto podés invertir por mes en mercadería?</h1>
              <p className={ayuda}>Opcional. Ayuda a que la IA no te sugiera cosas fuera de tu alcance.</p>
              <div className="relative mt-6">
                <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-texto-2">{moneda === "BOB" ? "Bs" : "US$"}</span>
                <input ref={campo} inputMode="decimal" value={presupuesto} onChange={(e) => setPresupuesto(e.target.value)} placeholder="Ej.: 5000" aria-label="Presupuesto mensual" className={`${CAMPO} py-3 pl-14 text-lg`} />
              </div>
            </>
          )}

          {paso === "costos" && (
            <>
              <h1 className={titulo}>¿Cuánto te cuesta traer cada producto?</h1>
              <p className={ayuda}>Opcional. Lo usamos para calcular tu ganancia real. Si no sabés, salteala.</p>
              <div className="mt-6 grid gap-3 sm:grid-cols-2">
                <label className="block text-sm text-texto-2">
                  Envío por unidad (US$)
                  <input ref={campo} inputMode="decimal" value={envio} onChange={(e) => setEnvio(e.target.value)} placeholder="Ej.: 2" className={`${CAMPO} mt-2 py-3 text-lg`} />
                </label>
                <label className="block text-sm text-texto-2">
                  Impuestos de importación (%)
                  <input inputMode="decimal" value={impuestos} onChange={(e) => setImpuestos(e.target.value)} placeholder="Ej.: 15" className={`${CAMPO} mt-2 py-3 text-lg`} />
                </label>
              </div>
            </>
          )}

          {paso === "resumen" && (
            <>
              <h1 className={titulo}>¡Listo! ¿Está todo bien?</h1>
              <p className={ayuda}>Podés cambiarlo cuando quieras en Configuración.</p>
              <dl className="mt-6 divide-y divide-borde rounded-2xl border border-borde bg-superficie text-sm">
                {[
                  ["Negocio", nombre],
                  ["Vendés", rubro],
                  ["País", MERCADOS[pais]?.nombre ?? pais],
                  ["Moneda", moneda === "BOB" ? (modoCambio === "bcb" ? "Bolivianos · dólar oficial del BCB" : `Bolivianos (Bs ${tipoCambio} por US$ 1)`) : "Dólares"],
                  ["Presupuesto mensual", presupuesto ? `${moneda === "BOB" ? "Bs" : "US$"} ${presupuesto}` : "Sin definir"],
                  ["Envío / impuestos", envio || impuestos ? `US$ ${envio || 0} · ${impuestos || 0}%` : "Sin definir"],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-4 px-4 py-3">
                    <dt className="text-texto-2">{k}</dt>
                    <dd className="text-right font-medium text-texto">{v}</dd>
                  </div>
                ))}
              </dl>
            </>
          )}
        </div>

        {error && (
          <p role="alert" className="mt-4 rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo animate-aparecer">
            {error}
          </p>
        )}

        <div className="mt-8 flex items-center justify-between gap-3">
          {indice > 0 ? (
            <button type="button" onClick={anterior} className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2.5 text-sm text-texto-2 hover:text-texto">
              <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Atrás
            </button>
          ) : (
            <span />
          )}
          <div className="flex items-center gap-2">
            {opcional && (
              <button type="button" onClick={saltear} className="rounded-lg px-3 py-2.5 text-sm text-texto-2 hover:text-texto">
                Saltear
              </button>
            )}
            <button type="submit" disabled={guardando} className={`px-6 py-3 ${BOTON_PRIMARIO}`}>
              {paso === "resumen" ? (
                guardando ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Guardando…
                  </>
                ) : (
                  <>
                    <Check className="h-4 w-4" aria-hidden="true" /> Empezar
                  </>
                )
              ) : (
                <>
                  Siguiente <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </>
              )}
            </button>
          </div>
        </div>
        {paso !== "resumen" && <p className="mt-3 text-right text-xs text-texto-3">o apretá Enter ↵</p>}
      </form>
    </div>
  );
}
