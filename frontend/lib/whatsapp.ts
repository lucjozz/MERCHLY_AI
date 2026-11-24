/** Mensajes con formato de WhatsApp (docs/004-Backend/05, sección 2). Sin dependencias, con tests. */

export interface ItemCatalogo {
  nombre: string;
  precio: string;
}

/** WhatsApp usa *texto* para negrita: se quitan los símbolos de formato que vengan en los datos. */
function limpiar(texto: string): string {
  return texto.replace(/[*_~`]/g, "").replace(/\s+/g, " ").trim();
}

export function armarMensajeCatalogo(d: { encabezado: string; nota: string; simbolo: string; items: ItemCatalogo[] }): string {
  const lineas: string[] = [];
  const titulo = limpiar(d.encabezado);
  if (titulo) lineas.push(`*${titulo}*`, "");
  for (const item of d.items) {
    const nombre = limpiar(item.nombre);
    const precio = limpiar(item.precio);
    lineas.push(precio ? `• ${nombre} — *${d.simbolo} ${precio}*` : `• ${nombre} — consultá el precio`);
  }
  const nota = d.nota.trim();
  if (nota) lineas.push("", nota);
  return lineas.join("\n");
}

/** Abre WhatsApp con el texto listo; la persona elige a quién mandarlo. */
export function enlaceWhatsApp(texto: string): string {
  return `https://wa.me/?text=${encodeURIComponent(texto)}`;
}
