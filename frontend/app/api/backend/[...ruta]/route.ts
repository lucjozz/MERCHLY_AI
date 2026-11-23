/**
 * /api/backend/... — BFF para los componentes cliente
 * (docs/013-Seguridad/04, sección 3).
 *
 * El navegador llama acá (mismo origen, cookie HttpOnly automática) y este
 * handler reenvía al backend agregando el Bearer. Solo se reenvían rutas de
 * una LISTA BLANCA: no es un proxy abierto hacia el backend.
 */
import { NextResponse, type NextRequest } from "next/server";
import { BACKEND_URL, COOKIE_ACCESS, mismoOrigen } from "@/lib/sesion/config";

const UUID = "[0-9a-fA-F-]{36}";
const PERMITIDAS: Record<string, RegExp[]> = {
  GET: [
    new RegExp(`^productos-candidatos(/${UUID})?$`),
    new RegExp(`^decisiones/${UUID}$`),
    new RegExp(`^campanas(/${UUID})?$`),
    /^auth\/me$/,
    /^organizacion(\/uso)?$/,
    /^usuarios(\/invitaciones)?$/,
  ],
  POST: [
    /^agentes\/(investigador-producto|marketing|analitica-basica)$/,
    /^decisiones$/,
    /^usuarios\/invitaciones$/,
  ],
  PUT: [/^organizacion\/perfil$/],
  PATCH: [new RegExp(`^campanas/${UUID}$`), new RegExp(`^usuarios/${UUID}$`)],
  DELETE: [
    new RegExp(`^productos-candidatos/${UUID}$`),
    new RegExp(`^campanas/${UUID}$`),
    new RegExp(`^usuarios/invitaciones/${UUID}$`),
  ],
};
const MAX_BODY_BYTES = 64 * 1024;

async function reenviar(request: NextRequest, segmentos: string[]) {
  const metodo = request.method.toUpperCase();
  const ruta = segmentos.map(encodeURIComponent).join("/");

  if (!(PERMITIDAS[metodo] ?? []).some((re) => re.test(ruta))) {
    return NextResponse.json({ detail: "No existe." }, { status: 404 });
  }
  if (metodo !== "GET" && !mismoOrigen(request, request.nextUrl.origin)) {
    return NextResponse.json({ detail: "Origen no permitido." }, { status: 403 });
  }

  const access = request.cookies.get(COOKIE_ACCESS)?.value;
  if (!access) {
    return NextResponse.json({ detail: "Tu sesión venció. Volvé a iniciar sesión." }, { status: 401 });
  }

  let cuerpo: string | undefined;
  if (metodo === "POST" || metodo === "PUT" || metodo === "PATCH") {
    cuerpo = await request.text();
    if (new TextEncoder().encode(cuerpo).length > MAX_BODY_BYTES) {
      return NextResponse.json({ detail: "La solicitud es demasiado grande." }, { status: 413 });
    }
  }

  let respuesta: Response;
  try {
    respuesta = await fetch(`${BACKEND_URL}/${ruta}${request.nextUrl.search}`, {
      method: metodo,
      headers: {
        Authorization: `Bearer ${access}`,
        ...(cuerpo !== undefined ? { "Content-Type": "application/json" } : {}),
      },
      body: cuerpo,
      cache: "no-store",
      // Los agentes de IA pueden tardar; nunca colgar indefinidamente.
      signal: AbortSignal.timeout(60_000),
    });
  } catch {
    return NextResponse.json(
      { detail: "No pudimos conectarnos con el servidor. Probá de nuevo en un momento." },
      { status: 503 }
    );
  }

  const texto = respuesta.status === 204 ? null : await respuesta.text();
  const salida = new NextResponse(texto, { status: respuesta.status });
  salida.headers.set("Content-Type", respuesta.headers.get("content-type") ?? "application/json");
  salida.headers.set("Cache-Control", "no-store");
  const retry = respuesta.headers.get("retry-after");
  if (retry) salida.headers.set("Retry-After", retry);
  return salida;
}

type Contexto = { params: Promise<{ ruta: string[] }> };

export async function GET(request: NextRequest, { params }: Contexto) {
  return reenviar(request, (await params).ruta);
}
export async function POST(request: NextRequest, { params }: Contexto) {
  return reenviar(request, (await params).ruta);
}
export async function PUT(request: NextRequest, { params }: Contexto) {
  return reenviar(request, (await params).ruta);
}
export async function PATCH(request: NextRequest, { params }: Contexto) {
  return reenviar(request, (await params).ruta);
}
export async function DELETE(request: NextRequest, { params }: Contexto) {
  return reenviar(request, (await params).ruta);
}
