import Link from "next/link";
import { Clock, Search } from "lucide-react";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import PageHeader from "@/components/ui/PageHeader";
import EmptyState from "@/components/ui/EmptyState";
import Alerta from "@/components/ui/Alerta";
import { BadgeEstado, BadgeSimulado } from "@/components/ui/Badge";
import {
  esProductoSimulado,
  etiquetaMercado,
  formatearFecha,
  haceCuanto,
  infoEstado,
  nombreLimpio,
} from "@/lib/etiquetas";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

const COLOR_PUNTO: Record<string, string> = {
  ambar: "bg-ambar ring-ambar-fondo",
  verde: "bg-verde ring-verde-fondo",
  gris: "bg-texto-2 ring-gris-fondo",
};

export default async function Actividad() {
  let datos;
  let error: string | null = null;

  try {
    datos = await listarProductosCandidatos(1, 20);
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  return (
    <>
      <PageHeader
        titulo="Actividad"
        icono={Clock}
        descripcion="Lo último que encontró la IA, del más reciente al más antiguo."
        ayuda="Es un registro de los productos que fue descubriendo el Investigador. Tocá cualquiera para ver su análisis."
      />

      {error && <Alerta>{error}</Alerta>}

      {datos && datos.productos.length === 0 && (
        <EmptyState
          icono={Search}
          titulo="Todavía no hay actividad"
          descripcion="Cuando la IA descubra productos, van a aparecer acá. Empezá con una búsqueda."
          accion={{ href: "/productos", texto: "Buscar productos" }}
        />
      )}

      {datos && datos.productos.length > 0 && (
        <ol className="relative max-w-3xl space-y-3 before:absolute before:bottom-4 before:left-[11px] before:top-4 before:w-px before:bg-borde">
          {datos.productos.map((producto, i) => {
            const tono = infoEstado(producto.estado).tono;
            return (
              <li
                key={producto.id}
                className="relative flex gap-4 animate-aparecer"
                style={{ animationDelay: `${Math.min(i, 10) * 35}ms` }}
              >
                <span
                  className={`relative z-10 mt-5 h-[9px] w-[9px] shrink-0 translate-x-[7px] rounded-full ring-4 ${
                    COLOR_PUNTO[tono] ?? COLOR_PUNTO.gris
                  }`}
                  aria-hidden="true"
                />
                <Link
                  href={`/productos/${producto.id}`}
                  className="group ml-2 min-w-0 flex-1 rounded-2xl border border-borde bg-superficie p-4 transition-all hover:border-borde-fuerte hover:bg-superficie-2"
                >
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <p className="min-w-0 text-sm">
                      <span className="text-texto-2">La IA encontró </span>
                      <span className="font-medium text-texto transition-colors group-hover:text-acento-claro">
                        {nombreLimpio(producto.nombre_producto)}
                      </span>
                    </p>
                    <time
                      dateTime={producto.creado_en}
                      className="whitespace-nowrap text-xs text-texto-2"
                      title={formatearFecha(producto.creado_en)}
                    >
                      {haceCuanto(producto.creado_en)}
                    </time>
                  </div>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-texto-2">
                    <BadgeEstado estado={producto.estado} />
                    {esProductoSimulado(producto) && <BadgeSimulado />}
                    <span>
                      {producto.categoria} · {etiquetaMercado(producto.mercado_objetivo)}
                    </span>
                  </div>
                </Link>
              </li>
            );
          })}
        </ol>
      )}
    </>
  );
}
