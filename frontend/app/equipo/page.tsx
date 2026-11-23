import { Users } from "lucide-react";
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
      />
      {error ? <Alerta>{error}</Alerta> : <PanelEquipo miembros={miembros} invitaciones={invitaciones} miId={miId} />}
    </>
  );
}
