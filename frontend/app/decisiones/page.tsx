import Link from "next/link";
import { Scale, CircleCheck, CircleSlash, Percent, ArrowRight, Inbox } from "lucide-react";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import PageHeader from "@/components/ui/PageHeader";
import Metrica from "@/components/ui/Metrica";
import EmptyState from "@/components/ui/EmptyState";
import Alerta from "@/components/ui/Alerta";
import { BadgeEstado, BadgeSimulado } from "@/components/ui/Badge";
import {
  esProductoSimulado,
  etiquetaMercado,
  formatearFecha,
  nombreLimpio,
} from "@/lib/etiquetas";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

export default async function Decisiones() {
  let aprobados;
  let descartados;
  let error: string | null = null;

  try {
    [aprobados, descartados] = await Promise.all([
      listarProductosCandidatos(1, 100, undefined, "en_catalogo"),
      listarProductosCandidatos(1, 100, undefined, "descartado"),
    ]);
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  const decididos = [
    ...(aprobados?.productos ?? []),
    ...(descartados?.productos ?? []),
  ].sort(
    (a, b) => new Date(b.creado_en).getTime() - new Date(a.creado_en).getTime()
  );

  const totalAprobados = aprobados?.total ?? 0;
  const totalDescartados = descartados?.total ?? 0;
  const totalDecididos = totalAprobados + totalDescartados;
  const tasa =
    totalDecididos > 0 ? Math.round((totalAprobados / totalDecididos) * 100) : 0;

  return (
    <>
      <PageHeader
        titulo="Decisiones"
        icono={Scale}
        descripcion="Los productos sobre los que una persona ya decidió."
        ayuda="Acá ves qué aprobaste y qué descartaste. Cada decisión queda registrada con su motivo y su responsable en la bitácora (el motivo todavía no se puede consultar desde esta pantalla)."
      />

      {error && <Alerta>{error}</Alerta>}

      {!error && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-3">
            <Metrica etiqueta="Aprobados" valor={totalAprobados} icono={CircleCheck} color="verde" detalle="Entraron a tu catálogo" />
            <Metrica etiqueta="Descartados" valor={totalDescartados} icono={CircleSlash} color="gris" detalle="No avanzan" retraso={60} />
            <div className="col-span-2 lg:col-span-1">
              <Metrica
                etiqueta="Tasa de aprobación"
                valor={`${tasa}%`}
                icono={Percent}
                color="azul"
                detalle="De lo que decidiste, cuánto aprobaste"
                retraso={120}
              />
            </div>
          </div>

          {decididos.length === 0 && (
            <EmptyState
              icono={Inbox}
              titulo="Todavía no tomaste decisiones"
              descripcion="Abrí un producto que esté “Por revisar”, mirá la evidencia y aprobalo o descartalo."
              accion={{ href: "/productos?estado=candidato", texto: "Revisar productos" }}
            />
          )}

          {decididos.length > 0 && (
            <section aria-labelledby="titulo-historial">
              <h2 id="titulo-historial" className="mb-3 text-base font-semibold text-texto">
                Historial
              </h2>
              <ul className="divide-y divide-borde overflow-hidden rounded-2xl border border-borde bg-superficie">
                {decididos.map((producto, i) => (
                  <li key={producto.id} className="animate-aparecer" style={{ animationDelay: `${Math.min(i, 10) * 30}ms` }}>
                    <Link
                      href={`/productos/${producto.id}`}
                      className="group flex flex-col gap-2 p-4 transition-colors hover:bg-superficie-2 sm:flex-row sm:items-center sm:gap-4 sm:px-5"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-texto transition-colors group-hover:text-acento-claro">
                          {nombreLimpio(producto.nombre_producto)}
                        </p>
                        <p className="mt-0.5 text-sm text-texto-2">
                          {producto.categoria} · {etiquetaMercado(producto.mercado_objetivo)}
                        </p>
                      </div>
                      <div className="flex flex-wrap items-center gap-2">
                        <BadgeEstado estado={producto.estado} />
                        {esProductoSimulado(producto) && <BadgeSimulado />}
                      </div>
                      <p className="text-xs text-texto-2 sm:w-40 sm:text-right">
                        Encontrado el {formatearFecha(producto.creado_en)}
                      </p>
                      <ArrowRight className="hidden h-4 w-4 text-texto-2 transition-transform group-hover:translate-x-0.5 sm:block" aria-hidden="true" />
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </>
  );
}
