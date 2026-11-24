/**
 * Errores de API con mensajes para personas (docs/013-Seguridad/04, sección 5).
 * Se distingue: sin sesión (401), sin permiso (403), no existe (404),
 * conflicto (409), datos inválidos (422), límite de uso (429), falla del
 * servidor (5xx) y falta de conexión.
 */

export class SesionInvalidaError extends Error {
  constructor(mensaje = "Tu sesión venció. Volvé a iniciar sesión.") {
    super(mensaje);
    this.name = "SesionInvalidaError";
  }
}

export class SinPermisoError extends Error {
  constructor(mensaje = "No tenés permiso para hacer esto. Pedile acceso al admin de tu negocio.") {
    super(mensaje);
    this.name = "SinPermisoError";
  }
}

export class ApiError extends Error {
  readonly status: number;
  constructor(status: number, mensaje: string) {
    super(mensaje);
    this.name = "ApiError";
    this.status = status;
  }
}

export const MENSAJE_SIN_CONEXION =
  "No pudimos conectarnos con el servidor. Revisá tu conexión y probá de nuevo.";

function minutos(retryAfter: string | null): string {
  const s = Number(retryAfter);
  if (!Number.isFinite(s) || s <= 0) return "unos minutos";
  const m = Math.ceil(s / 60);
  return m <= 1 ? "un minuto" : `${m} minutos`;
}

/** Mensaje legible para un status HTTP (el detalle del backend gana si es texto). */
export function mensajeDeError(status: number, detalle?: unknown, retryAfter?: string | null): string {
  const texto = typeof detalle === "string" && detalle.length < 300 ? detalle : null;
  switch (status) {
    case 401:
      return "Tu sesión venció. Volvé a iniciar sesión.";
    case 403:
      return texto ?? new SinPermisoError().message;
    case 404:
      return "Eso ya no existe (o no es de tu negocio).";
    case 409:
      return texto ?? "Este producto ya tiene una decisión final y no se puede cambiar. Recargá la página para ver su estado.";
    case 413:
      return "Lo que enviaste es demasiado grande.";
    case 422:
      return texto ?? "Revisá los datos: hay algo que no es válido.";
    case 429:
      return `Hiciste muchos intentos seguidos. Esperá ${minutos(retryAfter ?? null)} y probá de nuevo.`;
    case 503:
      return texto ?? "El servicio no está disponible en este momento. Probá de nuevo en un rato.";
    default:
      return status >= 500
        ? "Algo falló de nuestro lado. Probá de nuevo en un momento."
        : "No se pudo completar la acción.";
  }
}

/** Convierte una respuesta no-OK en el error que corresponde. */
export async function errorDeRespuesta(respuesta: Response): Promise<Error> {
  const cuerpo = await respuesta.json().catch(() => ({}));
  const mensaje = mensajeDeError(respuesta.status, cuerpo?.detail, respuesta.headers.get("retry-after"));
  if (respuesta.status === 401) return new SesionInvalidaError(mensaje);
  if (respuesta.status === 403) return new SinPermisoError(mensaje);
  return new ApiError(respuesta.status, mensaje);
}
