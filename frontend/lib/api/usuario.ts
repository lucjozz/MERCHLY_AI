import { fetchAutenticadoServidor } from "@/lib/api/servidor";

export interface UsuarioActual {
  id: string;
  email: string;
  nombre: string;
  rol: string;
  activo: boolean;
}

export async function obtenerUsuarioActual(): Promise<UsuarioActual> {
  const respuesta = await fetchAutenticadoServidor("/auth/me");

  if (!respuesta.ok) {
    throw new Error(`Error al obtener el usuario: ${respuesta.status}`);
  }

  return respuesta.json();
}