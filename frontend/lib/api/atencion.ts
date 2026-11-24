/** Lecturas del Agente de Atención desde Server Components (docs/007-Agentes/09). */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";
import type {
  AtencionConfig,
  ConversacionDetalle,
  ConversacionResumen,
  Notificacion,
  Pedido,
  QrPago,
  ZonaEnvio,
} from "@/lib/api/atencion-tipos";

async function leer<T>(ruta: string): Promise<T> {
  const r = await fetchAutenticadoServidor(ruta);
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}

export const obtenerConfigAtencion = () => leer<AtencionConfig>("/atencion/config");
export const listarQr = () => leer<QrPago[]>("/atencion/qr");
export const listarZonas = () => leer<ZonaEnvio[]>("/atencion/zonas");
export const listarConversaciones = () => leer<ConversacionResumen[]>("/atencion/conversaciones");
export const obtenerConversacion = (id: string) => leer<ConversacionDetalle>(`/atencion/conversaciones/${id}`);
export const listarPedidos = () => leer<Pedido[]>("/atencion/pedidos");
export const listarNotificaciones = () => leer<{ notificaciones: Notificacion[]; sin_leer: number }>("/atencion/notificaciones");
