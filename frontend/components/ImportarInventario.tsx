"use client";

/**
 * Importar un catálogo existente (docs/007-Agentes/08, sección 3.3).
 * Nunca guarda directo: muestra la vista previa y el dueño elige qué filas entran.
 */
import { useState } from "react";
import { AlertTriangle, FileSpreadsheet, Loader2 } from "lucide-react";
import Dialogo from "@/components/Dialogo";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO } from "@/components/ui/estilos";
import type { ImportarVistaPrevia } from "@/lib/api/inventario";
import { archivoABase64, confirmarImportacion, vistaPreviaImportacion } from "@/lib/api/inventario-acciones";
import { formatearPrecioLocal } from "@/lib/moneda";

const ETIQUETA_CAMPO: Record<string, string> = {
  nombre: "Nombre", sku: "Código", descripcion: "Descripción", precio_venta: "Precio de venta", costo_unitario: "Costo", stock: "Stock",
};
const MAX_BYTES = 750 * 1024;

export default function ImportarInventario({ moneda, onCerrar }: { moneda: string; onCerrar: (cambio: boolean) => void }) {
  const [vista, setVista] = useState<ImportarVistaPrevia | null>(null);
  const [elegidas, setElegidas] = useState<Record<number, boolean>>({});
  const [trabajando, setTrabajando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function leer(archivos: FileList | null) {
    const archivo = archivos?.[0];
    if (!archivo) return;
    setError(null);
    setVista(null);
    if (archivo.size > MAX_BYTES) return setError("El archivo es demasiado grande (máximo 750 KB). Si tiene fotos adentro, guardalo sin fotos.");
    setTrabajando(true);
    try {
      const r = await vistaPreviaImportacion(archivo.name, await archivoABase64(archivo));
      setVista(r);
      setElegidas(Object.fromEntries(r.filas.map((f) => [f.fila, true])));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No pudimos leer el archivo.");
    } finally {
      setTrabajando(false);
    }
  }

  async function confirmar() {
    if (!vista) return;
    const filas = vista.filas.filter((f) => elegidas[f.fila] && f.nombre);
    if (filas.length === 0) return setError("Elegí al menos un producto.");
    setTrabajando(true);
    try {
      await confirmarImportacion(
        filas.map((f) => ({
          nombre: f.nombre as string,
          sku: f.sku,
          descripcion: f.descripcion,
          precio_venta: f.precio_venta === null ? null : Number(f.precio_venta),
          costo_unitario: f.costo_unitario === null ? null : Number(f.costo_unitario),
          stock: f.stock ?? 0,
          publicado: false,
        }))
      );
      onCerrar(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo importar.");
      setTrabajando(false);
    }
  }

  const cantidad = vista ? vista.filas.filter((f) => elegidas[f.fila]).length : 0;

  return (
    <Dialogo
      titulo="Importar mi catálogo"
      descripcion="Subí tu lista en Excel (.xlsx) o CSV. Antes de guardar vas a ver lo que entendimos y elegir qué entra."
      onCerrar={() => onCerrar(false)}
      ancho="max-w-4xl"
    >
      {!vista && (
        <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-borde-fuerte px-6 py-10 text-center hover:border-acento-borde">
          {trabajando ? <Loader2 className="h-8 w-8 animate-spin text-acento-claro" aria-hidden="true" /> : <FileSpreadsheet className="h-8 w-8 text-acento-claro" aria-hidden="true" />}
          <span className="font-medium text-texto">{trabajando ? "Leyendo el archivo…" : "Elegí el archivo"}</span>
          <span className="text-sm text-texto-2">La primera fila tiene que tener los títulos (por ejemplo: Producto, Precio, Stock).</span>
          <span className="text-xs text-texto-3">PDF, Word y fotos de catálogos los va a leer la IA en la próxima versión.</span>
          <input type="file" accept=".xlsx,.csv,.txt,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" className="sr-only" disabled={trabajando} onChange={(e) => leer(e.target.files)} />
        </label>
      )}

      {vista && (
        <>
          <p className="mb-3 text-sm text-texto-2">
            Columnas que usamos:{" "}
            {Object.entries(vista.columnas).filter(([, c]) => c).map(([campo, c]) => `${ETIQUETA_CAMPO[campo]} ← «${c}»`).join(" · ")}
          </p>
          {vista.descartadas > 0 && (
            <p className="mb-3 text-sm text-ambar">{vista.descartadas} filas no se van a importar (sin nombre o más de 500 filas).</p>
          )}
          <div className="overflow-x-auto rounded-xl border border-borde">
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="border-b border-borde text-left text-xs text-texto-2">
                  <th scope="col" className="px-3 py-2"><span className="sr-only">Importar</span></th>
                  <th scope="col" className="px-3 py-2 font-medium">Producto</th>
                  <th scope="col" className="px-3 py-2 text-right font-medium">Precio</th>
                  <th scope="col" className="px-3 py-2 text-right font-medium">Costo</th>
                  <th scope="col" className="px-3 py-2 text-right font-medium">Stock</th>
                  <th scope="col" className="px-3 py-2 font-medium">Revisar</th>
                </tr>
              </thead>
              <tbody>
                {vista.filas.map((f) => (
                  <tr key={f.fila} className="border-b border-borde last:border-0">
                    <td className="px-3 py-2">
                      <input type="checkbox" aria-label={`Importar ${f.nombre}`} checked={Boolean(elegidas[f.fila])} onChange={(e) => setElegidas({ ...elegidas, [f.fila]: e.target.checked })} className="h-4 w-4" />
                    </td>
                    <td className="px-3 py-2 text-texto">{f.nombre}{f.sku && <span className="block text-xs text-texto-3">{f.sku}</span>}</td>
                    <td className="px-3 py-2 text-right tabular-nums">{f.precio_venta === null ? "—" : formatearPrecioLocal(f.precio_venta, moneda)}</td>
                    <td className="px-3 py-2 text-right tabular-nums text-texto-2">{f.costo_unitario === null ? "—" : formatearPrecioLocal(f.costo_unitario, moneda)}</td>
                    <td className="px-3 py-2 text-right tabular-nums">{f.stock ?? "—"}</td>
                    <td className="px-3 py-2 text-xs text-ambar">
                      {f.problemas.map((p) => (
                        <span key={p} className="flex items-start gap-1"><AlertTriangle className="mt-0.5 h-3 w-3 shrink-0" aria-hidden="true" />{p}</span>
                      ))}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-texto-3">
            Se importan como <strong>ocultos</strong>: revisalos y publicá los que quieras que la IA ofrezca. Lo que no pudimos leer queda vacío, nunca inventado.
          </p>
        </>
      )}

      {error && <p role="alert" className="mt-4 rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">{error}</p>}

      <div className="mt-5 flex justify-end gap-2 border-t border-borde pt-4">
        {vista && <button type="button" onClick={() => setVista(null)} className={BOTON_SECUNDARIO}>Elegir otro archivo</button>}
        <button type="button" onClick={() => onCerrar(false)} className={BOTON_SECUNDARIO}>Cancelar</button>
        {vista && (
          <button type="button" onClick={confirmar} disabled={trabajando || cantidad === 0} className={BOTON_PRIMARIO}>
            {trabajando && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
            Importar {cantidad} {cantidad === 1 ? "producto" : "productos"}
          </button>
        )}
      </div>
    </Dialogo>
  );
}
