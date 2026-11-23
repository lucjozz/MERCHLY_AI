/** Acciones de productos desde componentes CLIENTE (pasan por el BFF). */
import { fetchJson } from "@/lib/api/cliente";

/** Borrado lógico. Solo admin y responsable de negocio (403 si no). */
export async function eliminarProductoCandidato(id: string): Promise<void> {
  await fetchJson(`/productos-candidatos/${encodeURIComponent(id)}`, { method: "DELETE" });
}
