/** Clases compartidas de botones, enlaces-botón y campos de formulario. */
export const BOTON_PRIMARIO =
  "inline-flex items-center justify-center gap-2 rounded-lg bg-acento-boton px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-acento/10 transition-all hover:bg-acento hover:shadow-acento/25 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100";

export const BOTON_SECUNDARIO =
  "inline-flex items-center justify-center gap-2 rounded-lg border border-borde-fuerte bg-superficie px-4 py-2.5 text-sm font-medium text-texto transition-colors hover:border-acento-borde hover:bg-superficie-2 disabled:cursor-not-allowed disabled:opacity-50";

export const ENLACE =
  "inline-flex items-center gap-1.5 text-sm font-medium text-acento-claro transition-colors hover:text-texto";

export const CAMPO =
  "w-full rounded-lg border border-borde-fuerte bg-fondo px-3 py-2.5 text-sm text-texto placeholder:text-texto-3 outline-none transition-colors focus:border-acento focus:ring-2 focus:ring-acento/30 disabled:opacity-50";

export const ETIQUETA_CAMPO = "mb-2 block text-sm font-medium text-texto";

/** Contenedor de barra de progreso horizontal. */
export const PISTA_BARRA = "h-2 overflow-hidden rounded-full bg-fondo";
