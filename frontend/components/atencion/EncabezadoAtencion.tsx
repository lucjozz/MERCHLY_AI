/** Encabezado común de las pantallas de atención al cliente. */
import { Headset } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import NavAtencion from "@/components/atencion/NavAtencion";

export default function EncabezadoAtencion({ actual, sinLeer }: { actual: string; sinLeer?: number }) {
  return (
    <>
      <PageHeader
        titulo="Atención al cliente"
        icono={Headset}
        descripcion="Tu asistente responde a tus clientes con tu catálogo público: precios, stock y envíos reales. Arma pedidos y te avisa; el pago lo confirmás siempre vos."
      />
      <NavAtencion actual={actual} sinLeer={sinLeer} />
    </>
  );
}
