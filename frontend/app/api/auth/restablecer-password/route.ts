/** POST /api/auth/restablecer-password — pública: cambia la contraseña con el link del email. */
import type { NextRequest } from "next/server";
import { reenviarPublico } from "@/lib/sesion/reenviar-publico";

export async function POST(request: NextRequest) {
  return reenviarPublico(request, "/auth/restablecer-password");
}
