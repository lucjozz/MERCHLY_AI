/**
 * Mapa de etiquetas humanas para los valores crudos que devuelve el backend.
 * Regla: la UI nunca muestra `en_catalogo`, `candidato`, `MX`, etc. sueltos.
 */

export type Tono = "ambar" | "verde" | "azul" | "gris" | "rojo";

export interface InfoEstado {
  etiqueta: string;
  tono: Tono;
  descripcion: string;
}

export const ESTADOS: Record<string, InfoEstado> = {
  candidato: {
    etiqueta: "Por revisar",
    tono: "ambar",
    descripcion: "La IA lo sugirió y espera tu decisión.",
  },
  en_catalogo: {
    etiqueta: "En catálogo",
    tono: "verde",
    descripcion: "Lo aprobaste: ya está listo para vender y hacer campañas.",
  },
  descartado: {
    etiqueta: "Descartado",
    tono: "gris",
    descripcion: "Lo descartaste. No avanza.",
  },
};

export function infoEstado(estado: string): InfoEstado {
  return (
    ESTADOS[estado] ?? {
      etiqueta: capitalizar(estado.replace(/_/g, " ")),
      tono: "gris",
      descripcion: "",
    }
  );
}

const NIVELES: Record<string, { etiqueta: string; valor: number }> = {
  bajo: { etiqueta: "Baja", valor: 1 },
  medio: { etiqueta: "Media", valor: 2 },
  alto: { etiqueta: "Alta", valor: 3 },
};

/** "alto" -> "Alta" (se usa con "Demanda" / "Competencia", ambos femeninos). */
export function etiquetaNivel(nivel: string): string {
  return NIVELES[nivel]?.etiqueta ?? capitalizar(nivel);
}

/** 1 a 3 para dibujar medidores; 0 si el valor no es conocido. */
export function valorNivel(nivel: string): number {
  return NIVELES[nivel]?.valor ?? 0;
}

export const MERCADOS: Record<string, { nombre: string; bandera: string }> = {
  MX: { nombre: "México", bandera: "🇲🇽" },
  US: { nombre: "Estados Unidos", bandera: "🇺🇸" },
  BO: { nombre: "Bolivia", bandera: "🇧🇴" },
  AR: { nombre: "Argentina", bandera: "🇦🇷" },
};

export function etiquetaMercado(codigo: string): string {
  const mercado = MERCADOS[codigo?.toUpperCase()];
  return mercado ? `${mercado.nombre} ${mercado.bandera}` : codigo;
}

export const ETIQUETA_CANAL: Record<string, string> = {
  redes_sociales: "Redes sociales",
  busqueda_paga: "Búsqueda paga (Google, etc.)",
  email: "Email",
};

export function etiquetaCanal(canal: string): string {
  return ETIQUETA_CANAL[canal] ?? capitalizar(canal.replace(/_/g, " "));
}

export const ETIQUETA_ROL: Record<string, string> = {
  admin_principal: "Administrador principal",
  responsable_tecnico: "Responsable técnico",
  responsable_negocio: "Responsable de negocio",
  usuario_operativo: "Usuario operativo",
};

export function etiquetaRol(rol: string): string {
  return ETIQUETA_ROL[rol] ?? capitalizar(rol.replace(/_/g, " "));
}

/**
 * Los proveedores simulados marcan sus resultados con la palabra "simulado"
 * (en el nombre o en los riesgos). Lo detectamos para mostrar un badge.
 */
export function esProductoSimulado(producto: {
  nombre_producto: string;
  riesgos_identificados?: string[];
}): boolean {
  const textos = [producto.nombre_producto, ...(producto.riesgos_identificados ?? [])];
  return textos.some((t) => /simulad/i.test(t));
}

export function esCampanaSimulada(campana: {
  angulos_de_campana: string[];
  advertencias: string[];
  publico_objetivo_sugerido: string;
}): boolean {
  const textos = [
    ...campana.angulos_de_campana,
    ...campana.advertencias,
    campana.publico_objetivo_sugerido,
  ];
  return textos.some((t) => /simulad/i.test(t));
}

/** Quita el sufijo "(simulado)" del nombre: ya lo indica el badge. */
export function nombreLimpio(nombre: string): string {
  return nombre.replace(/\s*\(simulado\)\s*$/i, "").trim() || nombre;
}

export function formatearPrecio(valor: number | null): string {
  if (valor === null || valor === undefined) return "Sin dato";
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(valor);
}

export function formatearFecha(iso: string): string {
  return new Date(iso).toLocaleString("es-BO", {
    timeZone: "America/La_Paz",
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function haceCuanto(iso: string): string {
  const minutos = Math.max(
    0,
    Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  );
  if (minutos < 1) return "hace un momento";
  if (minutos < 60) return `hace ${minutos} min`;
  const horas = Math.floor(minutos / 60);
  if (horas < 24) return `hace ${horas} h`;
  const dias = Math.floor(horas / 24);
  return `hace ${dias} ${dias === 1 ? "día" : "días"}`;
}

export function capitalizar(texto: string): string {
  return texto ? texto.charAt(0).toUpperCase() + texto.slice(1) : texto;
}

export function plural(n: number, singular: string, pluralTexto?: string): string {
  return `${n} ${n === 1 ? singular : pluralTexto ?? `${singular}s`}`;
}
