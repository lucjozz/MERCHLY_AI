/**
 * Inventario (privado, del dueño) y catálogo público (lo que ve la IA).
 * docs/007-Agentes/08. Lecturas desde Server Components y acciones desde el cliente.
 */
import { fetchAutenticadoServidor } from "@/lib/api/servidor";
import { errorDeRespuesta } from "@/lib/api/errores";

// Decimal del backend: llega como string ("450.00"); se convierte al mostrar.
export type Monto = string | null;

export interface ProductoInventario {
  id: string;
  nombre: string;
  descripcion: string | null;
  especificaciones: Record<string, string>;
  precio_venta: Monto;
  publicado: boolean;
  sku: string | null;
  costo_unitario: Monto;
  gastos_unitarios: Monto;
  proveedor: string | null;
  notas_internas: string | null;
  stock: number;
  stock_reservado: number;
  disponibles: number;
  margen_unitario: Monto;
  origen: string;
  foto_ids: string[];
  creado_en: string;
  actualizado_en: string;
}

export interface ResumenInventario {
  productos: number;
  unidades: number;
  sin_stock: number;
  publicados: number;
  valor_a_costo: string;
}

export interface InventarioListado {
  productos: ProductoInventario[];
  total: number;
  pagina: number;
  tamano_pagina: number;
  resumen: ResumenInventario;
}

export interface ItemCatalogoPublico {
  id: string;
  nombre: string;
  descripcion: string | null;
  especificaciones: Record<string, string>;
  precio_venta: Monto;
  disponibles: number;
  foto_ids: string[];
}

/** Lo que se manda al crear o editar (los montos como número). */
export interface ProductoInventarioDatos {
  nombre: string;
  descripcion?: string | null;
  especificaciones?: Record<string, string>;
  precio_venta?: number | null;
  publicado?: boolean;
  sku?: string | null;
  costo_unitario?: number | null;
  gastos_unitarios?: number | null;
  proveedor?: string | null;
  notas_internas?: string | null;
  stock?: number;
}

export interface FilaImportada {
  fila: number;
  nombre: string | null;
  sku: string | null;
  descripcion: string | null;
  precio_venta: Monto;
  costo_unitario: Monto;
  stock: number | null;
  problemas: string[];
}

export interface ImportarVistaPrevia {
  formato: string;
  columnas: Record<string, string | null>;
  filas: FilaImportada[];
  descartadas: number;
}

export { urlFoto } from "@/lib/api/inventario-url";

// ------------------------------------------------------------ servidor

export async function listarInventario(buscar?: string): Promise<InventarioListado> {
  const p = new URLSearchParams({ pagina: "1", tamano_pagina: "100" });
  if (buscar) p.set("buscar", buscar.slice(0, 100));
  const r = await fetchAutenticadoServidor(`/inventario?${p}`);
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}

export async function listarCatalogoPublico(): Promise<ItemCatalogoPublico[]> {
  const r = await fetchAutenticadoServidor("/inventario/catalogo-publico");
  if (!r.ok) throw await errorDeRespuesta(r);
  return r.json();
}
