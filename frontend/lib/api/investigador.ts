import { fetchAutenticado } from "@/lib/api/cliente";

export async function investigarProductos(
  categoria: string,
  mercadoObjetivo: string
): Promise<void> {
  const respuesta = await fetchAutenticado("/agentes/investigador-producto", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      categoria,
      mercado_objetivo: mercadoObjetivo,
      cantidad_resultados: 5,
    }),
  });

  if (!respuesta.ok) {
    throw new Error(`Error al investigar productos: ${respuesta.status}`);
  }
}