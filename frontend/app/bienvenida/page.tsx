import { redirect } from "next/navigation";
import { Sparkles } from "lucide-react";
import Card from "@/components/ui/Card";
import Alerta from "@/components/ui/Alerta";
import FormularioPerfil from "@/components/FormularioPerfil";
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
    <div className="mx-auto max-w-2xl py-6">
      <div className="mb-6 flex items-center gap-3">
        <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-acento to-acento-hondo">
          <Sparkles className="h-5 w-5 text-white" aria-hidden="true" />
        </span>
        <div>
          <h1 className="text-2xl font-bold text-texto">¡Bienvenido{nombre ? `, ${nombre}` : ""}!</h1>
          <p className="text-sm text-texto-2">Contanos de tu negocio y la IA va a buscar productos pensando en vos.</p>
        </div>
      </div>
      {error && <Alerta>{error}</Alerta>}
      {organizacion && (
        <Card>
          <FormularioPerfil organizacion={organizacion} destino="/productos" textoBoton="Empezar" />
          <p className="mt-5 text-xs text-texto-3">Podés cambiar todo esto después en Configuración.</p>
        </Card>
      )}
    </div>
  );
}
