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
  destino?: string; // a dónde ir después de guardar
  textoBoton?: string;
}

function numero(valor: string): number | null {
  const n = Number(valor.replace(",", "."));
  return valor.trim() === "" || !Number.isFinite(n) ? null : n;
}

export default function FormularioPerfil({ organizacion, destino, textoBoton = "Guardar" }: FormularioPerfilProps) {
  const router = useRouter();
  const [nombre, setNombre] = useState(organizacion.nombre);
  const [pais, setPais] = useState(organizacion.pais || "BO");
  const [rubro, setRubro] = useState(organizacion.rubro ?? "");
  const [presupuesto, setPresupuesto] = useState(organizacion.presupuesto_mensual?.toString() ?? "");
  const [moneda, setMoneda] = useState<"BOB" | "USD">(organizacion.moneda);
  const [tipoCambio, setTipoCambio] = useState(organizacion.tipo_cambio?.toString() ?? "");
  const [envio, setEnvio] = useState(organizacion.costo_envio_unitario_usd.toString());
  const [impuestos, setImpuestos] = useState(organizacion.impuestos_importacion_pct.toString());
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [listo, setListo] = useState(false);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setGuardando(true);
    try {
      await guardarPerfil({
        nombre: nombre.trim(),
        pais,
        rubro: rubro.trim(),
        presupuesto_mensual: numero(presupuesto),
        moneda,
        tipo_cambio: numero(tipoCambio),
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
      <div>
        <label htmlFor="p-cambio" className={ETIQUETA_CAMPO}>
          Tipo de cambio propio (Bs por 1 US$)
        </label>
        <input id="p-cambio" inputMode="decimal" placeholder="Vacío = dólar oficial del BCB (automático)" value={tipoCambio} onChange={(e) => setTipoCambio(e.target.value)} className={CAMPO} />
        <p className="mt-1 text-xs text-texto-3">Dejalo vacío para usar el oficial del BCB, que se actualiza solo.</p>
      </div>
      <div>
        <label htmlFor="p-presupuesto" className={ETIQUETA_CAMPO}>Presupuesto mensual para comprar mercadería ({moneda === "BOB" ? "Bs" : "US$"}) · opcional</label>
        <input id="p-presupuesto" inputMode="decimal" value={presupuesto} onChange={(e) => setPresupuesto(e.target.value)} className={CAMPO} />
      </div>
      <div>
        <label htmlFor="p-envio" className={ETIQUETA_CAMPO}>Envío por unidad (US$) · para el margen</label>
        <input id="p-envio" inputMode="decimal" value={envio} onChange={(e) => setEnvio(e.target.value)} className={CAMPO} />
      </div>
      <div>
        <label htmlFor="p-impuestos" className={ETIQUETA_CAMPO}>Impuestos de importación (%) · para el margen</label>
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
