/** Historial de campañas desde Server Components. */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";

export interface CopyTexto {
  titulo: string;
  cuerpo: string;
}

export interface CampanaResumen {
  id: string;
  titulo: string;
  canales: string[];
  tono: string;
  modelo: string | null;
  editada: boolean;
  creado_en: string;
}

export interface CampanaDetalle extends CampanaResumen {
  productos_candidato_ids: string[];
  idioma: string;
  actualizado_en: string;
  contenido: {
    angulos: string[];
    copy_por_canal: Record<string, CopyTexto[]>;
    publico_objetivo: string;
    advertencias: string[];
  };
}

export interface CampanasListado {
  campanas: CampanaResumen[];
  total: number;
  pagina: number;
  tamano_pagina: number;
}

export async function listarCampanas(pagina = 1, tamanoPagina = 50): Promise<CampanasListado> {
  const r = await fetchAutenticadoServidor(`/campanas?pagina=${pagina}&tamano_pagina=${tamanoPagina}`);
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}

export async function obtenerCampana(id: string): Promise<CampanaDetalle | null> {
  const r = await fetchAutenticadoServidor(`/campanas/${encodeURIComponent(id)}`);
  if (r.status === 404 || r.status === 422) return null;
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}
