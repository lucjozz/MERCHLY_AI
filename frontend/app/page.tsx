import { obtenerReporteAnalitica } from "@/lib/api/analitica";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import Link from "next/link";
import {
  Package,
  CircleCheck,
  Hourglass,
  CircleSlash,
  Search,
  Inbox,
  Tags,
  ArrowRight,
  LayoutDashboard,
} from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Card, { TituloCard } from "@/components/ui/Card";
import Metrica from "@/components/ui/Metrica";
import EmptyState from "@/components/ui/EmptyState";
import Alerta from "@/components/ui/Alerta";
import Badge from "@/components/ui/Badge";
import { BOTON_PRIMARIO, ENLACE } from "@/components/ui/estilos";
import RecorridoGuiado from "@/components/RecorridoGuiado";
import TarjetaProducto from "@/components/TarjetaProducto";
import { plural } from "@/lib/etiquetas";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";
import { redirect } from "next/navigation";
import UsoDelPlan from "@/components/UsoDelPlan";
import ProximasTemporadas from "@/components/ProximasTemporadas";
import { obtenerTemporadas, type Temporada } from "@/lib/api/temporadas";
import { obtenerOrganizacion, obtenerUsoPlan, type UsoPlan } from "@/lib/api/organizacion";
import { obtenerUsuarioActual } from "@/lib/api/usuario";

export const dynamic = "force-dynamic";

export default async function Dashboard() {
  let reporte;
  let recientes;
  let uso: UsoPlan | null = null;
  let temporadas: Temporada[] = [];
  let esBolivia = false;
  let irAOnboarding = false;
  let error: string | null = null;

  try {
    const [usuario, organizacion] = await Promise.all([obtenerUsuarioActual(), obtenerOrganizacion()]);
    // Primer ingreso del admin: completar el perfil del negocio.
    esBolivia = organizacion.pais === "BO";
    irAOnboarding = usuario.rol === "admin_principal" && !organizacion.onboarding_completo;
    if (!irAOnboarding) {
      [reporte, recientes, uso] = await Promise.all([
        obtenerReporteAnalitica(),
        listarProductosCandidatos(1, 5, undefined, "candidato"),
        obtenerUsoPlan().catch(() => null),
      ]);
      if (esBolivia) temporadas = await obtenerTemporadas();
    }
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }
  if (irAOnboarding) redirect("/bienvenida");

  const conversion = reporte?.tasa_conversion_catalogo;
  const actividad = reporte?.actividad_agente_investigador;

  return (
    <>
      <PageHeader
        titulo="Hola, este es tu panel"
        icono={LayoutDashboard}
        descripcion="Un resumen de lo que encontró la IA y de lo que está esperando tu decisión."
        acciones={
          <Link href="/productos" className={BOTON_PRIMARIO}>
            <Search className="h-4 w-4" aria-hidden="true" />
            Buscar productos con IA
          </Link>
        }
      />

      {error && <Alerta>{error}</Alerta>}

      {uso && (
        <div className="mb-8">
          <UsoDelPlan uso={uso} />
        </div>
      )}

      {reporte && conversion && actividad && (
        <div className="space-y-8">
          <RecorridoGuiado
            investigaciones={actividad.total_investigaciones}
            porRevisar={conversion.candidato}
            aprobados={conversion.en_catalogo}
            descartados={conversion.descartado}
          />

          <ProximasTemporadas temporadas={temporadas} />

          <section aria-labelledby="titulo-numeros">
            <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
              <h2 id="titulo-numeros" className="text-base font-semibold text-texto">
                Tus números
              </h2>
              <p className="text-xs text-texto-2">Últimos 30 días</p>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
              <Metrica
                etiqueta="Productos encontrados"
                valor={reporte.resumen_catalogo.total_productos_candidatos}
                icono={Package}
                color="azul"
                detalle="Sugeridos por la IA"
              />
              <Metrica
                etiqueta="Por revisar"
                valor={conversion.candidato}
                icono={Hourglass}
                color="ambar"
                detalle="Esperan tu decisión"
                retraso={60}
              />
              <Metrica
                etiqueta="En catálogo"
                valor={conversion.en_catalogo}
                icono={CircleCheck}
                color="verde"
                detalle="Aprobados por vos"
                retraso={120}
              />
              <Metrica
                etiqueta="Descartados"
                valor={conversion.descartado}
                icono={CircleSlash}
                color="gris"
                detalle="No avanzan"
                retraso={180}
              />
            </div>
          </section>

          <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
            <Card as="section" aria-label="Requiere tu atención">
              <TituloCard
                descripcion="Productos que la IA sugirió y todavía no revisaste."
                accion={
                  conversion.candidato > 0 ? (
                    <Badge tono="ambar" punto>
                      {plural(conversion.candidato, "pendiente")}
                    </Badge>
                  ) : undefined
                }
              >
                Requiere tu atención
              </TituloCard>

              {recientes && recientes.productos.length === 0 && (
                <EmptyState
                  compacto
                  icono={Inbox}
                  titulo="Estás al día"
                  descripcion="No hay productos esperando tu decisión. Buscá una categoría nueva para que la IA te sugiera más."
                  accion={{ href: "/productos", texto: "Buscar productos" }}
                />
              )}

              {recientes && recientes.productos.length > 0 && (
                <>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {recientes.productos.map((producto, i) => (
                      <TarjetaProducto key={producto.id} producto={producto} retraso={i * 60} />
                    ))}
                  </div>
                  {recientes.total > recientes.productos.length && (
                    <Link href="/productos?estado=candidato" className={`mt-5 ${ENLACE}`}>
                      Ver los {recientes.total} pendientes
                      <ArrowRight className="h-4 w-4" aria-hidden="true" />
                    </Link>
                  )}
                </>
              )}
            </Card>

            <Card as="section" aria-label="Categorías más investigadas" className="h-fit">
              <TituloCard descripcion="Lo que más le pediste investigar a la IA.">
                Categorías más buscadas
              </TituloCard>

              {actividad.categorias_mas_investigadas.length === 0 ? (
                <EmptyState
                  compacto
                  icono={Tags}
                  titulo="Todavía no investigaste nada"
                  descripcion="Escribí una categoría como “mochilas antirrobo” y la IA te sugiere productos."
                />
              ) : (
                <ol className="space-y-2">
                  {actividad.categorias_mas_investigadas.map((categoria, i) => (
                    <li key={categoria}>
                      <Link
                        href={`/productos?categoria=${encodeURIComponent(categoria)}`}
                        className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm text-texto transition-colors hover:bg-superficie-2"
                      >
                        <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-acento-hondo text-xs font-semibold text-acento-claro">
                          {i + 1}
                        </span>
                        <span className="min-w-0 flex-1 truncate">{categoria}</span>
                        <ArrowRight className="h-4 w-4 text-texto-2" aria-hidden="true" />
                      </Link>
                    </li>
                  ))}
                </ol>
              )}

              <div className="mt-5 border-t border-borde pt-4 text-xs leading-relaxed text-texto-2">
                {plural(actividad.total_investigaciones, "búsqueda")} con IA ·{" "}
                {actividad.promedio_productos_por_investigacion} productos por búsqueda
                en promedio
              </div>
            </Card>
          </div>
        </div>
      )}
    </>
  );
}
