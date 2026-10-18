import { fetchAutenticado } from "@/lib/api/cliente";

export type AccionDecision = "approve" | "discard";

export interface DecisionInput {
  decision_type: string;
  entity_type: string;
  entity_id: string;
  action: AccionDecision;
  reason: string;
}

export async function registrarDecision(entrada: DecisionInput): Promise<void> {
  const respuesta = await fetchAutenticado("/decisiones", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entrada),
  });

  if (!respuesta.ok) {
    throw new Error(`Error al registrar la decisión: ${respuesta.status}`);
  }
}