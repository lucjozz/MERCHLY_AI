import type { ReactNode } from "react";
import Link from "next/link";
import { ArrowRight, MapPin } from "lucide-react";
import type { ProductoCandidato } from "@/lib/api/productos-candidatos";
import { BadgeEstado, BadgeSimulado } from "@/components/ui/Badge";
import Medidor from "@/components/ui/Medidor";
import {
  esProductoSimulado,
  etiquetaMercado,
  haceCuanto,
  nombreLimpio,
} from "@/lib/etiquetas";

interface TarjetaProductoProps {
  producto: ProductoCandidato;
  /** Botones extra (p. ej. eliminar). Quedan por encima del enlace de la tarjeta. */
  acciones?: ReactNode;
  retraso?: number;
}

/**
 * Tarjeta de producto. Toda la tarjeta es clickeable (patrón "enlace estirado")
 * sin anidar botones dentro del enlace.
 */
export default function TarjetaProducto({ producto, acciones, retraso = 0 }: TarjetaProductoProps) {
  const simulado = esProductoSimulado(producto);
  return (
    <article
      className="group relative flex flex-col rounded-2xl border border-borde bg-superficie p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-borde-fuerte hover:bg-superficie-2 hover:shadow-lg hover:shadow-black/30 focus-within:border-acento-borde animate-aparecer"
      style={{ animationDelay: `${retraso}ms` }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap gap-1.5">
          <BadgeEstado estado={producto.estado} />
          {simulado && <BadgeSimulado />}
        </div>
        {acciones && <div className="relative z-10 -mr-2 -mt-2">{acciones}</div>}
      </div>

      <h3 className="mt-3 text-base font-semibold leading-snug text-texto">
        <Link
          href={`/productos/${producto.id}`}
          className="outline-none after:absolute after:inset-0 after:rounded-2xl focus-visible:after:ring-2 focus-visible:after:ring-acento-claro"
        >
          {nombreLimpio(producto.nombre_producto)}
        </Link>
      </h3>
      <p className="mt-1 flex flex-wrap items-center gap-x-1.5 text-sm text-texto-2">
        <span>{producto.categoria}</span>
        <span aria-hidden="true">·</span>
        <span className="inline-flex items-center gap-1">
          <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
          {etiquetaMercado(producto.mercado_objetivo)}
        </span>
      </p>

      <div className="mt-4 grid grid-cols-2 gap-3 rounded-xl bg-fondo/60 p-3">
        <Medidor etiqueta="Demanda" nivel={producto.nivel_demanda_estimado} sentido="favorable-alto" compacto />
        <Medidor etiqueta="Competencia" nivel={producto.nivel_competencia_estimado} sentido="favorable-bajo" compacto />
      </div>

      <div className="mt-4 flex items-center justify-between text-xs text-texto-2">
        <span>Encontrado {haceCuanto(producto.creado_en)}</span>
        <span className="inline-flex items-center gap-1 font-semibold text-acento-claro">
          Ver análisis
          <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" aria-hidden="true" />
        </span>
      </div>
    </article>
  );
}
