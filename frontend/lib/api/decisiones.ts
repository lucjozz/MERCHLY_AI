import { fetchJson } from "@/lib/api/cliente";

export type AccionDecision = "approve" | "discard" | "request_review";

export interface DecisionInput {
  decision_type: string;
  entity_type: string;
  entity_id: string;
  action: AccionDecision;
  reason: string;
}

/** Registra una decisión. 409 = el producto ya fue decidido (estado final). */
export async function registrarDecision(entrada: DecisionInput): Promise<void> {
  await fetchJson("/decisiones", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(entrada),
  });
}
