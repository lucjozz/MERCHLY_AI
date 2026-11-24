"use client";

/**
 * Margen real por unidad (docs/004-Backend/05, sección 1).
 * Si el negocio vende en Bolivia, desglosa el costo puesto acá: FOB, flete,
 * seguro presunto, gravamen arancelario, IVA de importación, gastos locales y
 * comisión de cobro. En otros países usa el cálculo simple (un % de impuestos).
 * Los valores iniciales salen de la IA y del perfil del negocio; la persona
 * los ajusta con sus números reales. Nada de esto se guarda.
 */
import { useState } from "react";
import { Calculator } from "lucide-react";
import {
  ADUANA_BO,
  calcularCostoBolivia,
  calcularMargen,
  formatearMonto,
  usaBolivianos,
  type ConfigMoneda,
} from "@/lib/moneda";
import { CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";

interface CalculadoraMargenProps {
  costoUsd: number | null;
  precioUsd: number | null;
  envioUsd: number;
  impuestosPct: number;
  moneda: ConfigMoneda;
  pais?: string;
}

function aNumero(v: string): number {
  return Number(v.replace(",", "."));
}

type Campo = [etiqueta: string, valor: string, cambiar: (v: string) => void, unidad: string];

function Campos({ campos }: { campos: Campo[] }) {
  return (
    <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
      {campos.map(([etiqueta, valor, cambiar, unidad], i) => (
        <div key={etiqueta}>
          <label htmlFor={`m-${i}`} className={`${ETIQUETA_CAMPO} text-xs`}>{etiqueta} ({unidad})</label>
          <input id={`m-${i}`} inputMode="decimal" value={valor} onChange={(e) => cambiar(e.target.value)} className={CAMPO} />
        </div>
      ))}
    </div>
  );
}

function Resultado({ costoUsd, gananciaUsd, margenPct, moneda, etiquetaCosto }: {
  costoUsd: number; gananciaUsd: number; margenPct: number; moneda: ConfigMoneda; etiquetaCosto: string;
}) {
  return (
    <div className="mt-4 grid grid-cols-3 gap-3 text-center">
      <div className="rounded-xl bg-fondo p-3">
        <p className="text-xs text-texto-2">{etiquetaCosto}</p>
        <p className="font-semibold tabular-nums text-texto">{formatearMonto(costoUsd, moneda)}</p>
      </div>
      <div className="rounded-xl bg-fondo p-3">
        <p className="text-xs text-texto-2">Ganancia</p>
        <p className={`font-semibold tabular-nums ${gananciaUsd > 0 ? "text-verde" : "text-rojo"}`}>{formatearMonto(gananciaUsd, moneda)}</p>
      </div>
      <div className="rounded-xl bg-fondo p-3">
        <p className="text-xs text-texto-2">Margen</p>
        <p className={`font-semibold tabular-nums ${margenPct >= 20 ? "text-verde" : margenPct > 0 ? "text-ambar" : "text-rojo"}`}>{margenPct.toFixed(0)}%</p>
      </div>
    </div>
  );
}

export default function CalculadoraMargen({ costoUsd, precioUsd, envioUsd, impuestosPct, moneda, pais }: CalculadoraMargenProps) {
  const bolivia = pais === "BO";
  const enBs = usaBolivianos(moneda);
  const factor = enBs ? (moneda.tipo_cambio as number) : 1;
  const simbolo = enBs ? "Bs" : "US$";
  const inicial = (usd: number | null) => (usd === null ? "" : (usd * factor).toFixed(2));

  const [costo, setCosto] = useState(inicial(costoUsd));
  const [envio, setEnvio] = useState(inicial(envioUsd));
  const [impuestos, setImpuestos] = useState(
    String(bolivia && !(impuestosPct > 0) ? ADUANA_BO.gravamenPorDefectoPct : impuestosPct)
  );
  const [gastos, setGastos] = useState("0");
  const [comision, setComision] = useState("0");
  const [precio, setPrecio] = useState(inicial(precioUsd));

  const usd = (v: string) => aNumero(v || "0") / factor;
  const pct = (v: string) => aNumero(v || "0");

  const desglose = bolivia
    ? calcularCostoBolivia({
        fobUsd: usd(costo),
        fleteUsd: usd(envio),
        gravamenPct: pct(impuestos),
        gastosLocalesUsd: usd(gastos),
        comisionCobroPct: pct(comision),
        precioVentaUsd: usd(precio),
      })
    : null;
  const simple = bolivia ? null : calcularMargen(usd(costo), usd(envio), pct(impuestos), usd(precio));

  const campos: Campo[] = bolivia
    ? [
        ["Precio del proveedor (FOB)", costo, setCosto, simbolo],
        ["Flete por unidad", envio, setEnvio, simbolo],
        ["Gravamen arancelario", impuestos, setImpuestos, "%"],
        ["Despachante y transporte local", gastos, setGastos, simbolo],
        ["Comisión de cobro (QR, tarjeta)", comision, setComision, "%"],
        ["Precio al que vendés", precio, setPrecio, simbolo],
      ]
    : [
        ["Te cuesta en el proveedor", costo, setCosto, simbolo],
        ["Envío por unidad", envio, setEnvio, simbolo],
        ["Impuestos de importación", impuestos, setImpuestos, "%"],
        ["Precio al que vendés", precio, setPrecio, simbolo],
      ];

  const filas: [string, number][] = desglose
    ? [
        [`Seguro presunto (${ADUANA_BO.seguroPresuntoPct} % del FOB)`, desglose.seguroUsd],
        ["Valor CIF (FOB + flete + seguro)", desglose.cifUsd],
        [`Gravamen arancelario (${pct(impuestos)} % del CIF)`, desglose.gravamenUsd],
        [`IVA de importación (${ADUANA_BO.ivaImportacionPct.toString().replace(".", ",")} %)`, desglose.ivaUsd],
        ["Comisión de cobro", desglose.comisionUsd],
      ]
    : [];

  return (
    <div className="rounded-2xl border border-borde bg-superficie p-5">
      <p className="flex items-center gap-2 font-semibold text-texto">
        <Calculator className="h-4 w-4 text-acento-claro" aria-hidden="true" />
        {bolivia ? "¿Cuánto te cuesta puesto en Bolivia?" : "¿Cuánto ganás por unidad?"}
      </p>
      <p className="mt-1 text-sm text-texto-2">
        {bolivia
          ? "Incluye la aduana boliviana. Ajustá con tus números reales: los valores iniciales son estimaciones."
          : "Ajustá con tus números reales. Los valores iniciales son estimaciones."}
      </p>

      <Campos campos={campos} />

      {desglose && (
        <>
          <dl className="mt-4 space-y-1.5 rounded-xl bg-fondo p-3 text-sm">
            {filas.map(([etiqueta, valor]) => (
              <div key={etiqueta} className="flex justify-between gap-3">
                <dt className="text-texto-2">{etiqueta}</dt>
                <dd className="tabular-nums text-texto">{formatearMonto(valor, moneda)}</dd>
              </div>
            ))}
          </dl>
          <Resultado costoUsd={desglose.costoPuestoUsd} gananciaUsd={desglose.gananciaUsd} margenPct={desglose.margenPct} moneda={moneda} etiquetaCosto="Costo puesto" />
          <p className="mt-3 text-xs text-texto-3">
            El gravamen depende de la partida arancelaria del producto (de 0 % a 40 %). Confirmalo con tu despachante antes de comprar.
          </p>
        </>
      )}
      {simple && (
        <Resultado costoUsd={simple.costoTotalUsd} gananciaUsd={simple.gananciaUsd} margenPct={simple.margenPct} moneda={moneda} etiquetaCosto="Costo total" />
      )}
      {!desglose && !simple && <p className="mt-4 text-sm text-texto-2">Cargá el precio de venta para ver el margen.</p>}

      {!enBs && moneda.moneda === "BOB" && (
        <p className="mt-3 text-xs text-ambar">No pudimos obtener el dólar del BCB ahora: los montos se muestran en dólares.</p>
      )}
    </div>
  );
}
