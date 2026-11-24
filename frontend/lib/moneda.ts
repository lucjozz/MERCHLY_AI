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

/** Supuestos de la aduana boliviana (docs/004-Backend/05, sección 1). Estimaciones. */
export const ADUANA_BO = {
  seguroPresuntoPct: 2, // sobre el FOB, cuando no hay póliza
  ivaImportacionPct: 14.94, // 13 % de IVA calculado "por dentro"
  gravamenPorDefectoPct: 10,
} as const;

export interface EntradaCostoBolivia {
  fobUsd: number; // precio del proveedor
  fleteUsd: number; // envío por unidad
  gravamenPct: number; // GA según la partida arancelaria
  gastosLocalesUsd: number; // despachante, transporte interno, etc.
  comisionCobroPct: number; // QR, Tigo Money, tarjeta (sobre el precio)
  precioVentaUsd: number;
}

export interface CostoBolivia {
  seguroUsd: number;
  cifUsd: number;
  gravamenUsd: number;
  ivaUsd: number;
  costoPuestoUsd: number; // CIF + GA + IVA + gastos locales
  comisionUsd: number;
  gananciaUsd: number;
  margenPct: number;
}

/** Costo real puesto en Bolivia y margen por unidad. Null si algún dato es inválido. */
export function calcularCostoBolivia(e: EntradaCostoBolivia): CostoBolivia | null {
  const valores = [e.fobUsd, e.fleteUsd, e.gravamenPct, e.gastosLocalesUsd, e.comisionCobroPct, e.precioVentaUsd];
  if (valores.some((v) => !Number.isFinite(v) || v < 0)) return null;
  if (e.precioVentaUsd <= 0 || e.gravamenPct > 100 || e.comisionCobroPct > 100) return null;
  const seguroUsd = e.fobUsd * (ADUANA_BO.seguroPresuntoPct / 100);
  const cifUsd = e.fobUsd + e.fleteUsd + seguroUsd;
  const gravamenUsd = cifUsd * (e.gravamenPct / 100);
  const ivaUsd = (cifUsd + gravamenUsd) * (ADUANA_BO.ivaImportacionPct / 100);
  const costoPuestoUsd = cifUsd + gravamenUsd + ivaUsd + e.gastosLocalesUsd;
  const comisionUsd = e.precioVentaUsd * (e.comisionCobroPct / 100);
  const gananciaUsd = e.precioVentaUsd - costoPuestoUsd - comisionUsd;
  return {
    seguroUsd,
    cifUsd,
    gravamenUsd,
    ivaUsd,
    costoPuestoUsd,
    comisionUsd,
    gananciaUsd,
    margenPct: (gananciaUsd / e.precioVentaUsd) * 100,
  };
}

/** Monto ya expresado en la moneda del negocio (inventario): "Bs 450,00". Acepta el string decimal del backend. */
export function formatearPrecioLocal(valor: string | number | null | undefined, moneda: string): string {
  if (valor === null || valor === undefined || valor === "") return "Sin precio";
  const n = typeof valor === "number" ? valor : Number(valor);
  if (!Number.isFinite(n)) return "Sin precio";
  return (moneda === "USD" ? USD : BOB).format(n);
}
