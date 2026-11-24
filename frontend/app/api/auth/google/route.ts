/**
 * POST /api/auth/google — BFF del login con Google. Reenvía el ID token al
 * backend (que verifica firma, audiencia y email verificado) y guarda la
 * sesión en cookies HttpOnly.
 */
import { NextResponse, type NextRequest } from "next/server";
import { ipCliente } from "@/lib/sesion/ip";
import { respuestaDeLogin } from "@/lib/sesion/respuesta-login";
import {
  BACKEND_URL,
  mismoOrigen,
} from "@/lib/sesion/config";

export async function POST(request: NextRequest) {
  if (!mismoOrigen(request, request.nextUrl.origin)) {
    return NextResponse.json({ detail: "Origen no permitido." }, { status: 403 });
  }
  const cuerpo = (await request.json().catch(() => null)) as { id_token?: unknown } | null;
  const idToken = cuerpo?.id_token;
  if (typeof idToken !== "string" || idToken.length > 4096) {
    return NextResponse.json({ detail: "Datos inválidos." }, { status: 422 });
  }

  const ip = ipCliente(request.headers);

  let respuesta: Response;
  try {
    respuesta = await fetch(`${BACKEND_URL}/auth/google`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Forwarded-For": ip },
      body: JSON.stringify({ id_token: idToken }),
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
  } catch {
    return NextResponse.json(
      { detail: "No pudimos conectarnos con el servidor. Probá de nuevo en un momento." },
      { status: 503 }
    );
  }

  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    const salida = NextResponse.json(
      { detail: typeof detalle?.detail === "string" ? detalle.detail : "No se pudo iniciar sesión." },
      { status: respuesta.status }
    );
    const retry = respuesta.headers.get("retry-after");
    if (retry) salida.headers.set("Retry-After", retry);
    return salida;
  }

  return respuestaDeLogin(respuesta);
}
