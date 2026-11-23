/**
 * Cliente de API para componentes CLIENTE (navegador).
 *
 * Nunca habla directo con el backend ni toca tokens: llama a /api/backend/...
 * del mismo origen; la cookie HttpOnly viaja sola y el BFF agrega el Bearer.
 *
 * - 401 → la sesión venció: se va a /login (volviendo después a esta página).
 * - 403 → NO cierra la sesión: lanza SinPermisoError para mostrar un mensaje.
 */
import { MENSAJE_SIN_CONEXION, SesionInvalidaError, errorDeRespuesta } from "@/lib/api/errores";

export async function fetchAutenticado(ruta: string, init: RequestInit = {}): Promise<Response> {
  let respuesta: Response;
  try {
    respuesta = await fetch(`/api/backend${ruta}`, {
      ...init,
      credentials: "same-origin",
      cache: "no-store",
    });
  } catch {
    throw new Error(MENSAJE_SIN_CONEXION);
  }

  if (respuesta.status === 401) {
    const volver = encodeURIComponent(window.location.pathname + window.location.search);
    // Navegación completa a propósito: descarta todo el estado del cliente.
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign(`/login?siguiente=${volver}`);
    throw new SesionInvalidaError();
  }
  return respuesta;
}

/** fetchAutenticado + lanza un error con mensaje legible si no es 2xx. */
export async function fetchJson<T>(ruta: string, init: RequestInit = {}): Promise<T> {
  const respuesta = await fetchAutenticado(ruta, init);
  if (!respuesta.ok) throw await errorDeRespuesta(respuesta);
  return (respuesta.status === 204 ? undefined : await respuesta.json()) as T;
}
