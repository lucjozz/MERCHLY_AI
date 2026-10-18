import { redirect } from "next/navigation";
import { Check, Link2, Lock } from "lucide-react";
import BotonCerrarSesion from "@/components/BotonCerrarSesion";
import SesionInfo from "@/components/SesionInfo";
import { SesionInvalidaError } from "@/lib/api/errores";
import { obtenerUsuarioActual } from "@/lib/api/usuario";

export const dynamic = "force-dynamic";

const ETIQUETA_ROL: Record<string, string> = {
  admin_principal: "Administrador principal",
  responsable_tecnico: "Responsable técnico",
  responsable_negocio: "Responsable de negocio",
  usuario_operativo: "Usuario operativo",
};

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
];

const CANALES = [
  { nombre: "Instagram", detalle: "Publicar campañas de redes sociales" },
  { nombre: "Facebook", detalle: "Publicar campañas de redes sociales" },
  { nombre: "Email", detalle: "Enviar campañas por correo" },
  { nombre: "Búsqueda paga", detalle: "Anuncios en buscadores" },
];

export default async function Configuracion() {
  let usuario;
  let error: string | null = null;

  try {
    usuario = await obtenerUsuarioActual();
  } catch (e) {
    if (e instanceof SesionInvalidaError) redirect("/login");
    error = "No se pudo conectar con el backend. ¿Está corriendo?";
  }

  const rolActual = usuario?.rol ?? "";

  return (
    <div className="px-10 py-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-[#F5F7FA]">Configuración</h1>
        <p className="text-[#7C8699] mt-1">
          Tu sesión, tus permisos y los canales del sistema.
        </p>
      </header>

      {error && (
        <div className="bg-[#2A1414] border border-[#4A2020] text-[#E88B8B] rounded-lg p-4 text-sm">
          {error}
        </div>
      )}

      {usuario && (
        <div className="grid grid-cols-2 gap-6 max-w-4xl">
          <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="h-12 w-12 rounded-full bg-[#1E3A5F] flex items-center justify-center text-lg font-bold text-[#F5F7FA]">
                {usuario.nombre.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-[#F5F7FA] font-semibold">{usuario.nombre}</p>
                <p className="text-[#7C8699] text-sm">{usuario.email}</p>
              </div>
            </div>

            <dl className="space-y-4 text-sm">
              <div className="flex justify-between">
                <dt className="text-[#7C8699]">Rol</dt>
                <dd className="text-[#F5F7FA]">
                  {ETIQUETA_ROL[usuario.rol] ?? usuario.rol}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-[#7C8699]">Estado</dt>
                <dd className="text-[#4ADE80]">
                  {usuario.activo ? "Activo" : "Inactivo"}
                </dd>
              </div>
            </dl>

            <div className="border-t border-[#1F2430] mt-6 pt-6">
              <p className="text-[#7C8699] text-xs uppercase tracking-wide mb-4">
                Sesión
              </p>
              <SesionInfo />
            </div>

            <div className="border-t border-[#1F2430] mt-6 pt-6">
              <BotonCerrarSesion />
            </div>
          </div>

          <div className="bg-[#12151C] border border-[#1F2430] rounded-lg p-6 h-fit">
            <h2 className="text-lg font-semibold text-[#F5F7FA] mb-5">
              Qué podés hacer
            </h2>
            <ul className="space-y-4">
              {ACCIONES.map((accion) => {
                const permitido = accion.roles.includes(rolActual);
                return (
                  <li key={accion.nombre} className="flex items-center gap-3 text-sm">
                    {permitido ? (
                      <Check className="h-4 w-4 text-[#4ADE80]" aria-hidden="true" />
                    ) : (
                      <Lock className="h-4 w-4 text-[#5B6272]" aria-hidden="true" />
                    )}
                    <span className={permitido ? "text-[#F5F7FA]" : "text-[#5B6272]"}>
                      {accion.nombre}
                    </span>
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="col-span-2 bg-[#12151C] border border-[#1F2430] rounded-lg p-6">
            <h2 className="text-lg font-semibold text-[#F5F7FA] mb-1">
              Canales
            </h2>
            <p className="text-[#7C8699] text-sm mb-5">
              Hoy el agente de Marketing solo propone contenido: no publica ni
              gasta. Vincular cuentas requiere un contrato nuevo, aprobado por una
              persona.
            </p>
            <div className="grid grid-cols-2 gap-3">
              {CANALES.map((canal) => (
                <div
                  key={canal.nombre}
                  className="bg-[#0B0D12] border border-[#1F2430] rounded-md p-4 flex items-center justify-between"
                >
                  <div>
                    <p className="text-[#F5F7FA] text-sm font-medium">
                      {canal.nombre}
                    </p>
                    <p className="text-[#5B6272] text-xs mt-0.5">{canal.detalle}</p>
                  </div>
                  <button
                    disabled
                    className="inline-flex items-center gap-1.5 text-xs text-[#5B6272] border border-[#242938] rounded-md px-3 py-1.5 cursor-not-allowed"
                  >
                    <Link2 className="h-3.5 w-3.5" aria-hidden="true" />
                    Próximamente
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}