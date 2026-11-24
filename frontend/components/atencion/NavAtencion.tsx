/** Pestañas del Agente de Atención al Cliente. */
import Link from "next/link";
import { Bell, MessageSquare, MessagesSquare, Settings } from "lucide-react";

const PESTANAS = [
  { href: "/atencion", texto: "Pedidos y avisos", icono: Bell },
  { href: "/atencion/simulador", texto: "Probar el asistente", icono: MessageSquare },
  { href: "/atencion/conversaciones", texto: "Conversaciones", icono: MessagesSquare },
  { href: "/atencion/configuracion", texto: "Configuración", icono: Settings },
];

export default function NavAtencion({ actual, sinLeer = 0 }: { actual: string; sinLeer?: number }) {
  return (
    <nav aria-label="Secciones de atención al cliente" className="mb-6 flex flex-wrap gap-1 rounded-xl border border-borde bg-superficie p-1">
      {PESTANAS.map(({ href, texto, icono: Icono }) => {
        const activa = actual === href;
        return (
          <Link
            key={href}
            href={href}
            aria-current={activa ? "page" : undefined}
            className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              activa ? "bg-superficie-2 text-texto" : "text-texto-2 hover:text-texto"
            }`}
          >
            <Icono className="h-4 w-4" aria-hidden="true" />
            {texto}
            {href === "/atencion" && sinLeer > 0 && (
              <span className="rounded-full bg-ambar px-1.5 text-xs font-semibold text-fondo">{sinLeer}</span>
            )}
          </Link>
        );
      })}
    </nav>
  );
}
