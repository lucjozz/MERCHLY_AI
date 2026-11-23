import Link from "next/link";
import { History, Megaphone } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Alerta from "@/components/ui/Alerta";
import EmptyState from "@/components/ui/EmptyState";
import { listarCampanas, type CampanasListado } from "@/lib/api/campanas";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";
import { etiquetaCanal, haceCuanto } from "@/lib/etiquetas";

export const dynamic = "force-dynamic";

export default async function Campanas() {
  let datos: CampanasListado | null = null;
  let error: string | null = null;
  try {
    datos = await listarCampanas();
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  return (
    <>
      <PageHeader
        titulo="Mis campañas"
        icono={History}
        descripcion="Todas las campañas que generaste, guardadas para verlas, editarlas y compartirlas."
        ayuda="Cada vez que generás una campaña se guarda acá automáticamente. Abrila para editar los textos y compartirlos por WhatsApp o email."
      />
      {error && <Alerta>{error}</Alerta>}
      {datos && datos.campanas.length === 0 && (
        <EmptyState
          icono={Megaphone}
          titulo="Todavía no generaste campañas"
          descripcion="Aprobá un producto y generá su campaña desde el detalle o desde Marketing. Va a aparecer acá."
          accion={{ href: "/marketing", texto: "Ir a Marketing" }}
        />
      )}
      {datos && datos.campanas.length > 0 && (
        <ul className="grid gap-3 md:grid-cols-2">
          {datos.campanas.map((c) => (
            <li key={c.id}>
              <Link href={`/campanas/${c.id}`} className="block focus-visible:outline-2">
                <Card interactiva>
                  <div className="flex items-start justify-between gap-3">
                    <p className="min-w-0 break-words font-semibold text-texto">{c.titulo}</p>
                    {c.editada && <Badge tono="azul">Editada</Badge>}
                  </div>
                  <p className="mt-2 text-sm text-texto-2">{c.canales.map(etiquetaCanal).join(" · ")}</p>
                  <p className="mt-3 text-xs text-texto-3">
                    {haceCuanto(c.creado_en)}
                    {c.modelo ? ` · IA: ${c.modelo === "simulado" ? "simulada" : c.modelo}` : ""}
                  </p>
                </Card>
              </Link>
            </li>
          ))}
        </ul>
      )}
      {datos && datos.total > datos.campanas.length && (
        <p className="mt-4 text-sm text-texto-2">Mostrando las {datos.campanas.length} más recientes de {datos.total}.</p>
      )}
    </>
  );
}
