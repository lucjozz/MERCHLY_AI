import { API_URL } from "@/lib/api/cliente";

export interface RespuestaLogin {
  access_token: string;
  token_type: string;
  expira_en: number;
}

export async function iniciarSesion(
  email: string,
  password: string
): Promise<RespuestaLogin> {
  let respuesta: Response;
  try {
    respuesta = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  } catch {
    throw new Error("No se pudo conectar con el backend. ¿Está corriendo?");
  }

  if (respuesta.status === 401) {
    throw new Error("Credenciales inválidas.");
  }
  if (!respuesta.ok) {
    throw new Error(`Error al iniciar sesión: ${respuesta.status}`);
  }

  return respuesta.json();
}