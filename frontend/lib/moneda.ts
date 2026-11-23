/**
 * Precios en la moneda del negocio y margen real (docs/004-Backend/03, sección 4).
 * La IA trabaja en USD; la conversión usa el tipo de cambio que cargó el
 * admin del negocio. Si no hay tipo de cambio, se muestra en USD (nunca un
 * valor inventado).
 */

export interface ConfigMoneda {
  moneda: string; // "BOB" | "USD"
  tipo_cambio: number | null; // Bs por 1 USD
}

const USD = new Intl.NumberFormat("es-BO", { style: "currency", currency: "USD", maximumFractionDigits: 2 });
const BOB = new Intl.NumberFormat("es-BO", { style: "currency", currency: "BOB", maximumFractionDigits: 2 });

export function usaBolivianos(config?: ConfigMoneda | null): boolean {
  return Boolean(config && config.moneda === "BOB" && config.tipo_cambio && config.tipo_cambio > 0);
}

/** "Bs 139,20" (si hay tipo de cambio) o "US$ 20,00". */
export function formatearMonto(usd: number | null | undefined, config?: ConfigMoneda | null): string {
  if (usd === null || usd === undefined || Number.isNaN(usd)) return "Sin dato";
  if (usaBolivianos(config)) return BOB.format(usd * (config!.tipo_cambio as number));
  return USD.format(usd);
}

/** Texto secundario con el valor en USD cuando se muestra en bolivianos. */
export function equivalenteUsd(usd: number | null | undefined, config?: ConfigMoneda | null): string | null {
  if (usd === null || usd === undefined || !usaBolivianos(config)) return null;
  return USD.format(usd);
}

export interface Margen {
  costoTotalUsd: number;
  gananciaUsd: number;
  margenPct: number;
}

/** Costo real por unidad = proveedor + envío + impuestos de importación sobre (proveedor + envío). */
export function calcularMargen(
  costoProveedorUsd: number,
  envioUsd: number,
  impuestosPct: number,
  precioVentaUsd: number
): Margen | null {
  if ([costoProveedorUsd, envioUsd, impuestosPct, precioVentaUsd].some((v) => !Number.isFinite(v) || v < 0)) return null;
  if (precioVentaUsd <= 0) return null;
  const base = costoProveedorUsd + envioUsd;
  const costoTotalUsd = base * (1 + impuestosPct / 100);
  const gananciaUsd = precioVentaUsd - costoTotalUsd;
  return { costoTotalUsd, gananciaUsd, margenPct: (gananciaUsd / precioVentaUsd) * 100 };
}
