import { redirect } from "next/navigation";
import Link from "next/link";
import { Check, Lock, Settings, Mail, Share2, Search, MessageCircle, ArrowRight, Users } from "lucide-react";
import FormularioPerfil from "@/components/FormularioPerfil";
import { obtenerOrganizacion, type Organizacion } from "@/lib/api/organizacion";
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

/** Canales de venta: estado REAL de cada uno (docs/004-Backend/03, sección 2). */
const CANALES = [
  { nombre: "WhatsApp", detalle: "Compartí cada texto con un toque desde tus campañas.", icono: MessageCircle, activo: true },
  { nombre: "Email", detalle: "Abre tu correo con el texto listo para enviar.", icono: Mail, activo: true },
  { nombre: "Instagram y Facebook", detalle: "Copiá el texto y pegalo en tu publicación. La conexión directa requiere aprobación de Meta.", icono: Share2, activo: true },
  { nombre: "Búsqueda paga", detalle: "Copiá los textos para tus anuncios. La conexión con Google Ads llega más adelante.", icono: Search, activo: true },
];

export default async function Configuracion() {
  let usuario;
  let error: string | null = null;

  let organizacion: Organizacion | null = null;
  try {
    [usuario, organizacion] = await Promise.all([obtenerUsuarioActual(), obtenerOrganizacion()]);
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
            <TituloCard
              descripcion="MERCHLY nunca publica por vos: desde cada campaña copiás o compartís el texto y decidís dónde y cuándo."
              accion={
                <Link href="/campanas" className="inline-flex items-center gap-1 text-sm text-acento-claro hover:underline">
                  Mis campañas <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>
              }
            >
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
                    <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-verde-borde bg-verde-fondo px-2.5 py-1 text-xs text-verde">
                      <Check className="h-3.5 w-3.5" aria-hidden="true" />
                      Listo
                    </span>
                  </div>
                );
              })}
            </div>
          </Card>

          {organizacion && (
            <Card className="lg:col-span-2">
              <TituloCard
                descripcion="La IA usa estos datos para buscar productos pensando en tu negocio, y los precios se muestran en tu moneda."
                accion={
                  rolActual === "admin_principal" ? (
                    <Link href="/equipo" className="inline-flex items-center gap-1 text-sm text-acento-claro hover:underline">
                      <Users className="h-4 w-4" aria-hidden="true" /> Equipo
                    </Link>
                  ) : undefined
                }
              >
                Tu negocio
              </TituloCard>
              {rolActual === "admin_principal" ? (
                <FormularioPerfil organizacion={organizacion} />
              ) : (
                <dl className="grid gap-3 text-sm sm:grid-cols-2">
                  <div><dt className="text-texto-2">Negocio</dt><dd className="text-texto">{organizacion.nombre}</dd></div>
                  <div><dt className="text-texto-2">Rubro</dt><dd className="text-texto">{organizacion.rubro ?? "—"}</dd></div>
                  <div><dt className="text-texto-2">Moneda</dt><dd className="text-texto">{organizacion.moneda === "BOB" ? "Bolivianos" : "Dólares"}</dd></div>
                  <div><dt className="text-texto-2">Tipo de cambio</dt><dd className="text-texto">{organizacion.tipo_cambio ?? "—"}</dd></div>
                  <p className="text-xs text-texto-3 sm:col-span-2">Solo el administrador del negocio puede cambiar estos datos.</p>
                </dl>
              )}
            </Card>
          )}
        </div>
      )}
    </>
  );
}
