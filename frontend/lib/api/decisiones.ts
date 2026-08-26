const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type AccionDecision = "approve" | "discard";

export interface DecisionInput {
  decision_type: string;
  entity_type: string;
  entity_id: string;
  action: AccionDecision;
  user_id: string;
  reason: string;
}

export async function registrarDecision(
  entrada: DecisionInput
): Promise<void> {
  const respuesta = await fetch(`${API_URL}/decisiones`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entrada),
  });

  if (!respuesta.ok) {
    throw new Error(`Error al registrar la decisión: ${respuesta.status}`);
  }
}