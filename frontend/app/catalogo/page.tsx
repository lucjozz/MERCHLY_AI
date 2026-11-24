import { MessageCircle } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Alerta from "@/components/ui/Alerta";
import EmptyState from "@/components/ui/EmptyState";
import CatalogoWhatsApp from "@/components/CatalogoWhatsApp";
import { listarProductosCandidatos, type ProductoCandidato } from "@/lib/api/productos-candidatos";
import { obtenerOrganizacion, type Organizacion } from "@/lib/api/organizacion";
import { obtenerTipoCambioBcb, tipoCambioEfectivo, type TipoCambioBcb } from "@/lib/api/tipo-cambio";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";
import { nombreLimpio } from "@/lib/etiquetas";

export const dynamic = "force-dynamic";

/** Catálogo listo para WhatsApp (docs/004-Backend/05, sección 2): solo productos aprobados por una persona. */
export default async function Catalogo() {
  let productos: ProductoCandidato[] = [];
  let organizacion: Organizacion | null = null;
  let bcb: TipoCambioBcb | null = null;
  let error: string | null = null;
  try {
    const [listado, org, tc] = await Promise.all([
      listarProductosCandidatos(1, 100, undefined, "en_catalogo"),
      obtenerOrganizacion().catch(() => null),
      obtenerTipoCambioBcb(),
    ]);
    productos = listado.productos;
    organizacion = org;
    bcb = tc;
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  return (
    <>
      <PageHeader
        titulo="Catálogo para WhatsApp"
        icono={MessageCircle}
        descripcion="Armá tu lista de precios con los productos que aprobaste y mandala por WhatsApp o subila a tu estado. Nada se envía solo: lo mandás vos."
      />
      {error && <Alerta>{error}</Alerta>}
      {!error && productos.length === 0 && (
        <EmptyState
          icono={MessageCircle}
          titulo="Todavía no aprobaste productos"
          descripcion="Cuando apruebes un producto para tu catálogo, va a aparecer acá para armar tu mensaje de WhatsApp."
          accion={{ href: "/productos", texto: "Ver productos" }}
        />
      )}
      {!error && productos.length > 0 && (
        <CatalogoWhatsApp
          negocio={organizacion?.nombre ?? ""}
          moneda={{ moneda: organizacion?.moneda ?? "USD", tipo_cambio: tipoCambioEfectivo(organizacion?.tipo_cambio, bcb) }}
          productos={productos.map((p) => ({ id: p.id, nombre: nombreLimpio(p.nombre_producto), precioUsd: p.precio_sugerido_venta }))}
        />
      )}
    </>
  );
}
