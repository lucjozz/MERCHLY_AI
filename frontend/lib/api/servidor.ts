import { cookies, headers as headersEntrantes } from "next/headers";
import { ipCliente } from "@/lib/sesion/ip";
import { BACKEND_URL, COOKIE_ACCESS } from "@/lib/sesion/config";
import { SesionInvalidaError, SinPermisoError } from "@/lib/api/errores";

/**
 * Fetch al backend desde Server Components. Lee el access token de la
 * cookie HttpOnly (el proxy ya lo refrescó si hacía falta).
 *
 * - 401 → SesionInvalidaError (la página redirige a /login).
 * - 403 → SinPermisoError (NO es sesión vencida: se muestra "sin permiso").
 */
export async function fetchAutenticadoServidor(ruta: string, init: RequestInit = {}): Promise<Response> {
  const token = (await cookies()).get(COOKIE_ACCESS)?.value;
  if (!token) throw new SesionInvalidaError();

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);
  headers.set("X-Forwarded-For", ipCliente(await headersEntrantes()));

  const respuesta = await fetch(`${BACKEND_URL}${ruta}`, {
    ...init,
    headers,
    cache: "no-store",
    signal: init.signal ?? AbortSignal.timeout(30_000),
  });

  if (respuesta.status === 401) throw new SesionInvalidaError();
  if (respuesta.status === 403) throw new SinPermisoError();
  return respuesta;
}
