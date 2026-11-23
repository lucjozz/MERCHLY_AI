/**
 * POST /api/auth/logout — revoca la sesión en el backend (access token a la
 * denylist y refresh token revocado) y borra las cookies.
 * Con { todas: true } cierra la sesión en TODOS los dispositivos.
 */
import { NextResponse, type NextRequest } from "next/server";
import {
  BACKEND_URL,
  COOKIE_ACCESS,
  COOKIE_REFRESH,
  COOKIES_A_BORRAR,
  mismoOrigen,
} from "@/lib/sesion/config";

export async function POST(request: NextRequest) {
  if (!mismoOrigen(request, request.nextUrl.origin)) {
    return NextResponse.json({ detail: "Origen no permitido." }, { status: 403 });
  }
  const access = request.cookies.get(COOKIE_ACCESS)?.value;
  const refresh = request.cookies.get(COOKIE_REFRESH)?.value;
  const { todas } = ((await request.json().catch(() => ({}))) ?? {}) as { todas?: boolean };

  if (access) {
    const headers = { Authorization: `Bearer ${access}`, "Content-Type": "application/json" };
    const opciones = { cache: "no-store" as const, signal: AbortSignal.timeout(5000) };
    try {
      if (todas) {
        await fetch(`${BACKEND_URL}/auth/cerrar-todas-las-sesiones`, { method: "POST", headers, ...opciones });
      }
      await fetch(`${BACKEND_URL}/auth/logout`, {
        method: "POST",
        headers,
        body: JSON.stringify(refresh ? { refresh_token: refresh } : {}),
        ...opciones,
      });
    } catch {
      // Aunque el backend no responda, las cookies se borran igual.
    }
  }

  const salida = NextResponse.json({ ok: true });
  for (const nombre of COOKIES_A_BORRAR) salida.cookies.delete(nombre);
  salida.headers.set("Cache-Control", "no-store");
  return salida;
}
