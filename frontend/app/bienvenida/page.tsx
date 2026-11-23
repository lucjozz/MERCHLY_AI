import { redirect } from "next/navigation";
import Alerta from "@/components/ui/Alerta";
import OnboardingPasoAPaso from "@/components/OnboardingPasoAPaso";
import { obtenerOrganizacion, type Organizacion } from "@/lib/api/organizacion";
import { obtenerUsuarioActual } from "@/lib/api/usuario";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

/** Primer ingreso del admin: contanos de tu negocio y la IA busca con ese contexto. */
export default async function Bienvenida() {
  let organizacion: Organizacion | null = null;
  let esAdmin = false;
  let nombre = "";
  let error: string | null = null;
  try {
    const [o, u] = await Promise.all([obtenerOrganizacion(), obtenerUsuarioActual()]);
    organizacion = o;
    esAdmin = u.rol === "admin_principal";
    nombre = u.nombre.split(" ")[0];
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }
  if (organizacion && !esAdmin) redirect("/");

  return (
    <>
      {error && <Alerta>{error}</Alerta>}
      {organizacion && <OnboardingPasoAPaso organizacion={organizacion} nombrePersona={nombre} />}
    </>
  );
}
