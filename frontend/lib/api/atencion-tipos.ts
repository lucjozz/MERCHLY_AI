/** Tipos del Agente de Atención al Cliente (docs/007-Agentes/09). Sin dependencias de servidor. */

export interface AtencionConfig {
  encendido: boolean;
  completar_ventas: boolean;
  presentacion: string | null;
  info_negocio: string | null;
  minutos_reserva: number;
  proveedor: "openai" | "simulado";
  plan_incluye: boolean;
}

export interface QrPago {
  id: string;
  etiqueta: string;
}

export interface ZonaEnvio {
  id?: string;
  nombre: string;
  precio: string | number;
  notas: string | null;
}

export interface Adjunto {
  tipo: "qr" | "producto";
  qr_id?: string;
  producto_id?: string;
  foto_id?: string;
}

export interface Mensaje {
  id: string;
  rol: "comprador" | "agente" | "vendedor" | "sistema";
  texto: string;
  adjuntos: Adjunto[];
  simulado: boolean;
  creado_en: string;
}

export interface ConversacionResumen {
  id: string;
  canal: string;
  contacto: string;
  nombre_contacto: string | null;
  atendida_por: "agente" | "humano";
  ultimo_mensaje_en: string | null;
  creado_en: string;
}

export interface ConversacionDetalle extends ConversacionResumen {
  mensajes: Mensaje[];
}

export interface Pedido {
  id: string;
  conversacion_id: string | null;
  estado: string;
  items: { producto_id: string; nombre: string; cantidad: number; precio_unitario: string }[];
  subtotal: string;
  zona_envio: string | null;
  costo_envio: string;
  total: string;
  nombre_comprador: string | null;
  direccion: string | null;
  reservado_hasta: string | null;
  simulado: boolean;
  decidido_en: string | null;
  creado_en: string;
}

export interface Notificacion {
  id: string;
  tipo: string;
  titulo: string;
  cuerpo: string | null;
  pedido_id: string | null;
  conversacion_id: string | null;
  leida_en: string | null;
  creado_en: string;
}

export const ESTADO_PEDIDO: Record<string, { texto: string; tono: "ambar" | "verde" | "azul" | "gris" | "rojo" }> = {
  pedido_armado: { texto: "Para cerrar", tono: "azul" },
  reservado: { texto: "Reservado · esperando pago", tono: "ambar" },
  pago_por_confirmar: { texto: "Pago por confirmar", tono: "ambar" },
  pagado: { texto: "Pagado", tono: "verde" },
  entregado: { texto: "Entregado", tono: "verde" },
  vencido: { texto: "Reserva vencida", tono: "gris" },
  rechazado: { texto: "Pago rechazado", tono: "rojo" },
  cancelado: { texto: "Cancelado", tono: "gris" },
};

export const urlQr = (id: string) => `/api/backend/atencion/qr/${id}/imagen`;
