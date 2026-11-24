/** Acciones del Agente de Atención desde componentes cliente (vía BFF). */
import { fetchJson } from "@/lib/api/cliente";
import type { AtencionConfig, ConversacionResumen, Mensaje, Pedido, QrPago, ZonaEnvio } from "@/lib/api/atencion-tipos";

const J = { "Content-Type": "application/json" };
const post = <T>(ruta: string, cuerpo?: unknown) =>
  fetchJson<T>(ruta, { method: "POST", headers: J, body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo) });

export interface RespuestaSimulador {
  conversacion_id: string;
  atendida_por: "agente" | "humano";
  proveedor: string;
  mensajes: Mensaje[];
}

export const enviarAlSimulador = (texto: string, conversacionId: string | null) =>
  post<RespuestaSimulador>("/atencion/simulador", { texto, conversacion_id: conversacionId });

export const responderComoVendedor = (conversacionId: string, texto: string) =>
  post<Mensaje>(`/atencion/conversaciones/${conversacionId}/mensajes`, { texto });

export const cambiarAtencion = (conversacionId: string, atendidaPor: "agente" | "humano") =>
  fetchJson<ConversacionResumen>(`/atencion/conversaciones/${conversacionId}`, {
    method: "PATCH", headers: J, body: JSON.stringify({ atendida_por: atendidaPor }),
  });

export const decidirPedido = (pedidoId: string, accion: "confirmar-pago" | "rechazar-pago" | "entregado" | "cancelar") =>
  post<Pedido>(`/atencion/pedidos/${pedidoId}/${accion}`);

export const marcarAvisosLeidos = () => post<void>("/atencion/notificaciones/leer");

export const guardarConfigAtencion = (datos: Omit<AtencionConfig, "proveedor" | "plan_incluye">) =>
  fetchJson<AtencionConfig>("/atencion/config", { method: "PUT", headers: J, body: JSON.stringify(datos) });

export const guardarZonas = (zonas: { nombre: string; precio: number; notas: string | null }[]) =>
  fetchJson<ZonaEnvio[]>("/atencion/zonas", { method: "PUT", headers: J, body: JSON.stringify({ zonas }) });

export const subirQr = (etiqueta: string, imagenBase64: string) => post<QrPago>("/atencion/qr", { etiqueta, imagen_base64: imagenBase64 });

export const borrarQr = (id: string) => fetchJson<void>(`/atencion/qr/${id}`, { method: "DELETE" });

/** El QR se sube como PNG (sin pérdida) y achicado a 1200 px, para que se pueda escanear bien. */
export async function prepararQr(archivo: File): Promise<string> {
  if (!/^image\/(jpeg|png|webp)$/.test(archivo.type)) throw new Error("Elegí una imagen JPG, PNG o WebP del QR.");
  const bitmap = await createImageBitmap(archivo);
  const escala = Math.min(1, 1200 / Math.max(bitmap.width, bitmap.height));
  const lienzo = document.createElement("canvas");
  lienzo.width = Math.round(bitmap.width * escala);
  lienzo.height = Math.round(bitmap.height * escala);
  lienzo.getContext("2d")!.drawImage(bitmap, 0, 0, lienzo.width, lienzo.height);
  bitmap.close();
  const png = lienzo.toDataURL("image/png");
  if (png.length < 950_000) return png;
  const jpg = lienzo.toDataURL("image/jpeg", 0.92);
  if (jpg.length < 950_000) return jpg;
  throw new Error("La imagen del QR es demasiado pesada. Probá con una captura más chica.");
}
