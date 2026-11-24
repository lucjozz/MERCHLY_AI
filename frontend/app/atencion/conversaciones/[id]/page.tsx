import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import EncabezadoAtencion from "@/components/atencion/EncabezadoAtencion";
import ConversacionVista from "@/components/atencion/ConversacionVista";
import Alerta from "@/components/ui/Alerta";
import { ENLACE } from "@/components/ui/estilos";
import { obtenerConversacion } from "@/lib/api/atencion";
import type { ConversacionDetalle } from "@/lib/api/atencion-tipos";
import { ApiError } from "@/lib/api/errores";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

export default async function AtencionConversacion({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^[0-9a-fA-F-]{36}$/.test(id)) notFound();
  let conversacion: ConversacionDetalle | null = null;
  let error: string | null = null;
  let noExiste = false;
  try {
    conversacion = await obtenerConversacion(id);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) noExiste = true;
    else error = mensajeDeErrorDePagina(e);
  }
  if (noExiste) notFound();
  return (
    <>
      <EncabezadoAtencion actual="/atencion/conversaciones" />
      <Link href="/atencion/conversaciones" className={`mb-4 ${ENLACE}`}>
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Volver a conversaciones
      </Link>
      {error && <Alerta>{error}</Alerta>}
      {conversacion && (
        <>
          <h2 className="mb-3 text-lg font-semibold text-texto">{conversacion.nombre_contacto ?? conversacion.contacto}</h2>
          <ConversacionVista conversacion={conversacion} />
        </>
      )}
    </>
  );
}
