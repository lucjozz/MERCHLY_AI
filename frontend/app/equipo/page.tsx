import Link from "next/link";
import { ShieldCheck, Users } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Alerta from "@/components/ui/Alerta";
import PanelEquipo from "@/components/PanelEquipo";
import { listarInvitaciones, listarMiembros, type Invitacion, type Miembro } from "@/lib/api/equipo";
import { obtenerUsuarioActual } from "@/lib/api/usuario";
import { SinPermisoError } from "@/lib/api/errores";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

export default async function Equipo() {
  let miembros: Miembro[] = [];
  let invitaciones: Invitacion[] = [];
  let miId = "";
  let error: string | null = null;
  try {
    const usuario = await obtenerUsuarioActual();
    miId = usuario.id;
    if (usuario.rol !== "admin_principal") throw new SinPermisoError("Solo el administrador del negocio puede gestionar el equipo.");
    [miembros, invitaciones] = await Promise.all([listarMiembros(), listarInvitaciones()]);
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  return (
    <>
      <PageHeader
        titulo="Equipo"
        icono={Users}
        descripcion="Invitá a tu socio o a tus empleados y elegí qué puede hacer cada uno."
        ayuda="Creás una invitación, copiás el link y se lo mandás. La persona entra, elige su contraseña y ya forma parte de tu negocio. Nadie puede cambiarse su propio rol."
        acciones={
          <Link href="/equipo/actividad" className="inline-flex items-center gap-2 rounded-lg border border-borde px-4 py-2 text-sm text-texto-2 hover:text-texto">
            <ShieldCheck className="h-4 w-4" aria-hidden="true" /> Actividad de seguridad
          </Link>
        }
      />
      {error ? <Alerta>{error}</Alerta> : <PanelEquipo miembros={miembros} invitaciones={invitaciones} miId={miId} />}
    </>
  );
}
