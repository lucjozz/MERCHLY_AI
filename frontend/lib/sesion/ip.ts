/**
 * IP real del cliente para reenviarla al backend (límites por IP y bitácora).
 * Detrás de Cloudflare vale CF-Connecting-IP, que Cloudflare sobrescribe y no
 * se puede falsificar. El backend solo la usa con CONFIAR_PROXY=true (está
 * cerrado detrás de este BFF).
 */
export function ipCliente(headers: Headers): string {
  const cf = headers.get("cf-connecting-ip");
  if (cf) return cf.trim();
  return (headers.get("x-forwarded-for") ?? "").split(",")[0].trim() || "desconocida";
}
