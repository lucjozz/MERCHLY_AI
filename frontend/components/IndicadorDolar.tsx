import Link from "next/link";
import { cookies } from "next/headers";
import { DollarSign } from "lucide-react";
import { COOKIE_ACCESS } from "@/lib/sesion/config";
import { obtenerOrganizacion, type Organizacion } from "@/lib/api/organizacion";
import { obtenerTipoCambioBcb } from "@/lib/api/tipo-cambio";

function fecha(iso: string | null): string {
  return iso ? iso.slice(0, 10).split("-").reverse().join("/") : "";
}

function bs(valor: number): string {
  return `Bs ${valor.toLocaleString("es-BO", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/**
 * Dólar del día siempre visible (DEC-035): el oficial del BCB y, si el negocio
 * usa uno propio, cuál se está usando para sus precios.
 */
export default async function IndicadorDolar() {
  if (!(await cookies()).get(COOKIE_ACCESS)) return null; // pantallas públicas: nada
  const [bcb, organizacion] = await Promise.all([
    obtenerTipoCambioBcb(),
    obtenerOrganizacion().catch((): Organizacion | null => null),
  ]);
  if (!bcb) return null;

  const usaPropio = organizacion?.moneda === "BOB" && organizacion.tipo_cambio;

  return (
    <div className="mb-4 flex justify-end">
      <div className="inline-flex flex-wrap items-center gap-x-3 gap-y-1 rounded-full border border-borde bg-superficie px-3 py-1.5 text-xs text-texto-2">
        <span className="inline-flex items-center gap-1.5">
          <DollarSign className="h-3.5 w-3.5 text-verde" aria-hidden="true" />
          Dólar oficial BCB: <span className="font-semibold tabular-nums text-texto">{bs(bcb.valor)}</span>
          {bcb.fecha && <span className="text-texto-3">· {fecha(bcb.fecha)}</span>}
          {bcb.desactualizado && <span className="text-ambar">· puede estar desactualizado</span>}
        </span>
        {usaPropio && (
          <Link href="/configuracion#tu-negocio" className="text-ambar hover:underline">
            Tus precios usan {bs(Number(organizacion!.tipo_cambio))} (propio) · cambiar
          </Link>
        )}
      </div>
    </div>
  );
}
