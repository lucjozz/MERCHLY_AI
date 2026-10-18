import { fetchAutenticado } from "@/lib/api/cliente";

export type CanalMarketing = "busqueda_paga" | "redes_sociales" | "email";
export type TonoMarketing = "neutral" | "entusiasta" | "tecnico" | "premium";

export interface CopyCanal {
  titulo: string;
  cuerpo: string;
}

export interface CampanaMarketing {
  angulos_de_campana: string[];
  copy_por_canal: Record<string, CopyCanal[]>;
  publico_objetivo_sugerido: string;
  advertencias: string[];
}

export async function generarCampanaMarketing(
  productoId: string,
  canales: CanalMarketing[] = ["email"],
  tono: TonoMarketing = "neutral"
): Promise<CampanaMarketing> {
  const respuesta = await fetchAutenticado("/agentes/marketing", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      productos_candidato_ids: [productoId],
      canales_objetivo: canales,
      idioma_destino: "es",
      tono,
    }),
  });

  if (!respuesta.ok) {
    throw new Error(`Error al generar la campaña: ${respuesta.status}`);
  }

  return respuesta.json();
}