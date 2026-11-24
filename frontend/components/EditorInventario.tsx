"use client";

/** Alta y edición de un producto del inventario, con fotos (docs/007-Agentes/08, sección 2). */
import { useState } from "react";
import { ImagePlus, Loader2, Lock, Plus, Trash2, X } from "lucide-react";
import Dialogo from "@/components/Dialogo";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";
import type { ProductoInventario, ProductoInventarioDatos } from "@/lib/api/inventario";
import { urlFoto } from "@/lib/api/inventario-url";
import {
  achicarFoto,
  borrarFotoInventario,
  crearProductoInventario,
  editarProductoInventario,
  eliminarProductoInventario,
  subirFotoInventario,
} from "@/lib/api/inventario-acciones";

interface Props {
  moneda: string;
  producto?: ProductoInventario;
  onCerrar: (cambio: boolean) => void;
}

const MAX_FOTOS = 6;

function aMonto(v: string): number | null | "invalido" {
  const limpio = v.trim().replace(",", ".");
  if (!limpio) return null;
  const n = Number(limpio);
  return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : "invalido";
}

const texto = (v: string | null | undefined) => v ?? "";

export default function EditorInventario({ moneda, producto, onCerrar }: Props) {
  const simbolo = moneda === "USD" ? "US$" : "Bs";
  const [nombre, setNombre] = useState(texto(producto?.nombre));
  const [sku, setSku] = useState(texto(producto?.sku));
  const [descripcion, setDescripcion] = useState(texto(producto?.descripcion));
  const [specs, setSpecs] = useState<[string, string][]>(Object.entries(producto?.especificaciones ?? {}));
  const [precio, setPrecio] = useState(texto(producto?.precio_venta));
  const [costo, setCosto] = useState(texto(producto?.costo_unitario));
  const [gastos, setGastos] = useState(texto(producto?.gastos_unitarios));
  const [stock, setStock] = useState(String(producto?.stock ?? 0));
  const [proveedor, setProveedor] = useState(texto(producto?.proveedor));
  const [notas, setNotas] = useState(texto(producto?.notas_internas));
  const [publicado, setPublicado] = useState(producto?.publicado ?? false);
  const [fotos, setFotos] = useState<string[]>(producto?.foto_ids ?? []);
  const [guardando, setGuardando] = useState(false);
  const [subiendo, setSubiendo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cambio, setCambio] = useState(false);

  async function guardar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const montos = { precio_venta: aMonto(precio), costo_unitario: aMonto(costo), gastos_unitarios: aMonto(gastos) };
    if (Object.values(montos).includes("invalido")) return setError("Revisá los montos: tienen que ser números positivos.");
    const unidades = Number(stock);
    if (!Number.isInteger(unidades) || unidades < 0) return setError("El stock tiene que ser un número entero, 0 o más.");
    const especificaciones = Object.fromEntries(specs.map(([k, v]) => [k.trim(), v.trim()]).filter(([k, v]) => k && v));
    const datos: ProductoInventarioDatos = {
      nombre: nombre.trim(),
      sku: sku.trim() || null,
      descripcion: descripcion.trim() || null,
      especificaciones,
      precio_venta: montos.precio_venta as number | null,
      costo_unitario: montos.costo_unitario as number | null,
      gastos_unitarios: montos.gastos_unitarios as number | null,
      stock: unidades,
      proveedor: proveedor.trim() || null,
      notas_internas: notas.trim() || null,
      publicado,
    };
    if (!datos.nombre) return setError("Poné el nombre del producto.");
    if (publicado && datos.precio_venta === null) return setError("Para publicarlo en el catálogo, poné un precio de venta.");
    setGuardando(true);
    try {
      if (producto) await editarProductoInventario(producto.id, datos);
      else await crearProductoInventario(datos);
      onCerrar(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo guardar. Probá de nuevo.");
      setGuardando(false);
    }
  }

  async function agregarFotos(archivos: FileList | null) {
    if (!producto || !archivos) return;
    setError(null);
    setSubiendo(true);
    try {
      for (const archivo of Array.from(archivos).slice(0, MAX_FOTOS - fotos.length)) {
        const foto = await subirFotoInventario(producto.id, await achicarFoto(archivo));
        setFotos((f) => [...f, foto.id]);
        setCambio(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo subir la foto.");
    } finally {
      setSubiendo(false);
    }
  }

  async function quitarFoto(fotoId: string) {
    if (!producto) return;
    try {
      await borrarFotoInventario(producto.id, fotoId);
      setFotos((f) => f.filter((id) => id !== fotoId));
      setCambio(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo borrar la foto.");
    }
  }

  async function eliminar() {
    if (!producto || !window.confirm(`¿Eliminar «${producto.nombre}» del inventario? También sale del catálogo público.`)) return;
    setGuardando(true);
    try {
      await eliminarProductoInventario(producto.id);
      onCerrar(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo eliminar.");
      setGuardando(false);
    }
  }

  const campo = (id: string, etiqueta: string, valor: string, cambiar: (v: string) => void, extra: React.InputHTMLAttributes<HTMLInputElement> = {}) => (
    <div>
      <label htmlFor={id} className={ETIQUETA_CAMPO}>{etiqueta}</label>
      <input id={id} value={valor} onChange={(e) => cambiar(e.target.value)} className={CAMPO} {...extra} />
    </div>
  );

  return (
    <Dialogo titulo={producto ? "Editar producto" : "Agregar producto"} onCerrar={() => onCerrar(cambio)}>
      <form onSubmit={guardar} className="space-y-5">
        <fieldset className="space-y-4">
          <legend className="mb-1 text-sm font-semibold text-texto">Lo que ven tus clientes (y la IA, si lo publicás)</legend>
          {campo("e-nombre", "Nombre", nombre, setNombre, { maxLength: 200, required: true })}
          <div>
            <label htmlFor="e-desc" className={ETIQUETA_CAMPO}>Descripción</label>
            <textarea id="e-desc" rows={3} maxLength={2000} value={descripcion} onChange={(e) => setDescripcion(e.target.value)} className={CAMPO} />
          </div>
          <div>
            <p className={ETIQUETA_CAMPO}>Especificaciones <span className="font-normal text-texto-3">(ej.: potencia → 800 W)</span></p>
            <ul className="space-y-2">
              {specs.map(([k, v], i) => (
                <li key={i} className="flex gap-2">
                  <input aria-label="Especificación" placeholder="Potencia" maxLength={60} value={k} onChange={(e) => setSpecs(specs.map((s, j) => (j === i ? [e.target.value, s[1]] : s)))} className={CAMPO} />
                  <input aria-label="Valor" placeholder="800 W" maxLength={200} value={v} onChange={(e) => setSpecs(specs.map((s, j) => (j === i ? [s[0], e.target.value] : s)))} className={CAMPO} />
                  <button type="button" onClick={() => setSpecs(specs.filter((_, j) => j !== i))} className="rounded-lg px-2 text-texto-2 hover:text-rojo" aria-label="Quitar especificación">
                    <X className="h-4 w-4" aria-hidden="true" />
                  </button>
                </li>
              ))}
            </ul>
            {specs.length < 20 && (
              <button type="button" onClick={() => setSpecs([...specs, ["", ""]])} className="mt-2 inline-flex items-center gap-1 text-sm text-acento-claro hover:text-texto">
                <Plus className="h-4 w-4" aria-hidden="true" /> Agregar especificación
              </button>
            )}
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {campo("e-precio", `Precio de venta (${simbolo})`, precio, setPrecio, { inputMode: "decimal" })}
            {campo("e-stock", "Stock (unidades que tenés)", stock, setStock, { inputMode: "numeric" })}
          </div>
          <label className="flex items-start gap-3 rounded-xl border border-borde bg-fondo p-3 text-sm">
            <input type="checkbox" checked={publicado} onChange={(e) => setPublicado(e.target.checked)} className="mt-0.5 h-4 w-4" />
            <span>
              <span className="font-medium text-texto">Publicar en el catálogo público</span>
              <span className="block text-texto-2">La IA lo va a poder ofrecer con este nombre, descripción, precio, fotos y cuántos hay disponibles.</span>
            </span>
          </label>
        </fieldset>

        <fieldset className="space-y-4 rounded-xl border border-borde p-4">
          <legend className="flex items-center gap-1.5 px-1 text-sm font-semibold text-texto">
            <Lock className="h-3.5 w-3.5 text-texto-2" aria-hidden="true" /> Solo para vos (la IA nunca lo ve)
          </legend>
          <div className="grid gap-4 sm:grid-cols-2">
            {campo("e-costo", `Costo por unidad (${simbolo})`, costo, setCosto, { inputMode: "decimal" })}
            {campo("e-gastos", `Gastos por unidad (${simbolo}) · envío, aduana…`, gastos, setGastos, { inputMode: "decimal" })}
            {campo("e-sku", "Código / SKU", sku, setSku, { maxLength: 60 })}
            {campo("e-prov", "Proveedor", proveedor, setProveedor, { maxLength: 200 })}
          </div>
          <div>
            <label htmlFor="e-notas" className={ETIQUETA_CAMPO}>Notas internas</label>
            <textarea id="e-notas" rows={2} maxLength={2000} value={notas} onChange={(e) => setNotas(e.target.value)} className={CAMPO} />
          </div>
        </fieldset>

        <div>
          <p className={ETIQUETA_CAMPO}>Fotos ({fotos.length}/{MAX_FOTOS})</p>
          {producto ? (
            <div className="flex flex-wrap gap-2">
              {fotos.map((id) => (
                <div key={id} className="group relative">
                  {/* eslint-disable-next-line @next/next/no-img-element -- foto privada servida por el BFF con sesión */}
                  <img src={urlFoto(id)} alt="" className="h-20 w-20 rounded-lg object-cover" />
                  <button type="button" onClick={() => quitarFoto(id)} className="absolute right-1 top-1 rounded-md bg-black/70 p-1 text-white" aria-label="Quitar foto">
                    <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                  </button>
                </div>
              ))}
              {fotos.length < MAX_FOTOS && (
                <label className="flex h-20 w-20 cursor-pointer flex-col items-center justify-center gap-1 rounded-lg border border-dashed border-borde-fuerte text-xs text-texto-2 hover:border-acento-borde hover:text-texto">
                  {subiendo ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> : <ImagePlus className="h-5 w-5" aria-hidden="true" />}
                  {subiendo ? "Subiendo" : "Agregar"}
                  <input type="file" accept="image/jpeg,image/png,image/webp" multiple className="sr-only" disabled={subiendo} onChange={(e) => agregarFotos(e.target.files)} />
                </label>
              )}
            </div>
          ) : (
            <p className="text-sm text-texto-2">Guardá el producto y después agregale las fotos.</p>
          )}
        </div>

        {error && <p role="alert" className="rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">{error}</p>}

        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-borde pt-4">
          {producto ? (
            <button type="button" onClick={eliminar} disabled={guardando} className="inline-flex items-center gap-1.5 text-sm text-rojo hover:underline disabled:opacity-50">
              <Trash2 className="h-4 w-4" aria-hidden="true" /> Eliminar
            </button>
          ) : <span />}
          <div className="flex gap-2">
            <button type="button" onClick={() => onCerrar(cambio)} className={BOTON_SECUNDARIO}>Cancelar</button>
            <button type="submit" disabled={guardando} className={BOTON_PRIMARIO}>
              {guardando && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
              Guardar
            </button>
          </div>
        </div>
      </form>
    </Dialogo>
  );
}
