import { fetchJson } from "@/lib/api/cliente";

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
  metadata?: { campana_id?: string; modelo?: string | null };
}

export async function generarCampanaMarketing(
  productoId: string,
  canales: CanalMarketing[] = ["email"],
  tono: TonoMarketing = "neutral"
): Promise<CampanaMarketing> {
  return fetchJson<CampanaMarketing>("/agentes/marketing", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      productos_candidato_ids: [productoId],
      canales_objetivo: canales,
      idioma_destino: "es",
      tono,
    }),
  });
}
