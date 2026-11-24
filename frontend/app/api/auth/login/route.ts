/**
 * POST /api/auth/login — BFF del login (docs/013-Seguridad/04, sección 3).
 * Reenvía email y contraseña al backend y guarda los tokens en cookies
 * HttpOnly. Al navegador solo le responde { ok: true }.
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

  let cuerpo: unknown;
  try {
    cuerpo = await request.json();
  } catch {
    return NextResponse.json({ detail: "Datos inválidos." }, { status: 422 });
  }
  const { email, password } = (cuerpo ?? {}) as { email?: unknown; password?: unknown };
  if (typeof email !== "string" || typeof password !== "string") {
    return NextResponse.json({ detail: "Datos inválidos." }, { status: 422 });
  }

  let respuesta: Response;
  try {
    respuesta = await fetch(`${BACKEND_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // IP real del cliente para el rate limit del backend (que solo la usa
        // con CONFIAR_PROXY=true). Detrás de Cloudflare manda CF-Connecting-IP,
        // que Cloudflare sobrescribe y no se puede falsificar.
        "X-Forwarded-For": ipCliente(request.headers),
      },
      body: JSON.stringify({ email, password }),
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
