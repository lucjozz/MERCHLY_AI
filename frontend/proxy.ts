/**
 * Proxy de Next 16 (antes "middleware"). Corre antes de cada request:
 *
 * 1. Sin sesión → páginas redirigen a /login, /api responde 401.
 * 2. Access token vencido + refresh válido → refresca contra el backend,
 *    escribe las cookies nuevas en la respuesta y le pasa el token nuevo al
 *    resto del request (así los Server Components ya lo ven).
 * 3. Content-Security-Policy con nonce por request.
 *
 * Es un chequeo optimista: la autorización real la hace SIEMPRE el backend.
 * Ver docs/013-Seguridad/04, sección 3.
 */
import { NextResponse, type NextRequest } from "next/server";
import {
  BACKEND_URL,
  COOKIE_ACCESS,
  COOKIE_LEGADA,
  COOKIE_REFRESH,
  COOKIES_A_BORRAR,
  cookiesDeSesion,
  type SesionBackend,
} from "@/lib/sesion/config";

const RUTAS_PUBLICAS = ["/login", "/api/auth/login"];

function esPublica(ruta: string): boolean {
  return RUTAS_PUBLICAS.some((p) => ruta === p || ruta.startsWith(`${p}/`));
}

async function refrescar(refreshToken: string): Promise<SesionBackend | null> {
  try {
    const r = await fetch(`${BACKEND_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    return r.ok ? ((await r.json()) as SesionBackend) : null;
  } catch {
    return null;
  }
}

function construirCsp(nonce: string): string {
  const dev = process.env.NODE_ENV === "development";
  return [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${dev ? " 'unsafe-eval'" : ""}`,
    // Estilos inline (atributo style de React y Tailwind) sin ejecutar código.
    "style-src 'self' 'unsafe-inline' https://accounts.google.com/gsi/style",
    "img-src 'self' blob: data: https://*.googleusercontent.com",
    "font-src 'self'",
    `connect-src 'self' https://accounts.google.com/gsi/${dev ? " ws: wss:" : ""}`,
    // Botón y ventana de Google Identity Services.
    "frame-src https://accounts.google.com/gsi/",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    ...(dev ? [] : ["upgrade-insecure-requests"]),
  ].join("; ");
}

function borrarCookies(res: NextResponse): NextResponse {
  for (const nombre of COOKIES_A_BORRAR) res.cookies.delete(nombre);
  return res;
}

export async function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const esApi = pathname.startsWith("/api/");
  const access = request.cookies.get(COOKIE_ACCESS)?.value;
  const refresh = request.cookies.get(COOKIE_REFRESH)?.value;

  let sesionNueva: SesionBackend | null = null;
  if (!access && refresh) sesionNueva = await refrescar(refresh);
  const autenticado = Boolean(access || sesionNueva);

  if (!autenticado && !esPublica(pathname)) {
    if (esApi) {
      return borrarCookies(
        NextResponse.json({ detail: "Tu sesión venció. Volvé a iniciar sesión." }, { status: 401 })
      );
    }
    const login = new URL("/login", request.url);
    if (pathname !== "/") login.searchParams.set("siguiente", `${pathname}${search}`);
    return borrarCookies(NextResponse.redirect(login));
  }

  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  const csp = construirCsp(nonce);
  const headers = new Headers(request.headers);
  headers.set("x-nonce", nonce);
  headers.set("Content-Security-Policy", csp);

  if (sesionNueva) {
    // El resto del request (Server Components, Route Handlers) ve el token nuevo.
    const otras = request.cookies
      .getAll()
      .filter((c) => c.name !== COOKIE_ACCESS && c.name !== COOKIE_REFRESH)
      .map((c) => `${c.name}=${c.value}`);
    otras.push(`${COOKIE_ACCESS}=${sesionNueva.access_token}`);
    headers.set("cookie", otras.join("; "));
  }

  const respuesta = NextResponse.next({ request: { headers } });
  respuesta.headers.set("Content-Security-Policy", csp);
  if (sesionNueva) {
    for (const c of cookiesDeSesion(sesionNueva)) respuesta.cookies.set(c);
  }
  if (request.cookies.has(COOKIE_LEGADA)) respuesta.cookies.delete(COOKIE_LEGADA);
  return respuesta;
}

export const config = {
  matcher: [
    {
      source: "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:png|jpg|jpeg|svg|webp|ico)$).*)",
      missing: [{ type: "header", key: "next-router-prefetch" }],
    },
  ],
};
