/** Acciones del inventario desde componentes cliente (vía BFF). docs/007-Agentes/08. */
import { fetchJson } from "@/lib/api/cliente";
import type { ImportarVistaPrevia, ProductoInventario, ProductoInventarioDatos } from "@/lib/api/inventario";

const JSON_HEADERS = { "Content-Type": "application/json" };

export function crearProductoInventario(datos: ProductoInventarioDatos) {
  return fetchJson<ProductoInventario>("/inventario", { method: "POST", headers: JSON_HEADERS, body: JSON.stringify(datos) });
}

export function editarProductoInventario(id: string, cambios: Partial<ProductoInventarioDatos>) {
  return fetchJson<ProductoInventario>(`/inventario/${id}`, { method: "PATCH", headers: JSON_HEADERS, body: JSON.stringify(cambios) });
}

export function eliminarProductoInventario(id: string) {
  return fetchJson<void>(`/inventario/${id}`, { method: "DELETE" });
}

export function subirFotoInventario(id: string, imagenBase64: string) {
  return fetchJson<{ id: string; tamano: number }>(`/inventario/${id}/fotos`, {
    method: "POST", headers: JSON_HEADERS, body: JSON.stringify({ imagen_base64: imagenBase64 }),
  });
}

export function borrarFotoInventario(id: string, fotoId: string) {
  return fetchJson<void>(`/inventario/${id}/fotos/${fotoId}`, { method: "DELETE" });
}

export function vistaPreviaImportacion(nombreArchivo: string, contenidoBase64: string) {
  return fetchJson<ImportarVistaPrevia>("/inventario/importar/vista-previa", {
    method: "POST", headers: JSON_HEADERS, body: JSON.stringify({ nombre_archivo: nombreArchivo, contenido_base64: contenidoBase64 }),
  });
}

export function confirmarImportacion(productos: ProductoInventarioDatos[]) {
  return fetchJson<{ creados: number }>("/inventario/importar", {
    method: "POST", headers: JSON_HEADERS, body: JSON.stringify({ productos }),
  });
}

/** Achica la foto en el navegador (máx. 1600 px, JPEG) antes de subirla: del celular salen fotos de 5-10 MB. */
export async function achicarFoto(archivo: File): Promise<string> {
  if (!/^image\/(jpeg|png|webp)$/.test(archivo.type)) throw new Error("Elegí una foto JPG, PNG o WebP.");
  const bitmap = await createImageBitmap(archivo);
  const escala = Math.min(1, 1600 / Math.max(bitmap.width, bitmap.height));
  const lienzo = document.createElement("canvas");
  lienzo.width = Math.round(bitmap.width * escala);
  lienzo.height = Math.round(bitmap.height * escala);
  lienzo.getContext("2d")!.drawImage(bitmap, 0, 0, lienzo.width, lienzo.height);
  bitmap.close();
  for (const calidad of [0.85, 0.7, 0.55]) {
    const dataUrl = lienzo.toDataURL("image/jpeg", calidad);
    if (dataUrl.length < 950_000) return dataUrl;
  }
  throw new Error("La foto es demasiado pesada. Probá con otra.");
}

/** Archivo → base64 (sin el prefijo data:). */
export function archivoABase64(archivo: File): Promise<string> {
  return new Promise((resolver, rechazar) => {
    const lector = new FileReader();
    lector.onload = () => resolver(String(lector.result).split(",", 2)[1] ?? "");
    lector.onerror = () => rechazar(new Error("No pudimos leer el archivo."));
    lector.readAsDataURL(archivo);
  });
}
