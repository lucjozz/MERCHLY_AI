import { borrarToken, obtenerTokenCliente } from "@/lib/auth";
import { SesionInvalidaError } from "@/lib/api/errores";

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchAutenticado(
  ruta: string,
  init: RequestInit = {}
): Promise<Response> {
  const token = obtenerTokenCliente();
  if (!token) {
    window.location.href = "/login";
    throw new SesionInvalidaError();
  }

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);

  const respuesta = await fetch(`${API_URL}${ruta}`, { ...init, headers });

  if (respuesta.status === 401 || respuesta.status === 403) {
    borrarToken();
    window.location.href = "/login";
    throw new SesionInvalidaError();
  }

  return respuesta;
}