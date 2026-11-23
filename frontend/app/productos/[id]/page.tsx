import { obtenerProductoCandidato } from "@/lib/api/productos-candidatos";
import AccionesDecision from "@/components/AccionesDecision";
import CampanaMarketingPanel from "@/components/CampanaMarketing";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowLeft,
  ExternalLink,
  FileSearch,
  MapPin,
  ShieldAlert,
  Tag,
  DollarSign,
  TrendingUp,
} from "lucide-react";
import { BadgeEstado, BadgeSimulado } from "@/components/ui/Badge";
import Card, { TituloCard } from "@/components/ui/Card";
import Medidor from "@/components/ui/Medidor";
import Alerta from "@/components/ui/Alerta";
import { ENLACE } from "@/components/ui/estilos";
import {
  esProductoSimulado,
  etiquetaMercado,
  formatearFecha,
  formatearPrecio,
  infoEstado,
  nombreLimpio,
} from "@/lib/etiquetas";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

interface PageProps {
  params: Promise<{ id: string }>;
}

/** Solo se enlazan URLs http(s); cualquier otro texto de la IA se muestra como texto. */
function esUrlSegura(texto: string): boolean {
  try {
    const url = new URL(texto);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}

export default async function DetalleProducto({ params }: PageProps) {
  const { id } = await params;
  let producto;

  let mensajeError: string | null = null;
  try {
    producto = await obtenerProductoCandidato(id);
  } catch (e) {
    mensajeError = mensajeDeErrorDePagina(e);
  }
  if (mensajeError) {
    return (
      <div className="mx-auto max-w-md py-16">
        <Alerta>{mensajeError}</Alerta>
        <Link href="/productos" className={`mt-6 ${ENLACE}`}>
          <ArrowLeft className="h-4 w-4" aria-hidden="true" />
          Volver a productos
        </Link>
      </div>
    );
  }

  if (!producto) {
    notFound();
  }

  const simulado = esProductoSimulado(producto);
  const estado = infoEstado(producto.estado);
  const margen =
    producto.precio_estimado_proveedor !== null &&
    producto.precio_sugerido_venta !== null
      ? producto.precio_sugerido_venta - producto.precio_estimado_proveedor
      : null;

  return (
    <div className="mx-auto max-w-4xl">
      <Link href="/productos" className={`mb-6 ${ENLACE}`}>
        <ArrowLeft className="h-4 w-4" aria-hidden="true" />
        Volver a productos
      </Link>

      {/* Encabezado */}
      <header className="animate-aparecer">
        <div className="flex flex-wrap items-center gap-2">
          <BadgeEstado estado={producto.estado} />
          {simulado && <BadgeSimulado />}
        </div>
        <h1 className="mt-3 text-2xl font-bold leading-tight tracking-tight text-texto sm:text-3xl">
          {nombreLimpio(producto.nombre_producto)}
        </h1>
        <p className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-texto-2">
          <span className="inline-flex items-center gap-1.5">
            <Tag className="h-4 w-4" aria-hidden="true" />
            {producto.categoria}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <MapPin className="h-4 w-4" aria-hidden="true" />
            {etiquetaMercado(producto.mercado_objetivo)}
          </span>
          <span>Encontrado el {formatearFecha(producto.creado_en)}</span>
        </p>
        {estado.descripcion && (
          <p className="mt-3 text-sm text-texto-2">{estado.descripcion}</p>
        )}
      </header>

      {simulado && (
        <Alerta tipo="info" className="mt-6">
          Este resultado viene de un <strong className="text-texto">proveedor simulado</strong>:
          sirve para probar el flujo, pero no refleja el mercado real.
        </Alerta>
      )}

      {/* Paso 2: evidencia */}
      <section aria-labelledby="titulo-evidencia" className="mt-8">
        <p className="text-xs font-semibold uppercase tracking-wider text-acento-claro">
          Paso 2 · Revisá la evidencia
        </p>
        <h2 id="titulo-evidencia" className="sr-only">
          Evidencia del producto
        </h2>

        <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Card className="!p-4 animate-aparecer">
            <p className="flex items-center gap-1.5 text-xs text-texto-2">
              <DollarSign className="h-3.5 w-3.5" aria-hidden="true" />
              Te cuesta (aprox.)
            </p>
            <p className="mt-2 text-lg font-semibold tabular-nums text-texto">
              {formatearPrecio(producto.precio_estimado_proveedor)}
            </p>
          </Card>
          <Card className="!p-4 animate-aparecer [animation-delay:60ms]">
            <p className="flex items-center gap-1.5 text-xs text-texto-2">
              <Tag className="h-3.5 w-3.5" aria-hidden="true" />
              Precio de venta sugerido
            </p>
            <p className="mt-2 text-lg font-semibold tabular-nums text-texto">
              {formatearPrecio(producto.precio_sugerido_venta)}
            </p>
          </Card>
          <Card className="!p-4 animate-aparecer [animation-delay:120ms]">
            <Medidor etiqueta="Demanda estimada" nivel={producto.nivel_demanda_estimado} sentido="favorable-alto" />
          </Card>
          <Card className="!p-4 animate-aparecer [animation-delay:180ms]">
            <Medidor etiqueta="Competencia estimada" nivel={producto.nivel_competencia_estimado} sentido="favorable-bajo" />
          </Card>
        </div>

        {margen !== null && (
          <p className="mt-3 flex items-center gap-2 text-sm text-texto-2">
            <TrendingUp className={`h-4 w-4 ${margen > 0 ? "text-verde" : "text-ambar"}`} aria-hidden="true" />
            Ganancia bruta estimada por unidad:{" "}
            <span className={`font-semibold ${margen > 0 ? "text-verde" : "text-ambar"}`}>
              {formatearPrecio(margen)}
            </span>
            <span className="text-texto-2">(antes de envío, impuestos y comisiones)</span>
          </p>
        )}

        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <Card>
            <TituloCard descripcion="De dónde sacó la IA esta información.">
              <span className="inline-flex items-center gap-2">
                <FileSearch className="h-4 w-4 text-acento-claro" aria-hidden="true" />
                Fuentes
              </span>
            </TituloCard>
            {producto.fuentes_evidencia.length === 0 ? (
              <p className="text-sm leading-relaxed text-texto-2">
                La IA no trajo fuentes para este producto. Si decidís, hacelo con
                más cuidado.
              </p>
            ) : (
              <ul className="space-y-2">
                {producto.fuentes_evidencia.map((fuente, i) => (
                  <li key={i} className="min-w-0 text-sm">
                    {esUrlSegura(fuente) ? (
                      <a
                        href={fuente}
                        target="_blank"
                        rel="noopener noreferrer nofollow"
                        className="inline-flex max-w-full items-center gap-1.5 text-acento-claro hover:text-texto"
                      >
                        <span className="truncate">{fuente}</span>
                        <ExternalLink className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                      </a>
                    ) : (
                      <span className="break-words text-texto">{fuente}</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </Card>

          <Card>
            <TituloCard descripcion="Cosas a tener en cuenta antes de decidir.">
              <span className="inline-flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-ambar" aria-hidden="true" />
                Riesgos
              </span>
            </TituloCard>
            {producto.riesgos_identificados.length === 0 ? (
              <p className="text-sm text-texto-2">La IA no identificó riesgos.</p>
            ) : (
              <ul className="space-y-2">
                {producto.riesgos_identificados.map((riesgo, i) => (
                  <li
                    key={i}
                    className="flex gap-2 rounded-lg border border-ambar-borde/60 bg-ambar-fondo/40 px-3 py-2 text-sm leading-relaxed text-texto"
                  >
                    <span className="mt-0.5 text-ambar" aria-hidden="true">⚠</span>
                    <span className="break-words">{riesgo}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </div>
      </section>

      <AccionesDecision productoId={producto.id} estado={producto.estado} />
      <CampanaMarketingPanel productoId={producto.id} estado={producto.estado} />
    </div>
  );
}
