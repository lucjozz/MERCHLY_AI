import { cookies } from "next/headers";
import { COOKIE_TOKEN } from "@/lib/auth";
import { SesionInvalidaError } from "@/lib/api/errores";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchAutenticadoServidor(
  ruta: string,
  init: RequestInit = {}
): Promise<Response> {
  const almacen = await cookies();
  const token = almacen.get(COOKIE_TOKEN)?.value;
  if (!token) throw new SesionInvalidaError();

  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);

  const respuesta = await fetch(`${API_URL}${ruta}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (respuesta.status === 401 || respuesta.status === 403) {
    throw new SesionInvalidaError();
  }

  return respuesta;
}