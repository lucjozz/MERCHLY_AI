/**
 * Reenvío al backend para endpoints PÚBLICOS del BFF (sin sesión):
 * verifica Origin (CSRF), tope de tamaño, IP real del cliente para el límite
 * de intentos, y nunca devuelve detalles internos.
 */
import { NextResponse, type NextRequest } from "next/server";
import { BACKEND_URL, mismoOrigen } from "@/lib/sesion/config";

const MAX_BYTES = 8 * 1024;

export async function reenviarPublico(request: NextRequest, rutaBackend: string): Promise<NextResponse> {
  if (!mismoOrigen(request, request.nextUrl.origin)) {
    return NextResponse.json({ detail: "Origen no permitido." }, { status: 403 });
  }
  const cuerpo = await request.text();
  if (new TextEncoder().encode(cuerpo).length > MAX_BYTES) {
    return NextResponse.json({ detail: "La solicitud es demasiado grande." }, { status: 413 });
  }
  const ip =
    request.headers.get("cf-connecting-ip")?.trim() ||
    (request.headers.get("x-forwarded-for") ?? "").split(",")[0].trim() ||
    "desconocida";
  let respuesta: Response;
  try {
    respuesta = await fetch(`${BACKEND_URL}${rutaBackend}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Forwarded-For": ip },
      body: cuerpo,
      cache: "no-store",
      signal: AbortSignal.timeout(15_000),
    });
  } catch {
    return NextResponse.json({ detail: "No pudimos conectarnos con el servidor. Probá de nuevo en un momento." }, { status: 503 });
  }
  const texto = respuesta.status === 204 ? null : await respuesta.text();
  const salida = new NextResponse(texto, { status: respuesta.status });
  salida.headers.set("Content-Type", "application/json");
  salida.headers.set("Cache-Control", "no-store");
  const retry = respuesta.headers.get("retry-after");
  if (retry) salida.headers.set("Retry-After", retry);
  return salida;
}
