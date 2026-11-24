import Link from "next/link";
import { MessagesSquare } from "lucide-react";
import EncabezadoAtencion from "@/components/atencion/EncabezadoAtencion";
import Alerta from "@/components/ui/Alerta";
import Badge from "@/components/ui/Badge";
import EmptyState from "@/components/ui/EmptyState";
import { listarConversaciones } from "@/lib/api/atencion";
import type { ConversacionResumen } from "@/lib/api/atencion-tipos";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

const CANAL: Record<string, string> = { simulador: "Prueba", whatsapp: "WhatsApp", instagram: "Instagram", facebook: "Facebook" };

export default async function AtencionConversaciones() {
  let lista: ConversacionResumen[] = [];
  let error: string | null = null;
  try {
    lista = await listarConversaciones();
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }
  return (
    <>
      <EncabezadoAtencion actual="/atencion/conversaciones" />
      {error && <Alerta>{error}</Alerta>}
      {!error && lista.length === 0 && (
        <EmptyState
          icono={MessagesSquare}
          titulo="Todavía no hay conversaciones"
          descripcion="Probá el asistente en el simulador. Cuando conectes WhatsApp, acá vas a ver las de tus clientes."
          accion={{ href: "/atencion/simulador", texto: "Probar el asistente" }}
        />
      )}
      {lista.length > 0 && (
        <ul className="divide-y divide-borde overflow-hidden rounded-2xl border border-borde bg-superficie">
          {lista.map((c) => (
            <li key={c.id}>
              <Link href={`/atencion/conversaciones/${c.id}`} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 hover:bg-superficie-2">
                <span>
                  <span className="font-medium text-texto">{c.nombre_contacto ?? c.contacto}</span>
                  <span className="block text-xs text-texto-3">
                    {c.ultimo_mensaje_en
                      ? new Date(c.ultimo_mensaje_en).toLocaleString("es-BO", { dateStyle: "short", timeStyle: "short" })
                      : "Sin mensajes"}
                  </span>
                </span>
                <span className="flex gap-1.5">
                  <Badge tono="gris">{CANAL[c.canal] ?? c.canal}</Badge>
                  {c.atendida_por === "humano" ? (
                    <Badge tono="ambar" punto>Necesita una persona</Badge>
                  ) : (
                    <Badge tono="azul">Asistente</Badge>
                  )}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
