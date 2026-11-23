import Link from "next/link";
import {
  Search,
  FileSearch,
  Scale,
  Megaphone,
  Check,
  ArrowRight,
  type LucideIcon,
} from "lucide-react";

type EstadoPaso = "hecho" | "actual" | "pendiente";

interface Paso {
  titulo: string;
  texto: string;
  icono: LucideIcon;
  href: string;
  cta: string;
  estado: EstadoPaso;
  detalle?: string;
}

interface RecorridoGuiadoProps {
  investigaciones: number;
  porRevisar: number;
  aprobados: number;
  descartados: number;
}

/**
 * Recorrido del flujo principal con progreso calculado a partir de datos
 * reales. El paso 4 (campaña) no se puede marcar como hecho porque las
 * campañas todavía no se guardan en el backend.
 */
export default function RecorridoGuiado({
  investigaciones,
  porRevisar,
  aprobados,
  descartados,
}: RecorridoGuiadoProps) {
  const decididos = aprobados + descartados;
  const hizoBusqueda = investigaciones > 0 || porRevisar + decididos > 0;
  const tieneDecisiones = decididos > 0;

  const completados = [hizoBusqueda, tieneDecisiones, tieneDecisiones];
  const indiceActual = completados.findIndex((c) => !c);
  const estadoDe = (i: number): EstadoPaso =>
    i < 3 && completados[i]
      ? "hecho"
      : i === (indiceActual === -1 ? 3 : indiceActual)
        ? "actual"
        : "pendiente";

  const pasos: Paso[] = [
    {
      titulo: "Buscá productos con IA",
      texto: "Escribí una categoría y elegí el país.",
      icono: Search,
      href: "/productos",
      cta: "Buscar productos",
      estado: estadoDe(0),
      detalle: hizoBusqueda
        ? `${investigaciones} ${investigaciones === 1 ? "búsqueda" : "búsquedas"}`
        : undefined,
    },
    {
      titulo: "Revisá la evidencia",
      texto: "Mirá demanda, competencia, precios y riesgos.",
      icono: FileSearch,
      href: "/productos?estado=candidato",
      cta: "Ver pendientes",
      estado: estadoDe(1),
      detalle:
        porRevisar > 0
          ? `${porRevisar} por revisar`
          : hizoBusqueda
            ? "Nada pendiente"
            : undefined,
    },
    {
      titulo: "Decidí",
      texto: "Aprobá o descartá. La IA nunca decide por vos.",
      icono: Scale,
      href: "/decisiones",
      cta: "Ver decisiones",
      estado: estadoDe(2),
      detalle: tieneDecisiones
        ? `${aprobados} aprobados · ${descartados} descartados`
        : undefined,
    },
    {
      titulo: "Generá la campaña",
      texto: "Ideas y textos para tus canales de venta.",
      icono: Megaphone,
      href: "/marketing",
      cta: aprobados > 0 ? "Crear campaña" : "Ir a Marketing",
      estado: estadoDe(3),
      detalle:
        aprobados > 0
          ? "Las campañas no se guardan todavía"
          : "Necesitás un producto aprobado",
    },
  ];

  const hechos = completados.filter(Boolean).length;
  const porcentaje = Math.round((hechos / pasos.length) * 100);

  return (
    <section
      aria-labelledby="titulo-recorrido"
      className="relative overflow-hidden rounded-3xl border border-acento-borde/60 bg-gradient-to-br from-acento-hondo/40 via-superficie to-superficie p-5 sm:p-7 animate-aparecer"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-20 -top-24 h-64 w-64 rounded-full bg-acento/10 blur-3xl"
      />

      <div className="relative flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-acento-claro">
            Cómo funciona
          </p>
          <h2 id="titulo-recorrido" className="mt-1 text-xl font-bold text-texto sm:text-2xl">
            De una idea a una campaña, en 4 pasos
          </h2>
        </div>
        <div className="w-full sm:w-56">
          <div className="flex justify-between text-xs text-texto-2">
            <span>Tu progreso</span>
            <span className="font-semibold text-texto">
              {hechos} de {pasos.length} pasos
            </span>
          </div>
          <div
            className="mt-2 h-2 overflow-hidden rounded-full bg-fondo"
            role="progressbar"
            aria-valuenow={porcentaje}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label="Progreso del recorrido"
          >
            <div
              className="h-full rounded-full bg-gradient-to-r from-acento to-verde transition-[width] duration-700"
              style={{ width: `${porcentaje}%` }}
            />
          </div>
        </div>
      </div>

      <ol className="relative mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {pasos.map((paso, i) => {
          const Icono = paso.icono;
          const esActual = paso.estado === "actual";
          const esHecho = paso.estado === "hecho";
          return (
            <li
              key={paso.titulo}
              aria-current={esActual ? "step" : undefined}
              className={`flex flex-col rounded-2xl border p-4 transition-all duration-200 animate-aparecer ${
                esActual
                  ? "border-acento bg-superficie shadow-lg shadow-acento/10"
                  : esHecho
                    ? "border-verde-borde bg-superficie/80"
                    : "border-borde bg-superficie/60"
              }`}
              style={{ animationDelay: `${80 + i * 70}ms` }}
            >
              <div className="flex items-center justify-between">
                <span
                  className={`flex h-9 w-9 items-center justify-center rounded-xl ${
                    esHecho
                      ? "bg-verde-fondo text-verde"
                      : esActual
                        ? "bg-acento-hondo text-acento-claro"
                        : "bg-superficie-2 text-texto-2"
                  }`}
                >
                  {esHecho ? (
                    <Check className="h-4 w-4" aria-hidden="true" />
                  ) : (
                    <Icono className="h-4 w-4" aria-hidden="true" />
                  )}
                </span>
                <span
                  className={`text-xs font-semibold ${
                    esHecho ? "text-verde" : esActual ? "text-acento-claro" : "text-texto-2"
                  }`}
                >
                  {esHecho ? "Listo" : esActual ? "Siguiente paso" : `Paso ${i + 1}`}
                </span>
              </div>
              <p className="mt-3 font-semibold text-texto">
                <span className="text-texto-2">{i + 1}. </span>
                {paso.titulo}
              </p>
              <p className="mt-1 text-sm leading-relaxed text-texto-2">{paso.texto}</p>
              {paso.detalle && (
                <p className="mt-2 text-xs text-texto-2">{paso.detalle}</p>
              )}
              <Link
                href={paso.href}
                className={`group mt-4 inline-flex items-center gap-1.5 self-start text-sm font-semibold transition-colors ${
                  esActual ? "text-acento-claro hover:text-texto" : "text-texto-2 hover:text-texto"
                }`}
              >
                {paso.cta}
                <ArrowRight
                  className="h-4 w-4 transition-transform group-hover:translate-x-0.5"
                  aria-hidden="true"
                />
              </Link>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
