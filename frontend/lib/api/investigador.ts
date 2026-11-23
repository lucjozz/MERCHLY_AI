import { fetchJson } from "@/lib/api/cliente";

export async function investigarProductos(categoria: string, mercadoObjetivo: string): Promise<void> {
  await fetchJson("/agentes/investigador-producto", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ categoria, mercado_objetivo: mercadoObjetivo, cantidad_resultados: 5 }),
  });
}
