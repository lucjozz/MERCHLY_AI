import { redirect } from "next/navigation";
import { ApiError, SesionInvalidaError, SinPermisoError } from "@/lib/api/errores";
import { MENSAJE_SIN_BACKEND } from "@/components/ui/Alerta";

/**
 * Manejo común de errores en Server Components:
 * - sesión vencida/revocada → /login
 * - sin permiso / error de la API → su mensaje legible
 * - cualquier otra cosa (backend caído, red) → mensaje de conexión
 */
export function mensajeDeErrorDePagina(error: unknown): string {
  if (error instanceof SesionInvalidaError) redirect("/login");
  if (error instanceof SinPermisoError || error instanceof ApiError) return error.message;
  return MENSAJE_SIN_BACKEND;
}
