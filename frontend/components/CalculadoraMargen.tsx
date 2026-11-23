"use client";

/**
 * Margen real por unidad: costo del proveedor + envío + impuestos de
 * importación, comparado con el precio de venta (docs/004-Backend/03, sección 4).
 * Los valores iniciales salen de la IA y del perfil del negocio; la persona
 * los ajusta con sus números reales.
 */
import { useState } from "react";
import { Calculator } from "lucide-react";
import { calcularMargen, formatearMonto, usaBolivianos, type ConfigMoneda } from "@/lib/moneda";
import { CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";

interface CalculadoraMargenProps {
  costoUsd: number | null;
  precioUsd: number | null;
  envioUsd: number;
  impuestosPct: number;
  moneda: ConfigMoneda;
}

function aNumero(v: string): number {
  return Number(v.replace(",", "."));
}

export default function CalculadoraMargen({ costoUsd, precioUsd, envioUsd, impuestosPct, moneda }: CalculadoraMargenProps) {
  const enBs = usaBolivianos(moneda);
  const factor = enBs ? (moneda.tipo_cambio as number) : 1;
  const simbolo = enBs ? "Bs" : "US$";
  const inicial = (usd: number | null) => (usd === null ? "" : (usd * factor).toFixed(2));

  const [costo, setCosto] = useState(inicial(costoUsd));
  const [envio, setEnvio] = useState(inicial(envioUsd));
  const [impuestos, setImpuestos] = useState(String(impuestosPct));
  const [precio, setPrecio] = useState(inicial(precioUsd));

  const margen = calcularMargen(aNumero(costo || "0") / factor, aNumero(envio || "0") / factor, aNumero(impuestos || "0"), aNumero(precio || "0") / factor);
  const campos: [string, string, (v: string) => void, string][] = [
    ["Te cuesta en el proveedor", costo, setCosto, simbolo],
    ["Envío por unidad", envio, setEnvio, simbolo],
    ["Impuestos de importación", impuestos, setImpuestos, "%"],
    ["Precio al que vendés", precio, setPrecio, simbolo],
  ];

  return (
    <div className="rounded-2xl border border-borde bg-superficie p-5">
      <p className="flex items-center gap-2 font-semibold text-texto">
        <Calculator className="h-4 w-4 text-acento-claro" aria-hidden="true" />
        ¿Cuánto ganás por unidad?
      </p>
      <p className="mt-1 text-sm text-texto-2">Ajustá con tus números reales. Los valores iniciales son estimaciones.</p>
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {campos.map(([etiqueta, valor, cambiar, unidad], i) => (
          <div key={etiqueta}>
            <label htmlFor={`m-${i}`} className={`${ETIQUETA_CAMPO} text-xs`}>{etiqueta} ({unidad})</label>
            <input id={`m-${i}`} inputMode="decimal" value={valor} onChange={(e) => cambiar(e.target.value)} className={CAMPO} />
          </div>
        ))}
      </div>
      {margen ? (
        <div className="mt-4 grid grid-cols-3 gap-3 text-center">
          <div className="rounded-xl bg-fondo p-3">
            <p className="text-xs text-texto-2">Costo total</p>
            <p className="font-semibold tabular-nums text-texto">{formatearMonto(margen.costoTotalUsd, moneda)}</p>
          </div>
          <div className="rounded-xl bg-fondo p-3">
            <p className="text-xs text-texto-2">Ganancia</p>
            <p className={`font-semibold tabular-nums ${margen.gananciaUsd > 0 ? "text-verde" : "text-rojo"}`}>{formatearMonto(margen.gananciaUsd, moneda)}</p>
          </div>
          <div className="rounded-xl bg-fondo p-3">
            <p className="text-xs text-texto-2">Margen</p>
            <p className={`font-semibold tabular-nums ${margen.margenPct >= 20 ? "text-verde" : margen.margenPct > 0 ? "text-ambar" : "text-rojo"}`}>{margen.margenPct.toFixed(0)}%</p>
          </div>
        </div>
      ) : (
        <p className="mt-4 text-sm text-texto-2">Cargá el precio de venta para ver el margen.</p>
      )}
      {!enBs && moneda.moneda === "BOB" && (
        <p className="mt-3 text-xs text-ambar">Para ver todo en bolivianos, cargá tu tipo de cambio en Configuración.</p>
      )}
    </div>
  );
}
