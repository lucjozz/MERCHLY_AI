import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import Link from "next/link";
import { Package, SearchX, Sparkles, Filter, X } from "lucide-react";
import BuscarProductos from "@/components/BuscarProductos";
import BotonEliminar from "@/components/BotonEliminar";
import TarjetaProducto from "@/components/TarjetaProducto";
import PageHeader from "@/components/ui/PageHeader";
import EmptyState from "@/components/ui/EmptyState";
import Alerta from "@/components/ui/Alerta";
import { BOTON_SECUNDARIO, CAMPO } from "@/components/ui/estilos";
import { ESTADOS, plural } from "@/lib/etiquetas";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

interface PageProps {
  searchParams: Promise<{ categoria?: string; estado?: string }>;
}

const PESTANAS = [
  { valor: "", etiqueta: "Todos" },
  ...Object.entries(ESTADOS).map(([valor, info]) => ({ valor, etiqueta: info.etiqueta })),
];

function hrefFiltro(categoria: string | undefined, estado: string) {
  const parametros = new URLSearchParams();
  if (categoria) parametros.set("categoria", categoria);
  if (estado) parametros.set("estado", estado);
  const query = parametros.toString();
  return query ? `/productos?${query}` : "/productos";
}

export default async function Productos({ searchParams }: PageProps) {
  const filtros = await searchParams;
  let datos;
  let error: string | null = null;

  try {
    datos = await listarProductosCandidatos(
      1,
      20,
      filtros.categoria,
      filtros.estado
    );
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  const hayFiltros = Boolean(filtros.categoria || filtros.estado);
  const estadoActual = filtros.estado ?? "";

  return (
    <>
      <PageHeader
        titulo="Productos"
        icono={Package}
        descripcion="Las oportunidades de venta que encontró la IA, con su evidencia."
        ayuda={
          <>
            Buscá una categoría, abrí cada producto para revisar la evidencia y
            decidí si entra a tu catálogo. Los que están <strong className="text-ambar">Por revisar</strong>{" "}
            esperan tu decisión.
          </>
        }
      />

      <BuscarProductos />

      <section aria-labelledby="titulo-lista">
        <div className="mb-4 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <h2 id="titulo-lista" className="text-lg font-semibold text-texto">
            Tus productos
          </h2>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <nav aria-label="Filtrar por estado" className="-mx-1 overflow-x-auto px-1">
              <ul className="flex w-max gap-1 rounded-xl border border-borde bg-superficie p-1">
                {PESTANAS.map((p) => {
                  const activa = estadoActual === p.valor;
                  return (
                    <li key={p.valor || "todos"}>
                      <Link
                        href={hrefFiltro(filtros.categoria, p.valor)}
                        aria-current={activa ? "page" : undefined}
                        className={`block whitespace-nowrap rounded-lg px-3 py-1.5 text-sm transition-colors ${
                          activa
                            ? "bg-acento-hondo font-medium text-texto"
                            : "text-texto-2 hover:text-texto"
                        }`}
                      >
                        {p.etiqueta}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </nav>

            <form className="flex gap-2" role="search">
              {filtros.estado && <input type="hidden" name="estado" value={filtros.estado} />}
              <label htmlFor="filtro-categoria" className="sr-only">
                Filtrar por categoría
              </label>
              <input
                id="filtro-categoria"
                type="text"
                name="categoria"
                placeholder="Filtrar por categoría"
                defaultValue={filtros.categoria}
                className={`${CAMPO} min-w-0 py-2 sm:w-52`}
              />
              <button type="submit" className={`${BOTON_SECUNDARIO} py-2`} aria-label="Aplicar filtro">
                <Filter className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">Filtrar</span>
              </button>
            </form>
          </div>
        </div>

        {filtros.categoria && (
          <p className="mb-4 flex flex-wrap items-center gap-2 text-sm text-texto-2">
            Mostrando la categoría{" "}
            <span className="font-medium text-texto">“{filtros.categoria}”</span>
            <Link
              href={hrefFiltro(undefined, estadoActual)}
              className="inline-flex items-center gap-1 rounded-full border border-borde-fuerte px-2 py-0.5 text-xs text-texto-2 hover:text-texto"
            >
              <X className="h-3 w-3" aria-hidden="true" />
              Quitar
            </Link>
          </p>
        )}

        {error && <Alerta>{error}</Alerta>}

        {datos && datos.productos.length === 0 &&
          (hayFiltros ? (
            <EmptyState
              icono={SearchX}
              titulo="No hay productos con estos filtros"
              descripcion="Probá con otra categoría u otro estado, o mirá todos tus productos."
              accion={{ href: "/productos", texto: "Ver todos" }}
            />
          ) : (
            <EmptyState
              icono={Sparkles}
              titulo="Todavía no investigaste nada"
              descripcion="Escribí una categoría como “mochilas antirrobo” en el buscador de arriba y la IA te sugiere productos."
            />
          ))}

        {datos && datos.productos.length > 0 && (
          <>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {datos.productos.map((producto, i) => (
                <TarjetaProducto
                  key={producto.id}
                  producto={producto}
                  retraso={Math.min(i, 8) * 40}
                  acciones={
                    <BotonEliminar
                      productoId={producto.id}
                      nombreProducto={producto.nombre_producto}
                    />
                  }
                />
              ))}
            </div>
            <p className="mt-4 text-xs text-texto-2">
              {datos.total > datos.productos.length
                ? `Mostrando ${datos.productos.length} de ${datos.total} productos.`
                : plural(datos.total, "producto") + "."}
            </p>
          </>
        )}
      </section>
    </>
  );
}
