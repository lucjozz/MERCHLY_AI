/** Bitácora de auditoría desde Server Components (solo admin). */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";

export interface EventoAuditoria {
  id: string;
  accion: string;
  usuario_id: string | null;
  usuario_nombre: string | null;
  objetivo_tipo: string | null;
  detalle: Record<string, string | number | boolean | null>;
  ip: string | null;
  creado_en: string;
}

export interface EventosListado {
  eventos: EventoAuditoria[];
  total: number;
  pagina: number;
  tamano_pagina: number;
}

export async function listarEventos(pagina = 1, accion?: string): Promise<EventosListado> {
  const p = new URLSearchParams({ pagina: String(pagina), tamano_pagina: "50" });
  if (accion) p.set("accion", accion);
  const r = await fetchAutenticadoServidor(`/auditoria?${p}`);
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}
