/** Lecturas de productos desde Server Components (con la sesión del usuario). */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";

export interface ProductoCandidato {
  id: string;
  nombre_producto: string;
  categoria: string;
  mercado_objetivo: string;
  precio_estimado_proveedor: number | null;
  precio_sugerido_venta: number | null;
  nivel_demanda_estimado: string;
  nivel_competencia_estimado: string;
  /** Solo en el detalle (el listado usa un schema resumido). */
  fuentes_evidencia?: string[];
  riesgos_identificados: string[];
  estado: string;
  /** Solo en el detalle. */
  investigacion_id?: string;
  creado_en: string;
}

/** El detalle siempre trae evidencia e id de investigación. */
export interface ProductoCandidatoDetalle extends ProductoCandidato {
  fuentes_evidencia: string[];
  investigacion_id: string;
}

export interface ProductosCandidatosListado {
  productos: ProductoCandidato[];
  total: number;
  pagina: number;
  tamano_pagina: number;
}

export async function listarProductosCandidatos(
  pagina: number = 1,
  tamanoPagina: number = 20,
  categoria?: string,
  estado?: string
): Promise<ProductosCandidatosListado> {
  const parametros = new URLSearchParams({
    pagina: String(pagina),
    tamano_pagina: String(tamanoPagina),
  });

  if (categoria) parametros.set("categoria", categoria);
  if (estado) parametros.set("estado", estado);

  const respuesta = await fetchAutenticadoServidor(`/productos-candidatos?${parametros}`);
  if (!respuesta.ok) throw await errorDeRespuesta(respuesta);

  return respuesta.json();
}

export async function obtenerProductoCandidato(
  id: string
): Promise<ProductoCandidatoDetalle | null> {
  // 422 = id con formato inválido: para la persona es lo mismo que "no existe".
  const respuesta = await fetchAutenticadoServidor(`/productos-candidatos/${encodeURIComponent(id)}`);
  if (respuesta.status === 404 || respuesta.status === 422) return null;
  if (!respuesta.ok) throw await errorDeRespuesta(respuesta);

  return respuesta.json();
}
