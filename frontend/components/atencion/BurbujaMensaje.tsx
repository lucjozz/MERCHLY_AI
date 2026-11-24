/** Un mensaje de la conversación, con sus adjuntos (QR, foto del producto). */
import { Bot, ShieldCheck, Store, User } from "lucide-react";
import { urlQr, type Mensaje } from "@/lib/api/atencion-tipos";
import { urlFoto } from "@/lib/api/inventario-url";

const ESTILO = {
  comprador: { lado: "justify-start", burbuja: "bg-superficie-2 text-texto", icono: User, nombre: "Comprador" },
  agente: { lado: "justify-end", burbuja: "bg-acento-hondo text-texto", icono: Bot, nombre: "Asistente" },
  vendedor: { lado: "justify-end", burbuja: "bg-verde-fondo text-texto", icono: Store, nombre: "Vos" },
  sistema: { lado: "justify-center", burbuja: "bg-fondo text-texto-2 border border-borde", icono: ShieldCheck, nombre: "Aviso" },
} as const;

export default function BurbujaMensaje({ mensaje }: { mensaje: Mensaje }) {
  const e = ESTILO[mensaje.rol];
  const Icono = e.icono;
  const hora = new Date(mensaje.creado_en).toLocaleTimeString("es-BO", { hour: "2-digit", minute: "2-digit" });
  return (
    <li className={`flex ${e.lado}`}>
      <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${e.burbuja}`}>
        <p className="mb-1 flex items-center gap-1.5 text-xs text-texto-2">
          <Icono className="h-3.5 w-3.5" aria-hidden="true" />
          {e.nombre} · {hora}
          {mensaje.simulado && mensaje.rol === "agente" && <span className="text-texto-3">· simulado</span>}
        </p>
        <p className="whitespace-pre-wrap leading-relaxed">{mensaje.texto}</p>
        {mensaje.adjuntos.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {mensaje.adjuntos.map((a, i) =>
              a.tipo === "qr" && a.qr_id ? (
                // eslint-disable-next-line @next/next/no-img-element -- imagen privada servida por el BFF con sesión
                <img key={i} src={urlQr(a.qr_id)} alt="QR de pago" className="h-40 w-40 rounded-lg bg-white object-contain p-1" />
              ) : a.tipo === "producto" && a.foto_id ? (
                // eslint-disable-next-line @next/next/no-img-element -- imagen privada servida por el BFF con sesión
                <img key={i} src={urlFoto(a.foto_id)} alt="Foto del producto" className="h-24 w-24 rounded-lg object-cover" />
              ) : null
            )}
          </div>
        )}
      </div>
    </li>
  );
}
