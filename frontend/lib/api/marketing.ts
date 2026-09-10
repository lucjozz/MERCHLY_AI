const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
  productoId: string
): Promise<CampanaMarketing> {
  const respuesta = await fetch(`${API_URL}/agentes/marketing`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      productos_candidato_ids: [productoId],
      canales_objetivo: ["email"],
      idioma_destino: "es",
    }),
  });

  if (!respuesta.ok) {
    throw new Error(`Error al generar la campaña: ${respuesta.status}`);
  }

  return respuesta.json();
}