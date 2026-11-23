/**
 * Login y logout desde el navegador, vía el BFF de Next. El navegador nunca
 * recibe ni guarda tokens: quedan en cookies HttpOnly.
 */
import { MENSAJE_SIN_CONEXION, mensajeDeError } from "@/lib/api/errores";

export async function iniciarSesion(email: string, password: string): Promise<void> {
  let respuesta: Response;
  try {
    respuesta = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ email, password }),
    });
  } catch {
    throw new Error(MENSAJE_SIN_CONEXION);
  }
  if (!respuesta.ok) {
    const cuerpo = await respuesta.json().catch(() => ({}));
    if (respuesta.status === 401) throw new Error("Email o contraseña incorrectos.");
    throw new Error(mensajeDeError(respuesta.status, cuerpo?.detail, respuesta.headers.get("retry-after")));
  }
}

/** Cierra la sesión (revoca tokens en el backend y borra cookies). */
export async function cerrarSesion(todas = false): Promise<void> {
  try {
    await fetch("/api/auth/logout", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify({ todas }),
    });
  } finally {
    // Navegación completa a propósito: descarta todo el estado del cliente.
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign("/login");
  }
}
