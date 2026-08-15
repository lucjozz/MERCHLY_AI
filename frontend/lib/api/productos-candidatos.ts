const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ProductoCandidato {
  id: string;
  nombre_producto: string;
  categoria: string;
  mercado_objetivo: string;
  precio_estimado_proveedor: number | null;
  precio_sugerido_venta: number | null;
  nivel_demanda_estimado: string;
  nivel_competencia_estimado: string;
  fuentes_evidencia: string[];
  riesgos_identificados: string[];
  estado: string;
  investigacion_id: string;
  creado_en: string;
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

  const respuesta = await fetch(`${API_URL}/productos-candidatos?${parametros}`);

  if (!respuesta.ok) {
    throw new Error(
      `Error al obtener productos candidatos: ${respuesta.status}`
    );
  }

  return respuesta.json();
}

export async function obtenerProductoCandidato(
  id: string
): Promise<ProductoCandidato | null> {
  const respuesta = await fetch(`${API_URL}/productos-candidatos/${id}`);

  if (respuesta.status === 404) {
    return null;
  }

  if (!respuesta.ok) {
    throw new Error(`Error al obtener el producto: ${respuesta.status}`);
  }

  return respuesta.json();
}