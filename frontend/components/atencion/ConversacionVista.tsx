"use client";

/** Una conversación: la persona puede tomarla (el asistente se calla), responder y devolvérsela al asistente. */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Bot, Hand, Loader2, Send } from "lucide-react";
import BurbujaMensaje from "@/components/atencion/BurbujaMensaje";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO, CAMPO } from "@/components/ui/estilos";
import type { ConversacionDetalle } from "@/lib/api/atencion-tipos";
import { cambiarAtencion, responderComoVendedor } from "@/lib/api/atencion-acciones";

export default function ConversacionVista({ conversacion }: { conversacion: ConversacionDetalle }) {
  const router = useRouter();
  const [texto, setTexto] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const humano = conversacion.atendida_por === "humano";

  async function hacer(accion: () => Promise<unknown>) {
    setError(null);
    setOcupado(true);
    try {
      await accion();
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo completar la acción.");
    } finally {
      setOcupado(false);
    }
  }

  return (
    <section className="rounded-2xl border border-borde bg-superficie">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-borde px-4 py-3">
        <p className="text-sm text-texto-2">
          {humano ? "La estás atendiendo vos: el asistente no responde." : "La está atendiendo el asistente."}
        </p>
        <button
          type="button"
          disabled={ocupado}
          onClick={() => hacer(() => cambiarAtencion(conversacion.id, humano ? "agente" : "humano"))}
          className={BOTON_SECUNDARIO}
        >
          {humano ? <Bot className="h-4 w-4" aria-hidden="true" /> : <Hand className="h-4 w-4" aria-hidden="true" />}
          {humano ? "Devolver al asistente" : "Tomar la conversación"}
        </button>
      </div>
      <ul className="max-h-[60vh] space-y-3 overflow-y-auto p-4">
        {conversacion.mensajes.map((m) => <BurbujaMensaje key={m.id} mensaje={m} />)}
      </ul>
      {error && <p role="alert" className="border-t border-borde px-4 py-2 text-sm text-rojo">{error}</p>}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const limpio = texto.trim();
          if (limpio) hacer(async () => { await responderComoVendedor(conversacion.id, limpio); setTexto(""); });
        }}
        className="flex gap-2 border-t border-borde p-3"
      >
        <label htmlFor="v-texto" className="sr-only">Tu respuesta</label>
        <input id="v-texto" value={texto} onChange={(e) => setTexto(e.target.value)} maxLength={2000} placeholder="Escribile al cliente…" className={CAMPO} disabled={ocupado} />
        <button type="submit" disabled={ocupado || !texto.trim()} className={BOTON_PRIMARIO} aria-label="Enviar">
          {ocupado ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Send className="h-4 w-4" aria-hidden="true" />}
        </button>
      </form>
      {conversacion.canal === "simulador" && (
        <p className="border-t border-borde px-4 py-2 text-xs text-texto-3">Conversación de prueba: tus respuestas no se mandan a nadie.</p>
      )}
    </section>
  );
}
