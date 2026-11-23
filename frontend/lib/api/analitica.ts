import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";

export interface GrupoResumen {
  clave: string;
  cantidad: number;
  porcentaje_del_total: number;
}

export interface ReporteAnalitica {
  resumen_catalogo: {
    total_productos_candidatos: number;
    grupos: GrupoResumen[];
  };
  tasa_conversion_catalogo: {
    candidato: number;
    en_catalogo: number;
    descartado: number;
    tasa_candidato_a_en_catalogo: number;
  };
  actividad_agente_investigador: {
    total_investigaciones: number;
    promedio_productos_por_investigacion: number;
    categorias_mas_investigadas: string[];
  };
}

export async function obtenerReporteAnalitica(): Promise<ReporteAnalitica> {
  const respuesta = await fetchAutenticadoServidor("/agentes/analitica-basica", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });

  if (!respuesta.ok) throw await errorDeRespuesta(respuesta);

  return respuesta.json();
}