/** Próximas temporadas comerciales de Bolivia (docs/004-Backend/05, sección 3). [] si no está disponible. */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";

export interface Temporada {
  clave: string;
  nombre: string;
  fecha: string;
  dias_faltantes: number;
  anticipacion_dias: number;
  preparar_ya: boolean;
  aproximada: boolean;
  ideas: string[];
}

export async function obtenerTemporadas(): Promise<Temporada[]> {
  try {
    const r = await fetchAutenticadoServidor("/temporadas");
    return r.ok ? r.json() : [];
  } catch {
    return [];
  }
}
