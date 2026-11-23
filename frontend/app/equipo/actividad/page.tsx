import Link from "next/link";
import {
  ArrowLeft, KeyRound, LogIn, LogOut, ShieldAlert, ShieldCheck, Trash2, UserCog, UserMinus, UserPlus, Settings,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Alerta from "@/components/ui/Alerta";
import EmptyState from "@/components/ui/EmptyState";
import { listarEventos, type EventoAuditoria, type EventosListado } from "@/lib/api/auditoria";
import { obtenerUsuarioActual } from "@/lib/api/usuario";
import { SinPermisoError } from "@/lib/api/errores";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";
import { etiquetaRol, formatearFecha } from "@/lib/etiquetas";
import { ENLACE } from "@/components/ui/estilos";

export const dynamic = "force-dynamic";

const ACCIONES: Record<string, { texto: string; icono: LucideIcon; tono: string }> = {
  login_ok: { texto: "Inició sesión", icono: LogIn, tono: "text-verde" },
  login_fallido: { texto: "Intento de inicio de sesión fallido", icono: ShieldAlert, tono: "text-rojo" },
  login_google: { texto: "Inició sesión con Google", icono: LogIn, tono: "text-verde" },
  registro_google: { texto: "Creó su cuenta con Google", icono: UserPlus, tono: "text-verde" },
  logout: { texto: "Cerró sesión", icono: LogOut, tono: "text-texto-2" },
  sesiones_cerradas: { texto: "Cerró sesión en todos sus dispositivos", icono: LogOut, tono: "text-ambar" },
  password_restablecimiento_pedido: { texto: "Pidió restablecer su contraseña", icono: KeyRound, tono: "text-ambar" },
  password_restablecida: { texto: "Cambió su contraseña con el link del email", icono: KeyRound, tono: "text-ambar" },
  invitacion_creada: { texto: "Invitó a una persona", icono: UserPlus, tono: "text-acento-claro" },
  invitacion_revocada: { texto: "Revocó una invitación", icono: UserMinus, tono: "text-texto-2" },
  invitacion_aceptada: { texto: "Se unió al equipo", icono: UserPlus, tono: "text-verde" },
  rol_cambiado: { texto: "Cambió un rol", icono: UserCog, tono: "text-ambar" },
  usuario_desactivado: { texto: "Desactivó a un miembro", icono: UserMinus, tono: "text-rojo" },
  usuario_reactivado: { texto: "Reactivó a un miembro", icono: UserPlus, tono: "text-verde" },
  producto_borrado: { texto: "Borró un producto", icono: Trash2, tono: "text-rojo" },
  campana_borrada: { texto: "Borró una campaña", icono: Trash2, tono: "text-rojo" },
  perfil_actualizado: { texto: "Actualizó el perfil del negocio", icono: Settings, tono: "text-acento-claro" },
};

const FILTROS: [string, string][] = [
  ["", "Todo"],
  ["login_fallido", "Intentos fallidos"],
  ["rol_cambiado", "Cambios de rol"],
  ["usuario_desactivado", "Desactivaciones"],
  ["producto_borrado", "Productos borrados"],
];

function descripcion(e: EventoAuditoria): string {
  const d = e.detalle;
  if (e.accion === "rol_cambiado") return `${d.miembro ?? "Un miembro"}: ${etiquetaRol(String(d.antes))} → ${etiquetaRol(String(d.despues))}`;
  if (e.accion === "usuario_desactivado" || e.accion === "usuario_reactivado") return String(d.miembro ?? "");
  if (e.accion === "invitacion_creada" || e.accion === "invitacion_aceptada") return d.rol ? `Rol: ${etiquetaRol(String(d.rol))}` : "";
  if (e.accion === "perfil_actualizado") return d.dolar === "bcb" ? "Dólar: oficial del BCB" : d.dolar === "propio" ? "Dólar: propio" : "";
  return "";
}

export default async function ActividadSeguridad({ searchParams }: { searchParams: Promise<{ accion?: string }> }) {
  const { accion } = await searchParams;
  let datos: EventosListado | null = null;
  let error: string | null = null;
  try {
    const usuario = await obtenerUsuarioActual();
    if (usuario.rol !== "admin_principal") throw new SinPermisoError("Solo el administrador del negocio puede ver la actividad de seguridad.");
    datos = await listarEventos(1, accion);
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  return (
    <>
      <Link href="/equipo" className={`mb-4 ${ENLACE}`}>
        <ArrowLeft className="h-4 w-4" aria-hidden="true" /> Volver a Equipo
      </Link>
      <PageHeader
        titulo="Actividad de seguridad"
        icono={ShieldCheck}
        descripcion="Quién entró, quién cambió permisos y quién borró qué en tu negocio."
        ayuda="Este registro no se puede editar ni borrar. Si ves intentos fallidos que no reconocés o cambios que nadie de tu equipo hizo, cambiá tu contraseña y escribinos."
      />
      {error && <Alerta>{error}</Alerta>}
      {datos && (
        <>
          <nav aria-label="Filtrar actividad" className="mb-4 flex flex-wrap gap-2">
            {FILTROS.map(([valor, texto]) => {
              const activo = (accion ?? "") === valor;
              return (
                <Link
                  key={valor}
                  href={valor ? `/equipo/actividad?accion=${valor}` : "/equipo/actividad"}
                  aria-current={activo ? "page" : undefined}
                  className={`rounded-full border px-3 py-1.5 text-xs ${activo ? "border-acento bg-acento-hondo/40 text-texto" : "border-borde text-texto-2 hover:text-texto"}`}
                >
                  {texto}
                </Link>
              );
            })}
          </nav>
          {datos.eventos.length === 0 ? (
            <EmptyState icono={ShieldCheck} titulo="Sin actividad para mostrar" descripcion="Cuando tu equipo inicie sesión o haga cambios, lo vas a ver acá." />
          ) : (
            <ul className="divide-y divide-borde rounded-2xl border border-borde bg-superficie">
              {datos.eventos.map((e) => {
                const info = ACCIONES[e.accion] ?? { texto: e.accion, icono: ShieldCheck, tono: "text-texto-2" };
                const Icono = info.icono;
                const extra = descripcion(e);
                return (
                  <li key={e.id} className="flex items-start gap-3 p-4">
                    <Icono className={`mt-0.5 h-4 w-4 shrink-0 ${info.tono}`} aria-hidden="true" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm text-texto">
                        <span className="font-medium">{e.usuario_nombre ?? "Alguien"}</span> · {info.texto}
                      </p>
                      {extra && <p className="text-xs text-texto-2">{extra}</p>}
                    </div>
                    <div className="shrink-0 text-right text-xs text-texto-3">
                      <p>{formatearFecha(e.creado_en)}</p>
                      {e.ip && <p className="font-mono">{e.ip}</p>}
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
          {datos.total > datos.eventos.length && (
            <p className="mt-3 text-xs text-texto-3">Mostrando los {datos.eventos.length} eventos más recientes de {datos.total}.</p>
          )}
        </>
      )}
    </>
  );
}
