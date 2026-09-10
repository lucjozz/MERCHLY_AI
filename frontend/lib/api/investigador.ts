const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function investigarProductos(
  categoria: string,
  mercadoObjetivo: string
): Promise<void> {
  const respuesta = await fetch(`${API_URL}/agentes/investigador-producto`, {
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