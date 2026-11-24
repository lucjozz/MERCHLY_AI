"use client";

/**
 * Simulador: escribís como si fueras un comprador y el asistente responde de verdad
 * con tu catálogo, tus zonas y tu QR. Los pedidos que se armen acá quedan marcados como simulados.
 */
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Loader2, RotateCcw, Send } from "lucide-react";
import BurbujaMensaje from "@/components/atencion/BurbujaMensaje";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO, CAMPO } from "@/components/ui/estilos";
import type { Mensaje } from "@/lib/api/atencion-tipos";
import { enviarAlSimulador } from "@/lib/api/atencion-acciones";

const EJEMPLOS = ["Hola", "¿Qué venden?", "¿Tenés taladro de 800 W?", "Lo quiero, con envío a Equipetrol", "Ya pagué", "¿Me hacés un descuento?"];

export default function ChatSimulador({ proveedor }: { proveedor: string }) {
  const [mensajes, setMensajes] = useState<Mensaje[]>([]);
  const [conversacionId, setConversacionId] = useState<string | null>(null);
  const [texto, setTexto] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [atendidaPor, setAtendidaPor] = useState<"agente" | "humano">("agente");
  const fin = useRef<HTMLLIElement>(null);

  // Con llaves: en Chrome reciente scrollIntoView devuelve una Promise, y si el efecto
  // la devuelve React la toma como función de limpieza y la pantalla se rompe.
  useEffect(() => {
    fin.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [mensajes]);

  async function enviar(valor: string) {
    const limpio = valor.trim();
    if (!limpio || enviando) return;
    setError(null);
    setEnviando(true);
    setTexto("");
    try {
      const r = await enviarAlSimulador(limpio, conversacionId);
      setConversacionId(r.conversacion_id);
      setAtendidaPor(r.atendida_por);
      setMensajes((m) => [...m, ...r.mensajes]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo enviar el mensaje.");
      setTexto(limpio);
    } finally {
      setEnviando(false);
    }
  }

  function reiniciar() {
    setMensajes([]);
    setConversacionId(null);
    setAtendidaPor("agente");
    setError(null);
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
      <section aria-label="Chat de prueba" className="flex h-[min(70vh,640px)] flex-col rounded-2xl border border-borde bg-superficie">
        <ul className="flex-1 space-y-3 overflow-y-auto p-4" aria-live="polite">
          {mensajes.length === 0 && (
            <li className="py-10 text-center text-sm text-texto-2">Escribí como si fueras un cliente. Probá con los ejemplos de la derecha.</li>
          )}
          {mensajes.map((m) => <BurbujaMensaje key={m.id} mensaje={m} />)}
          {enviando && (
            <li className="flex justify-end text-xs text-texto-2">
              <span className="inline-flex items-center gap-1.5"><Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" /> El asistente está escribiendo…</span>
            </li>
          )}
          <li ref={fin} aria-hidden="true" />
        </ul>
        {atendidaPor === "humano" && (
          <p className="border-t border-borde bg-ambar-fondo px-4 py-2 text-xs text-ambar">
            El asistente pasó esta conversación a una persona: ya no responde solo.{" "}
            {conversacionId && <Link href={`/atencion/conversaciones/${conversacionId}`} className="underline">Atenderla</Link>}
          </p>
        )}
        {error && <p role="alert" className="border-t border-borde px-4 py-2 text-sm text-rojo">{error}</p>}
        <form onSubmit={(e) => { e.preventDefault(); enviar(texto); }} className="flex gap-2 border-t border-borde p-3">
          <label htmlFor="sim-texto" className="sr-only">Mensaje del comprador</label>
          <input id="sim-texto" value={texto} onChange={(e) => setTexto(e.target.value)} maxLength={1000} placeholder="Escribí como un cliente…" className={CAMPO} disabled={enviando} autoComplete="off" />
          <button type="submit" className={BOTON_PRIMARIO} disabled={enviando || !texto.trim()} aria-label="Enviar">
            <Send className="h-4 w-4" aria-hidden="true" />
          </button>
        </form>
      </section>

      <aside className="space-y-4">
        <div className="rounded-2xl border border-borde bg-superficie p-4 text-sm">
          <p className="font-semibold text-texto">Probá con</p>
          <ul className="mt-3 flex flex-wrap gap-1.5">
            {EJEMPLOS.map((e) => (
              <li key={e}>
                <button type="button" onClick={() => enviar(e)} disabled={enviando} className="rounded-full border border-borde-fuerte px-2.5 py-1 text-xs text-texto hover:border-acento-borde hover:text-acento-claro disabled:opacity-50">
                  {e}
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-2xl border border-borde bg-superficie p-4 text-xs leading-relaxed text-texto-2">
          <p>
            {proveedor === "openai"
              ? "Responde la IA real con tu catálogo público."
              : "Modo simulado: todavía no hay clave de IA cargada, así que responde con reglas simples. Los precios, el stock, los envíos y el QR son los reales de tu negocio."}
          </p>
          <p className="mt-2">Los pedidos que armes acá quedan marcados como <strong className="text-texto">simulados</strong> en Pedidos.</p>
        </div>
        <button type="button" onClick={reiniciar} className={`${BOTON_SECUNDARIO} w-full`}>
          <RotateCcw className="h-4 w-4" aria-hidden="true" /> Empezar otra conversación
        </button>
      </aside>
    </div>
  );
}
