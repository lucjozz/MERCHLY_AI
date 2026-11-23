import { Megaphone, PackageCheck } from "lucide-react";
import { listarProductosCandidatos } from "@/lib/api/productos-candidatos";
import PanelMarketing from "@/components/PanelMarketing";
import PageHeader from "@/components/ui/PageHeader";
import EmptyState from "@/components/ui/EmptyState";
import Alerta from "@/components/ui/Alerta";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

export default async function Marketing() {
  let productos: { id: string; nombre_producto: string }[] = [];
  let error: string | null = null;

  try {
    const datos = await listarProductosCandidatos(1, 100, undefined, "en_catalogo");
    productos = datos.productos.map((p) => ({
      id: p.id,
      nombre_producto: p.nombre_producto,
    }));
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  return (
    <>
      <PageHeader
        titulo="Marketing"
        icono={Megaphone}
        descripcion="Ideas y textos para promocionar los productos que ya aprobaste."
        ayuda="Elegí un producto de tu catálogo, los canales donde lo vas a mostrar y el tono. La IA te propone una campaña; no publica ni gasta nada por su cuenta."
      />

      {error && <Alerta>{error}</Alerta>}

      {!error && productos.length === 0 && (
        <EmptyState
          icono={PackageCheck}
          titulo="Todavía no tenés productos aprobados"
          descripcion="Marketing solo trabaja con productos que una persona ya aprobó. Revisá tus productos pendientes y aprobá el primero."
          accion={{ href: "/productos?estado=candidato", texto: "Revisar productos" }}
        />
      )}

      {productos.length > 0 && <PanelMarketing productos={productos} />}
    </>
  );
}
