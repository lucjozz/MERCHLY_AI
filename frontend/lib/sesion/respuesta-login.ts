/**
 * Respuesta común del BFF a un login exitoso (contraseña o Google).
 *
 * Si el usuario tiene la verificación en dos pasos activada, el backend no da
 * la sesión sino un DESAFÍO de un solo uso: se guarda en una cookie HttpOnly
 * de 5 minutos (el JavaScript de la página nunca lo ve) y el navegador solo
 * recibe { requiere_2fa: true } para mostrar el campo del código.
 */
import { NextResponse } from "next/server";
import { COOKIE_2FA, COOKIE_LEGADA, OPCIONES_COOKIE_2FA, cookiesDeSesion, type SesionBackend } from "@/lib/sesion/config";

export async function respuestaDeLogin(respuesta: Response): Promise<NextResponse> {
  const cuerpo = (await respuesta.json()) as SesionBackend | { requiere_2fa: true; desafio: string };
  if ("requiere_2fa" in cuerpo && cuerpo.requiere_2fa) {
    const salida = NextResponse.json({ requiere_2fa: true });
    salida.cookies.set({ name: COOKIE_2FA, value: cuerpo.desafio, ...OPCIONES_COOKIE_2FA });
    salida.headers.set("Cache-Control", "no-store");
    return salida;
  }
  const salida = NextResponse.json({ ok: true });
  for (const c of cookiesDeSesion(cuerpo as SesionBackend)) salida.cookies.set(c);
  salida.cookies.delete(COOKIE_LEGADA);
  salida.cookies.delete(COOKIE_2FA);
  salida.headers.set("Cache-Control", "no-store");
  return salida;
}
