"use client";

/**
 * Inventario privado del dueño (docs/007-Agentes/08, sección 2): costos, gastos,
 * stock real y margen. "Publicado" decide qué pasa al catálogo público de la IA.
 */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Boxes, CircleSlash, Eye, ImageOff, Package, Pencil, Plus, Search, Upload, Wallet } from "lucide-react";
import Metrica from "@/components/ui/Metrica";
import Badge from "@/components/ui/Badge";
import EmptyState from "@/components/ui/EmptyState";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO, CAMPO } from "@/components/ui/estilos";
import EditorInventario from "@/components/EditorInventario";
import ImportarInventario from "@/components/ImportarInventario";
import type { InventarioListado, ProductoInventario } from "@/lib/api/inventario";
import { urlFoto } from "@/lib/api/inventario-url";
import { formatearPrecioLocal } from "@/lib/moneda";

interface Props {
  listado: InventarioListado;
  moneda: string;
  puedeEditar: boolean;
  buscar: string;
}

type Modo = { tipo: "nuevo" } | { tipo: "editar"; producto: ProductoInventario } | { tipo: "importar" } | null;

export default function PanelInventario({ listado, moneda, puedeEditar, buscar }: Props) {
  const router = useRouter();
  const [modo, setModo] = useState<Modo>(null);
  const { resumen, productos } = listado;
  const precio = (v: string | null) => formatearPrecioLocal(v, moneda);

  function cerrar(cambio: boolean) {
    setModo(null);
    if (cambio) router.refresh();
  }

  return (
    <>
      <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Metrica etiqueta="Productos" valor={resumen.productos} icono={Package} color="azul" detalle={`${resumen.publicados} publicados`} />
        <Metrica etiqueta="Unidades en stock" valor={resumen.unidades} icono={Boxes} color="verde" detalle="Stock real" retraso={60} />
        <Metrica etiqueta="Sin stock" valor={resumen.sin_stock} icono={CircleSlash} color={resumen.sin_stock > 0 ? "ambar" : "gris"} detalle="Nada disponible para vender" retraso={120} />
        <Metrica etiqueta="Valor a costo" valor={precio(resumen.valor_a_costo)} icono={Wallet} color="texto" detalle="Stock × (costo + gastos)" retraso={180} />
      </div>

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <form action="/inventario" className="flex flex-1 gap-2 sm:max-w-sm">
          <label htmlFor="inv-buscar" className="sr-only">Buscar en el inventario</label>
          <input id="inv-buscar" name="buscar" defaultValue={buscar} placeholder="Buscar por nombre o código" maxLength={100} className={CAMPO} />
          <button type="submit" className={BOTON_SECUNDARIO} aria-label="Buscar">
            <Search className="h-4 w-4" aria-hidden="true" />
          </button>
        </form>
        {puedeEditar && (
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => setModo({ tipo: "importar" })} className={BOTON_SECUNDARIO}>
              <Upload className="h-4 w-4" aria-hidden="true" />
              Importar Excel o CSV
            </button>
            <button type="button" onClick={() => setModo({ tipo: "nuevo" })} className={BOTON_PRIMARIO}>
              <Plus className="h-4 w-4" aria-hidden="true" />
              Agregar producto
            </button>
          </div>
        )}
      </div>

      {productos.length === 0 ? (
        <EmptyState
          icono={Boxes}
          titulo={buscar ? "No encontramos productos con esa búsqueda" : "Tu inventario está vacío"}
          descripcion={
            buscar
              ? "Probá con otra palabra o borrá la búsqueda."
              : "Agregá tus productos uno por uno o importá la lista que ya tenés en Excel o CSV."
          }
        />
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-borde bg-superficie">
          <table className="w-full min-w-[720px] text-sm">
            <thead>
              <tr className="border-b border-borde text-left text-xs text-texto-2">
                <th scope="col" className="px-4 py-3 font-medium">Producto</th>
                <th scope="col" className="px-4 py-3 text-right font-medium">Precio de venta</th>
                <th scope="col" className="px-4 py-3 text-right font-medium">Costo + gastos</th>
                <th scope="col" className="px-4 py-3 text-right font-medium">Ganancia por unidad</th>
                <th scope="col" className="px-4 py-3 text-right font-medium">Stock</th>
                <th scope="col" className="px-4 py-3 font-medium">Catálogo público</th>
                {puedeEditar && <th scope="col" className="px-4 py-3"><span className="sr-only">Acciones</span></th>}
              </tr>
            </thead>
            <tbody>
              {productos.map((p) => {
                const costo = p.costo_unitario === null ? null : Number(p.costo_unitario) + Number(p.gastos_unitarios ?? 0);
                const margen = p.margen_unitario === null ? null : Number(p.margen_unitario);
                return (
                  <tr key={p.id} className="border-b border-borde last:border-0 hover:bg-superficie-2/50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        {p.foto_ids[0] ? (
                          // eslint-disable-next-line @next/next/no-img-element -- foto privada servida por el BFF con sesión
                          <img src={urlFoto(p.foto_ids[0])} alt="" className="h-10 w-10 shrink-0 rounded-lg object-cover" />
                        ) : (
                          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-superficie-2 text-texto-3">
                            <ImageOff className="h-4 w-4" aria-hidden="true" />
                          </div>
                        )}
                        <div className="min-w-0">
                          <p className="truncate font-medium text-texto">{p.nombre}</p>
                          {p.sku && <p className="text-xs text-texto-3">{p.sku}</p>}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-texto">{precio(p.precio_venta)}</td>
                    <td className="px-4 py-3 text-right tabular-nums text-texto-2">{costo === null ? "—" : precio(String(costo))}</td>
                    <td className={`px-4 py-3 text-right font-medium tabular-nums ${margen === null ? "text-texto-3" : margen > 0 ? "text-verde" : "text-rojo"}`}>
                      {margen === null ? "—" : precio(p.margen_unitario)}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums">
                      <span className={p.disponibles > 0 ? "text-texto" : "text-ambar"}>{p.stock}</span>
                      {p.stock_reservado > 0 && <span className="block text-xs text-texto-3">{p.stock_reservado} reservadas</span>}
                    </td>
                    <td className="px-4 py-3">
                      {p.publicado ? (
                        <Badge tono="verde" punto><Eye className="h-3 w-3" aria-hidden="true" /> Publicado</Badge>
                      ) : (
                        <Badge tono="gris">Oculto</Badge>
                      )}
                    </td>
                    {puedeEditar && (
                      <td className="px-4 py-3 text-right">
                        <button
                          type="button"
                          onClick={() => setModo({ tipo: "editar", producto: p })}
                          className="inline-flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm text-acento-claro hover:bg-superficie-2"
                        >
                          <Pencil className="h-4 w-4" aria-hidden="true" />
                          Editar
                        </button>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      {listado.total > productos.length && (
        <p className="mt-3 text-xs text-texto-3">Mostrando {productos.length} de {listado.total}. Usá la búsqueda para encontrar el resto.</p>
      )}

      {modo?.tipo === "nuevo" && <EditorInventario moneda={moneda} onCerrar={cerrar} />}
      {modo?.tipo === "editar" && <EditorInventario moneda={moneda} producto={modo.producto} onCerrar={cerrar} />}
      {modo?.tipo === "importar" && <ImportarInventario moneda={moneda} onCerrar={cerrar} />}
    </>
  );
}
