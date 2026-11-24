import EncabezadoAtencion from "@/components/atencion/EncabezadoAtencion";
import ChatSimulador from "@/components/atencion/ChatSimulador";
import Alerta from "@/components/ui/Alerta";
import { obtenerConfigAtencion } from "@/lib/api/atencion";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

export default async function AtencionSimulador() {
  let proveedor = "simulado";
  let incluye = true;
  let error: string | null = null;
  try {
    const config = await obtenerConfigAtencion();
    proveedor = config.proveedor;
    incluye = config.plan_incluye;
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }
  return (
    <>
      <EncabezadoAtencion actual="/atencion/simulador" />
      {error && <Alerta>{error}</Alerta>}
      {!error && !incluye && <Alerta tipo="info">Tu plan no incluye el asistente de atención al cliente.</Alerta>}
      {!error && incluye && <ChatSimulador proveedor={proveedor} />}
    </>
  );
}
