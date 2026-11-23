import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, Megaphone } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Card from "@/components/ui/Card";
import Alerta from "@/components/ui/Alerta";
import { BadgeSimulado } from "@/components/ui/Badge";
import EditorCampana from "@/components/EditorCampana";
import { obtenerCampana, type CampanaDetalle } from "@/lib/api/campanas";
import { obtenerUsuarioActual } from "@/lib/api/usuario";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";
import { formatearFecha } from "@/lib/etiquetas";
import { ENLACE } from "@/components/ui/estilos";

export const dynamic = "force-dynamic";

const ROLES_EDICION = ["admin_principal", "responsable_tecnico", "responsable_negocio"];

export default async function DetalleCampana({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let campana: CampanaDetalle | null = null;
  let rol = "";
  let error: string | null = null;
  try {
    const [c, u] = await Promise.all([obtenerCampana(id), obtenerUsuarioActual()]);
    campana = c;
    rol = u.rol;
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }
  if (!error && !campana) notFound();

  return (
    <>
      <Link href="/campanas" className={`mb-4 ${ENLACE}`}>
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Volver a mis campañas
      </Link>
      <PageHeader
        titulo="Campaña"
        icono={Megaphone}
        descripcion={campana ? `Creada el ${formatearFecha(campana.creado_en)}` : ""}
        ayuda="Copiá cada texto o compartilo por WhatsApp o email. MERCHLY nunca publica por vos: vos decidís dónde y cuándo."
      />
      {error && <Alerta>{error}</Alerta>}
      {campana && (
        <Card>
          {campana.modelo === "simulado" && (
            <div className="mb-5 flex flex-wrap items-center gap-2 rounded-xl border border-dashed border-acento-borde bg-acento-hondo/20 px-4 py-3 text-sm text-texto-2">
              <BadgeSimulado /> Contenido de prueba generado sin IA real.
            </div>
          )}
          <EditorCampana campana={campana} puedeEditar={ROLES_EDICION.includes(rol)} />
        </Card>
      )}
    </>
  );
}
