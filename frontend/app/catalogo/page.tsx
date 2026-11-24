import { MessageCircle } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Alerta from "@/components/ui/Alerta";
import EmptyState from "@/components/ui/EmptyState";
import CatalogoWhatsApp from "@/components/CatalogoWhatsApp";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import { listarCatalogoPublico } from "@/lib/api/inventario";
import { obtenerOrganizacion, type Organizacion } from "@/lib/api/organizacion";
import { obtenerTipoCambioBcb, tipoCambioEfectivo } from "@/lib/api/tipo-cambio";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";
import { usaBolivianos } from "@/lib/moneda";
import { nombreLimpio } from "@/lib/etiquetas";

export const dynamic = "force-dynamic";

interface Item {
  id: string;
  nombre: string;
  precio: number | null;
}

/**
 * Catálogo listo para WhatsApp (docs/004-Backend/05, sección 2).
 * Sale del CATÁLOGO PÚBLICO del inventario (precio y stock reales, solo lo publicado
 * y con unidades disponibles). Si todavía no hay inventario, usa los productos que
 * aprobaste de las sugerencias de la IA, con el precio sugerido.
 */
export default async function Catalogo() {
  let productos: Item[] = [];
  let organizacion: Organizacion | null = null;
  let simbolo = "Bs";
  let origen: "inventario" | "sugerencias" = "inventario";
  let error: string | null = null;
  try {
    const [publico, org] = await Promise.all([listarCatalogoPublico(), obtenerOrganizacion().catch(() => null)]);
    organizacion = org;
    simbolo = org?.moneda === "USD" ? "US$" : "Bs";
    productos = publico
      .filter((p) => p.disponibles > 0)
      .map((p) => ({ id: p.id, nombre: p.nombre, precio: p.precio_venta === null ? null : Number(p.precio_venta) }));
    if (publico.length === 0) {
      origen = "sugerencias";
      const [listado, bcb] = await Promise.all([listarProductosCandidatos(1, 100, undefined, "en_catalogo"), obtenerTipoCambioBcb()]);
      const moneda = { moneda: org?.moneda ?? "USD", tipo_cambio: tipoCambioEfectivo(org?.tipo_cambio, bcb) };
      const factor = usaBolivianos(moneda) ? (moneda.tipo_cambio as number) : 1;
      simbolo = usaBolivianos(moneda) ? "Bs" : "US$";
      productos = listado.productos.map((p) => ({
        id: p.id,
        nombre: nombreLimpio(p.nombre_producto),
        precio: p.precio_sugerido_venta === null ? null : Math.round(p.precio_sugerido_venta * factor),
      }));
    }
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  return (
    <>
      <PageHeader
        titulo="Catálogo para WhatsApp"
        icono={MessageCircle}
        descripcion="Armá tu lista de precios y mandala por WhatsApp o subila a tu estado. Nada se envía solo: lo mandás vos."
      />
      {error && <Alerta>{error}</Alerta>}
      {!error && origen === "sugerencias" && productos.length > 0 && (
        <Alerta tipo="info" className="mb-6">
          Todavía no publicaste productos en tu inventario: te mostramos los que aprobaste de las sugerencias de la IA, con el precio sugerido.
          Cargá tu inventario para usar tus precios y tu stock reales.
        </Alerta>
      )}
      {!error && productos.length === 0 && (
        <EmptyState
          icono={MessageCircle}
          titulo="No hay productos para el catálogo"
          descripcion="Publicá productos con stock en tu inventario (o aprobá sugerencias de la IA) y van a aparecer acá."
          accion={{ href: "/inventario", texto: "Ir al inventario" }}
        />
      )}
      {!error && productos.length > 0 && <CatalogoWhatsApp negocio={organizacion?.nombre ?? ""} simbolo={simbolo} productos={productos} />}
    </>
  );
}
