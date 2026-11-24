import EncabezadoAtencion from "@/components/atencion/EncabezadoAtencion";
import PanelPedidos from "@/components/atencion/PanelPedidos";
import Alerta from "@/components/ui/Alerta";
import { listarNotificaciones, listarPedidos } from "@/lib/api/atencion";
import type { Notificacion, Pedido } from "@/lib/api/atencion-tipos";
import { obtenerOrganizacion } from "@/lib/api/organizacion";
import { obtenerUsuarioActual } from "@/lib/api/usuario";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

export default async function AtencionPedidos() {
  let pedidos: Pedido[] = [];
  let avisos: Notificacion[] = [];
  let sinLeer = 0;
  let moneda = "BOB";
  let puedeDecidir = false;
  let conDosPasos = false;
  let error: string | null = null;
  try {
    const [usuario, organizacion, lista, notificaciones] = await Promise.all([
      obtenerUsuarioActual(),
      obtenerOrganizacion().catch(() => null),
      listarPedidos(),
      listarNotificaciones(),
    ]);
    pedidos = lista;
    avisos = notificaciones.notificaciones;
    sinLeer = notificaciones.sin_leer;
    moneda = organizacion?.moneda ?? "BOB";
    puedeDecidir = ["admin_principal", "responsable_negocio"].includes(usuario.rol);
    conDosPasos = Boolean(usuario.totp_activado);
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }
  return (
    <>
      <EncabezadoAtencion actual="/atencion" sinLeer={sinLeer} />
      {error ? (
        <Alerta>{error}</Alerta>
      ) : (
        <PanelPedidos pedidos={pedidos} avisos={avisos} sinLeer={sinLeer} moneda={moneda} puedeDecidir={puedeDecidir} conDosPasos={conDosPasos} />
      )}
    </>
  );
}
