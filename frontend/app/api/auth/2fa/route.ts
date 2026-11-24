/**
 * POST /api/auth/2fa — segundo paso del login (docs/013-Seguridad/09).
 * Toma el desafío de la cookie HttpOnly, lo manda al backend con el código del
 * celular (o de respaldo) y, si es correcto, guarda las cookies de sesión.
 */
import { NextResponse, type NextRequest } from "next/server";
import { ipCliente } from "@/lib/sesion/ip";
import { BACKEND_URL, COOKIE_2FA, mismoOrigen } from "@/lib/sesion/config";
import { respuestaDeLogin } from "@/lib/sesion/respuesta-login";


export async function POST(request: NextRequest) {
  if (!mismoOrigen(request, request.nextUrl.origin)) {
    return NextResponse.json({ detail: "Origen no permitido." }, { status: 403 });
  }
  const desafio = request.cookies.get(COOKIE_2FA)?.value;
  if (!desafio) {
    return NextResponse.json({ detail: "El código venció. Volvé a ingresar tu contraseña." }, { status: 401 });
  }
  const cuerpo = (await request.json().catch(() => null)) as { codigo?: unknown } | null;
  const codigo = typeof cuerpo?.codigo === "string" ? cuerpo.codigo.trim().slice(0, 12) : "";
  if (codigo.length < 6) return NextResponse.json({ detail: "Escribí el código de 6 dígitos." }, { status: 422 });

  let respuesta: Response;
  try {
    respuesta = await fetch(`${BACKEND_URL}/auth/2fa/verificar`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Forwarded-For": ipCliente(request.headers) },
      body: JSON.stringify({ desafio, codigo }),
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
  } catch {
    return NextResponse.json({ detail: "No pudimos conectarnos con el servidor. Probá de nuevo en un momento." }, { status: 503 });
  }
  if (!respuesta.ok) {
    const detalle = await respuesta.json().catch(() => ({}));
    const salida = NextResponse.json(
      { detail: typeof detalle?.detail === "string" ? detalle.detail : "No se pudo verificar el código." },
      { status: respuesta.status }
    );
    const retry = respuesta.headers.get("retry-after");
    if (retry) salida.headers.set("Retry-After", retry);
    return salida;
  }
  return respuestaDeLogin(respuesta);
}
