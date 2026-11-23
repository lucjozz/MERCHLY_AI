/** Equipo del negocio desde Server Components (solo admin; 403 para el resto). */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";

export interface Miembro {
  id: string;
  email: string;
  nombre: string;
  rol: string;
  activo: boolean;
  creado_en: string;
}

export interface Invitacion {
  id: string;
  email: string;
  rol: string;
  expira_en: string;
  aceptada_en: string | null;
  revocada_en: string | null;
  creado_en: string;
}

export async function listarMiembros(): Promise<Miembro[]> {
  const r = await fetchAutenticadoServidor("/usuarios");
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}

export async function listarInvitaciones(): Promise<Invitacion[]> {
  const r = await fetchAutenticadoServidor("/usuarios/invitaciones");
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}
