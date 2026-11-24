"use client";

/** Perfil del negocio: onboarding y Configuración (docs/004-Backend/03, secciones 3 y 4). */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Save } from "lucide-react";
import { guardarPerfil } from "@/lib/api/acciones";
import type { Organizacion } from "@/lib/api/organizacion";
import { MERCADOS } from "@/lib/etiquetas";
import { BOTON_PRIMARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";

interface FormularioPerfilProps {
  organizacion: Organizacion;
  /** Dólar oficial del BCB de hoy, para mostrarlo en la elección. */
  dolarBcb?: number | null;
  destino?: string; // a dónde ir después de guardar
  textoBoton?: string;
}

function numero(valor: string): number | null {
  const n = Number(valor.replace(",", "."));
  return valor.trim() === "" || !Number.isFinite(n) ? null : n;
}

export default function FormularioPerfil({ organizacion, dolarBcb = null, destino, textoBoton = "Guardar" }: FormularioPerfilProps) {
  const router = useRouter();
  const [nombre, setNombre] = useState(organizacion.nombre);
  const [pais, setPais] = useState(organizacion.pais || "BO");
  const [rubro, setRubro] = useState(organizacion.rubro ?? "");
  const [presupuesto, setPresupuesto] = useState(organizacion.presupuesto_mensual?.toString() ?? "");
  const [moneda, setMoneda] = useState<"BOB" | "USD">(organizacion.moneda);
  const [tipoCambio, setTipoCambio] = useState(organizacion.tipo_cambio?.toString() ?? "");
  const [modoCambio, setModoCambio] = useState<"bcb" | "propio">(organizacion.tipo_cambio ? "propio" : "bcb");
  const [envio, setEnvio] = useState(organizacion.costo_envio_unitario_usd.toString());
  const [impuestos, setImpuestos] = useState(organizacion.impuestos_importacion_pct.toString());
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [listo, setListo] = useState(false);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (moneda === "BOB" && modoCambio === "propio" && !numero(tipoCambio)) {
      setError("Escribí tu tipo de cambio o elegí el oficial del BCB.");
      return;
    }
    setGuardando(true);
    try {
      await guardarPerfil({
        nombre: nombre.trim(),
        pais,
        rubro: rubro.trim(),
        presupuesto_mensual: numero(presupuesto),
        moneda,
        // Automático = sin valor propio: se usa el dólar oficial del BCB del día.
        tipo_cambio: modoCambio === "propio" ? numero(tipoCambio) : null,
        costo_envio_unitario_usd: numero(envio) ?? 0,
        impuestos_importacion_pct: numero(impuestos) ?? 0,
      });
      setListo(true);
      if (destino) router.push(destino);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar.");
    } finally {
      setGuardando(false);
    }
  }

  return (
    <form onSubmit={enviar} className="grid gap-5 sm:grid-cols-2">
      <div className="sm:col-span-2">
        <label htmlFor="p-nombre" className={ETIQUETA_CAMPO}>Nombre de tu negocio</label>
        <input id="p-nombre" required minLength={2} maxLength={120} value={nombre} onChange={(e) => setNombre(e.target.value)} className={CAMPO} />
      </div>
      <div>
        <label htmlFor="p-rubro" className={ETIQUETA_CAMPO}>¿Qué vendés o querés vender?</label>
        <input id="p-rubro" required minLength={2} maxLength={120} placeholder="Ej.: ropa deportiva, accesorios para celulares" value={rubro} onChange={(e) => setRubro(e.target.value)} className={CAMPO} />
      </div>
      <div>
        <label htmlFor="p-pais" className={ETIQUETA_CAMPO}>País donde vendés</label>
        <select id="p-pais" value={pais} onChange={(e) => setPais(e.target.value)} className={CAMPO}>
          {Object.entries(MERCADOS).map(([codigo, m]) => (
            <option key={codigo} value={codigo}>{m.nombre}</option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="p-moneda" className={ETIQUETA_CAMPO}>Moneda para ver los precios</label>
        <select id="p-moneda" value={moneda} onChange={(e) => setMoneda(e.target.value as "BOB" | "USD")} className={CAMPO}>
          <option value="BOB">Bolivianos (Bs)</option>
          <option value="USD">Dólares (US$)</option>
        </select>
      </div>
      {moneda === "BOB" && (
        <fieldset className="sm:col-span-2">
          <legend className={ETIQUETA_CAMPO}>¿Qué dólar usamos para tus precios?</legend>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className={`flex cursor-pointer gap-3 rounded-xl border p-4 text-sm ${modoCambio === "bcb" ? "border-acento bg-acento-hondo/30" : "border-borde"}`}>
              <input type="radio" name="modo-cambio" checked={modoCambio === "bcb"} onChange={() => setModoCambio("bcb")} className="mt-1" />
              <span>
                <span className="block font-medium text-texto">
                  Oficial del BCB{dolarBcb ? ` · hoy Bs ${dolarBcb.toLocaleString("es-BO")}` : ""}
                </span>
                <span className="text-xs text-texto-2">Se actualiza solo todos los días.</span>
              </span>
            </label>
            <label className={`flex cursor-pointer gap-3 rounded-xl border p-4 text-sm ${modoCambio === "propio" ? "border-acento bg-acento-hondo/30" : "border-borde"}`}>
              <input type="radio" name="modo-cambio" checked={modoCambio === "propio"} onChange={() => setModoCambio("propio")} className="mt-1" />
              <span className="flex-1">
                <span className="block font-medium text-texto">El que pago yo</span>
                <span className="text-xs text-texto-2">Fijo, hasta que lo cambies.</span>
                {modoCambio === "propio" && (
                  <input
                    id="p-cambio"
                    inputMode="decimal"
                    aria-label="Tipo de cambio propio (Bs por 1 US$)"
                    placeholder="Bs por 1 US$"
                    value={tipoCambio}
                    onChange={(e) => setTipoCambio(e.target.value)}
                    className={`${CAMPO} mt-2`}
                  />
                )}
              </span>
            </label>
          </div>
        </fieldset>
      )}
      <div>
        <label htmlFor="p-presupuesto" className={ETIQUETA_CAMPO}>Presupuesto mensual para comprar mercadería ({moneda === "BOB" ? "Bs" : "US$"}) · opcional</label>
        <input id="p-presupuesto" inputMode="decimal" value={presupuesto} onChange={(e) => setPresupuesto(e.target.value)} className={CAMPO} />
      </div>
      <div>
        <label htmlFor="p-envio" className={ETIQUETA_CAMPO}>Envío por unidad (US$) · para el margen</label>
        <input id="p-envio" inputMode="decimal" value={envio} onChange={(e) => setEnvio(e.target.value)} className={CAMPO} />
      </div>
      <div>
        <label htmlFor="p-impuestos" className={ETIQUETA_CAMPO}>{pais === "BO" ? "Gravamen arancelario (%) · el IVA de importación se suma solo" : "Impuestos de importación (%) · para el margen"}</label>
        <input id="p-impuestos" inputMode="decimal" value={impuestos} onChange={(e) => setImpuestos(e.target.value)} className={CAMPO} />
      </div>
      {error && <p role="alert" className="sm:col-span-2 rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">{error}</p>}
      {listo && !destino && <p role="status" className="sm:col-span-2 text-sm text-verde">Guardado.</p>}
      <div className="sm:col-span-2">
        <button type="submit" disabled={guardando} className={`px-6 py-3 ${BOTON_PRIMARIO}`}>
          <Save className="h-4 w-4" aria-hidden="true" />
          {guardando ? "Guardando…" : textoBoton}
        </button>
      </div>
    </form>
  );
}
