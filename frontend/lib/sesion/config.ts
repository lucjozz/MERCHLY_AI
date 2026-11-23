/**
 * Configuración de sesión del BFF (docs/013-Seguridad/04, sección 3).
 *
 * El navegador NUNCA ve los tokens: viven en cookies HttpOnly que solo lee
 * el servidor de Next (proxy.ts, Route Handlers y Server Components).
 * Este archivo no importa nada de servidor, así que lo puede usar proxy.ts.
 */

const ES_PRODUCCION = process.env.NODE_ENV === "production";

/** URL del backend, solo del lado servidor (nunca NEXT_PUBLIC_*). */
export const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

// En producción el prefijo __Host- obliga a Secure + Path=/ + sin Domain.
const PREFIJO = ES_PRODUCCION ? "__Host-" : "";
export const COOKIE_ACCESS = `${PREFIJO}merchly_at`;
export const COOKIE_REFRESH = `${PREFIJO}merchly_rt`;
/** Cookie vieja (escrita por JavaScript, legible por XSS): se borra si aparece. */
export const COOKIE_LEGADA = "merchly_token";

/** El access token se borra 30 s antes de vencer, así el proxy refresca a tiempo. */
export const MARGEN_ACCESS_SEGUNDOS = 30;

export const OPCIONES_COOKIE = {
  httpOnly: true,
  secure: ES_PRODUCCION,
  sameSite: "lax" as const,
  path: "/",
};

export interface SesionBackend {
  access_token: string;
  expira_en: number;
  refresh_token: string;
  refresh_expira_en: number;
}

/** Cookies que hay que escribir para una sesión nueva. */
export function cookiesDeSesion(sesion: SesionBackend) {
  return [
    {
      name: COOKIE_ACCESS,
      value: sesion.access_token,
      ...OPCIONES_COOKIE,
      maxAge: Math.max(1, sesion.expira_en - MARGEN_ACCESS_SEGUNDOS),
    },
    {
      name: COOKIE_REFRESH,
      value: sesion.refresh_token,
      ...OPCIONES_COOKIE,
      maxAge: sesion.refresh_expira_en,
    },
  ];
}

/** Cookies que hay que borrar al cerrar sesión. */
export const COOKIES_A_BORRAR = [COOKIE_ACCESS, COOKIE_REFRESH, COOKIE_LEGADA];

/**
 * Protección CSRF para Route Handlers que mutan: el Origin (o, si falta,
 * el Referer) tiene que ser el mismo sitio. Se suma a SameSite=Lax.
 */
export function mismoOrigen(request: Request, origenPropio: string): boolean {
  const origen = request.headers.get("origin");
  if (origen) return origen === origenPropio;
  const referer = request.headers.get("referer");
  if (referer) {
    try {
      return new URL(referer).origin === origenPropio;
    } catch {
      return false;
    }
  }
  return false;
}

/** Solo permite redirigir a rutas internas (evita open redirect). */
export function rutaInternaSegura(ruta: string | null | undefined): string {
  if (!ruta || !ruta.startsWith("/") || ruta.startsWith("//") || ruta.startsWith("/\\")) return "/";
  return ruta;
}
