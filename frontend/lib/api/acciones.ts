/**
 * Acciones desde componentes CLIENTE para las funciones de DEC-034
 * (pasan por el BFF: /api/backend/... con cookie HttpOnly).
 */
import { fetchJson } from "@/lib/api/cliente";
import { MENSAJE_SIN_CONEXION, mensajeDeError } from "@/lib/api/errores";
import type { CampanaDetalle, CopyTexto } from "@/lib/api/campanas";
import type { Invitacion, Miembro } from "@/lib/api/equipo";
import type { Organizacion } from "@/lib/api/organizacion";

const JSON_HEADERS = { "Content-Type": "application/json" };

// ---------------------------------------------------------------- campañas

export interface EdicionCampana {
  titulo?: string;
  angulos?: string[];
  copy_por_canal?: Record<string, CopyTexto[]>;
  publico_objetivo?: string;
}

export function editarCampana(id: string, cambios: EdicionCampana): Promise<CampanaDetalle> {
  return fetchJson(`/campanas/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: JSON_HEADERS,
    body: JSON.stringify(cambios),
  });
}

export async function eliminarCampana(id: string): Promise<void> {
  await fetchJson(`/campanas/${encodeURIComponent(id)}`, { method: "DELETE" });
}

// ---------------------------------------------------------------- perfil

export interface PerfilNegocio {
  nombre: string;
  pais: string;
  rubro: string;
  presupuesto_mensual: number | null;
  moneda: "BOB" | "USD";
  tipo_cambio: number | null;
  costo_envio_unitario_usd: number;
  impuestos_importacion_pct: number;
}

export function guardarPerfil(perfil: PerfilNegocio): Promise<Organizacion> {
  return fetchJson("/organizacion/perfil", { method: "PUT", headers: JSON_HEADERS, body: JSON.stringify(perfil) });
}

// ---------------------------------------------------------------- equipo

export interface InvitacionCreada extends Invitacion {
  token: string;
}

export function invitarMiembro(email: string, rol: string): Promise<InvitacionCreada> {
  return fetchJson("/usuarios/invitaciones", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify({ email, rol }) });
}

export async function revocarInvitacion(id: string): Promise<void> {
  await fetchJson(`/usuarios/invitaciones/${encodeURIComponent(id)}`, { method: "DELETE" });
}

export function cambiarMiembro(id: string, cambio: { rol?: string; activo?: boolean }): Promise<Miembro> {
  return fetchJson(`/usuarios/${encodeURIComponent(id)}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(cambio) });
}

/** Pública (sin sesión): crea la cuenta de la persona invitada e inicia su sesión. */
export async function aceptarInvitacion(token: string, nombre: string, password: string): Promise<void> {
  let r: Response;
  try {
    r = await fetch("/api/auth/aceptar-invitacion", {
      method: "POST",
      headers: JSON_HEADERS,
      credentials: "same-origin",
      body: JSON.stringify({ token, nombre, password }),
    });
  } catch {
    throw new Error(MENSAJE_SIN_CONEXION);
  }
  if (!r.ok) {
    const cuerpo = await r.json().catch(() => ({}));
    const detalle = typeof cuerpo?.detail === "string" ? cuerpo.detail : undefined;
    throw new Error(r.status === 400 || r.status === 422 ? detalle ?? mensajeDeError(r.status) : mensajeDeError(r.status, detalle, r.headers.get("retry-after")));
  }
}
