/** Dólar oficial del BCB (DEC-035), desde Server Components. Null si no está disponible. */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";

export interface TipoCambioBcb {
  valor: number;
  fecha: string | null;
  fuente: string;
  actualizado: string;
  desactualizado: boolean;
}

export async function obtenerTipoCambioBcb(): Promise<TipoCambioBcb | null> {
  try {
    const r = await fetchAutenticadoServidor("/tipo-cambio");
    return r.ok ? r.json() : null;
  } catch {
    return null;
  }
}

/** El del negocio si cargó uno propio; si no, el oficial del BCB. */
export function tipoCambioEfectivo(propio: number | null | undefined, bcb: TipoCambioBcb | null): number | null {
  return propio && propio > 0 ? propio : bcb?.valor ?? null;
}
