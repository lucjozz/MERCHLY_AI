/** POST /api/auth/olvide-password — pública. Siempre la misma respuesta (sin enumeración). */
import type { NextRequest } from "next/server";
import { reenviarPublico } from "@/lib/sesion/reenviar-publico";

export async function POST(request: NextRequest) {
  return reenviarPublico(request, "/auth/olvide-password");
}
