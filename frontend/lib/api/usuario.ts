import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";

export interface UsuarioActual {
  id: string;
  email: string;
  nombre: string;
  rol: string;
  activo: boolean;
  organizacion_id: string;
  organizacion_nombre: string | null;
  totp_activado?: boolean;
}

export async function obtenerUsuarioActual(): Promise<UsuarioActual> {
  const respuesta = await fetchAutenticadoServidor("/auth/me");

  if (!respuesta.ok) throw await errorDeRespuesta(respuesta);

  return respuesta.json();
}