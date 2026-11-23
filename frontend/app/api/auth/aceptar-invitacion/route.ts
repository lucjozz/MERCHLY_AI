/**
 * POST /api/auth/aceptar-invitacion — BFF para que una persona invitada cree
 * su cuenta. Reenvía token + nombre + contraseña al backend y guarda la
 * sesión en cookies HttpOnly (docs/004-Backend/03, sección 5).
 */
import { NextResponse, type NextRequest } from "next/server";
import {
  BACKEND_URL,
  COOKIE_LEGADA,
  cookiesDeSesion,
  mismoOrigen,
  type SesionBackend,
} from "@/lib/sesion/config";

export async function POST(request: NextRequest) {
  if (!mismoOrigen(request, request.nextUrl.origin)) {
    return NextResponse.json({ detail: "Origen no permitido." }, { status: 403 });
  }
  const cuerpo = (await request.json().catch(() => null)) as
    | { token?: unknown; nombre?: unknown; password?: unknown }
    | null;
  const { token, nombre, password } = cuerpo ?? {};
  if (typeof token !== "string" || typeof nombre !== "string" || typeof password !== "string" || token.length > 128) {
    return NextResponse.json({ detail: "Datos inválidos." }, { status: 422 });
  }

  const ip =
    request.headers.get("cf-connecting-ip")?.trim() ||
    (request.headers.get("x-forwarded-for") ?? "").split(",")[0].trim() ||
    "desconocida";

  let respuesta: Response;
  try {
    respuesta = await fetch(`${BACKEND_URL}/auth/aceptar-invitacion`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Forwarded-For": ip },
      body: JSON.stringify({ token, nombre, password }),
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

  const sesion = (await respuesta.json()) as SesionBackend;
  const salida = NextResponse.json({ ok: true });
  for (const c of cookiesDeSesion(sesion)) salida.cookies.set(c);
  salida.cookies.delete(COOKIE_LEGADA);
  salida.headers.set("Cache-Control", "no-store");
  return salida;
}
