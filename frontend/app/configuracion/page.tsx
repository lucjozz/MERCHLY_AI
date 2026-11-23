import { redirect } from "next/navigation";
import { Check, Link2, Lock, Settings, Mail, Share2, Search } from "lucide-react";
import BotonCerrarSesion from "@/components/BotonCerrarSesion";
import SesionInfo from "@/components/SesionInfo";
import { SesionInvalidaError } from "@/lib/api/errores";
import { obtenerUsuarioActual } from "@/lib/api/usuario";
import PageHeader from "@/components/ui/PageHeader";
import Card, { TituloCard } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Alerta, { MENSAJE_SIN_BACKEND } from "@/components/ui/Alerta";
import { etiquetaRol } from "@/lib/etiquetas";

export const dynamic = "force-dynamic";

const ROLES_NEGOCIO = [
  "admin_principal",
  "responsable_tecnico",
  "responsable_negocio",
];

const ACCIONES = [
  { nombre: "Investigar productos", roles: ROLES_NEGOCIO },
  {
    nombre: "Generar reportes de analítica",
    roles: [...ROLES_NEGOCIO, "usuario_operativo"],
  },
  { nombre: "Generar campañas de marketing", roles: ROLES_NEGOCIO },
  { nombre: "Aprobar o descartar productos", roles: ROLES_NEGOCIO },
  { nombre: "Borrar productos", roles: ["admin_principal", "responsable_negocio"] },
];

const CANALES = [
  { nombre: "Instagram", detalle: "Publicar campañas de redes sociales", icono: Share2 },
  { nombre: "Facebook", detalle: "Publicar campañas de redes sociales", icono: Share2 },
  { nombre: "Email", detalle: "Enviar campañas por correo", icono: Mail },
  { nombre: "Búsqueda paga", detalle: "Anuncios en buscadores", icono: Search },
];

export default async function Configuracion() {
  let usuario;
  let error: string | null = null;

  try {
    usuario = await obtenerUsuarioActual();
  } catch (e) {
    if (e instanceof SesionInvalidaError) redirect("/login");
    error = MENSAJE_SIN_BACKEND;
  }

  const rolActual = usuario?.rol ?? "";

  return (
    <>
      <PageHeader
        titulo="Configuración"
        icono={Settings}
        descripcion="Tu cuenta, tus permisos y los canales de venta."
      />

      {error && <Alerta>{error}</Alerta>}

      {usuario && (
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <div className="mb-6 flex items-center gap-4">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-acento to-acento-hondo text-xl font-bold text-white">
                {usuario.nombre.charAt(0).toUpperCase()}
              </div>
              <div className="min-w-0">
                <p className="truncate font-semibold text-texto">{usuario.nombre}</p>
                <p className="truncate text-sm text-texto-2">{usuario.email}</p>
              </div>
            </div>

            <dl className="space-y-3 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-texto-2">Rol</dt>
                <dd className="text-right text-texto">{etiquetaRol(usuario.rol)}</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-texto-2">Estado</dt>
                <dd>
                  <Badge tono={usuario.activo ? "verde" : "gris"} punto>
                    {usuario.activo ? "Activo" : "Inactivo"}
                  </Badge>
                </dd>
              </div>
            </dl>

            <div className="mt-6 border-t border-borde pt-6">
              <p className="mb-4 text-sm font-semibold text-texto">Tu sesión</p>
              <SesionInfo organizacion={usuario?.organizacion_nombre} />
            </div>

            <div className="mt-6 border-t border-borde pt-6">
              <BotonCerrarSesion />
            </div>
          </Card>

          <Card className="h-fit">
            <TituloCard descripcion={`Según tu rol: ${etiquetaRol(rolActual)}.`}>
              Qué podés hacer
            </TituloCard>
            <ul className="space-y-2">
              {ACCIONES.map((accion) => {
                const permitido = accion.roles.includes(rolActual);
                return (
                  <li
                    key={accion.nombre}
                    className="flex items-center gap-3 rounded-xl bg-fondo/60 px-3 py-2.5 text-sm"
                  >
                    {permitido ? (
                      <Check className="h-4 w-4 shrink-0 text-verde" aria-hidden="true" />
                    ) : (
                      <Lock className="h-4 w-4 shrink-0 text-texto-3" aria-hidden="true" />
                    )}
                    <span className={permitido ? "text-texto" : "text-texto-2"}>
                      {accion.nombre}
                      <span className="sr-only">{permitido ? " (permitido)" : " (no permitido)"}</span>
                    </span>
                  </li>
                );
              })}
            </ul>
          </Card>

          <Card className="lg:col-span-2">
            <TituloCard descripcion="Hoy el agente de Marketing solo propone contenido: no publica ni gasta. Conectar cuentas va a requerir la aprobación de una persona.">
              Canales de venta
            </TituloCard>
            <div className="grid gap-3 sm:grid-cols-2">
              {CANALES.map((canal) => {
                const Icono = canal.icono;
                return (
                  <div
                    key={canal.nombre}
                    className="flex items-center justify-between gap-3 rounded-xl border border-borde bg-fondo p-4"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-superficie-2 text-texto-2">
                        <Icono className="h-4 w-4" aria-hidden="true" />
                      </span>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-texto">{canal.nombre}</p>
                        <p className="text-xs text-texto-2">{canal.detalle}</p>
                      </div>
                    </div>
                    <button
                      disabled
                      className="inline-flex shrink-0 cursor-not-allowed items-center gap-1.5 rounded-lg border border-borde-fuerte px-3 py-1.5 text-xs text-texto-2"
                    >
                      <Link2 className="h-3.5 w-3.5" aria-hidden="true" />
                      Próximamente
                    </button>
                  </div>
                );
              })}
            </div>
          </Card>
        </div>
      )}
    </>
  );
}
