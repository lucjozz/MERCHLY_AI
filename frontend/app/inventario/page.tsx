import Link from "next/link";
import { Boxes, Eye, Lock } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Alerta from "@/components/ui/Alerta";
import PanelInventario from "@/components/PanelInventario";
import CatalogoPublicoVista from "@/components/CatalogoPublicoVista";
import { listarCatalogoPublico, listarInventario, type InventarioListado, type ItemCatalogoPublico } from "@/lib/api/inventario";
import { obtenerOrganizacion } from "@/lib/api/organizacion";
import { obtenerUsuarioActual } from "@/lib/api/usuario";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

const EDITORES = ["admin_principal", "responsable_negocio"];

interface PageProps {
  searchParams: Promise<{ vista?: string; buscar?: string }>;
}

/** Dos catálogos sobre los mismos productos (docs/007-Agentes/08, sección 2). */
export default async function Inventario({ searchParams }: PageProps) {
  const { vista, buscar } = await searchParams;
  const publico = vista === "publico";
  let listado: InventarioListado | null = null;
  let catalogo: ItemCatalogoPublico[] = [];
  let moneda = "BOB";
  let puedeEditar = false;
  let error: string | null = null;
  try {
    const [usuario, organizacion] = await Promise.all([obtenerUsuarioActual(), obtenerOrganizacion().catch(() => null)]);
    puedeEditar = EDITORES.includes(usuario.rol);
    moneda = organizacion?.moneda ?? "BOB";
    if (publico) catalogo = await listarCatalogoPublico();
    else listado = await listarInventario(buscar);
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  const pestana = (activa: boolean) =>
    `inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
      activa ? "bg-superficie-2 text-texto" : "text-texto-2 hover:text-texto"
    }`;

  return (
    <>
      <PageHeader
        titulo="Inventario"
        icono={Boxes}
        descripcion="Tus productos reales: lo que te costaron, cuántos tenés y a cuánto los vendés. Lo que publicás pasa al catálogo público, que es lo que usa la IA para responder a tus clientes."
      />
      <nav aria-label="Vistas del inventario" className="mb-6 inline-flex gap-1 rounded-xl border border-borde bg-superficie p-1">
        <Link href="/inventario" className={pestana(!publico)} aria-current={!publico ? "page" : undefined}>
          <Lock className="h-4 w-4" aria-hidden="true" />
          Mi inventario (privado)
        </Link>
        <Link href="/inventario?vista=publico" className={pestana(publico)} aria-current={publico ? "page" : undefined}>
          <Eye className="h-4 w-4" aria-hidden="true" />
          Catálogo público (lo que ve la IA)
        </Link>
      </nav>

      {error && <Alerta>{error}</Alerta>}
      {!error && listado && (
        <PanelInventario listado={listado} moneda={moneda} puedeEditar={puedeEditar} buscar={buscar ?? ""} />
      )}
      {!error && publico && <CatalogoPublicoVista productos={catalogo} moneda={moneda} />}
    </>
  );
}
