import EncabezadoAtencion from "@/components/atencion/EncabezadoAtencion";
import FormularioAtencion from "@/components/atencion/FormularioAtencion";
import Alerta from "@/components/ui/Alerta";
import { listarQr, listarZonas, obtenerConfigAtencion } from "@/lib/api/atencion";
import type { AtencionConfig, QrPago, ZonaEnvio } from "@/lib/api/atencion-tipos";
import { obtenerOrganizacion } from "@/lib/api/organizacion";
import { obtenerUsuarioActual } from "@/lib/api/usuario";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

export default async function AtencionConfiguracion() {
  let config: AtencionConfig | null = null;
  let qrs: QrPago[] = [];
  let zonas: ZonaEnvio[] = [];
  let moneda = "BOB";
  let puedeEditar = false;
  let error: string | null = null;
  try {
    const [usuario, organizacion, c, q, z] = await Promise.all([
      obtenerUsuarioActual(),
      obtenerOrganizacion().catch(() => null),
      obtenerConfigAtencion(),
      listarQr(),
      listarZonas(),
    ]);
    config = c;
    qrs = q;
    zonas = z;
    moneda = organizacion?.moneda ?? "BOB";
    puedeEditar = ["admin_principal", "responsable_negocio"].includes(usuario.rol) && c.plan_incluye;
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }
  return (
    <>
      <EncabezadoAtencion actual="/atencion/configuracion" />
      {error && <Alerta>{error}</Alerta>}
      {config && <FormularioAtencion config={config} qrs={qrs} zonas={zonas} moneda={moneda} puedeEditar={puedeEditar} />}
    </>
  );
}
