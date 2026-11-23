/** Perfil del negocio y uso del plan, desde Server Components. */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";

export interface Organizacion {
  id: string;
  nombre: string;
  plan: "beta" | "emprendedor" | "negocio";
  pais: string;
  rubro: string | null;
  presupuesto_mensual: number | null;
  moneda: "BOB" | "USD";
  tipo_cambio: number | null;
  costo_envio_unitario_usd: number;
  impuestos_importacion_pct: number;
  onboarding_completo: boolean;
}

export interface UsoCuota {
  agente: "investigador" | "marketing";
  limite_por_hora: number;
  usadas: number;
  restantes: number;
  se_renueva_en_segundos: number;
}

export interface UsoPlan {
  plan: string;
  cuotas: UsoCuota[];
  disponible: boolean;
}

export async function obtenerOrganizacion(): Promise<Organizacion> {
  const r = await fetchAutenticadoServidor("/organizacion");
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}

export async function obtenerUsoPlan(): Promise<UsoPlan> {
  const r = await fetchAutenticadoServidor("/organizacion/uso");
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}
