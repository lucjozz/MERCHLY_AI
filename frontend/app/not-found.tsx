import { SearchX } from "lucide-react";
import EmptyState from "@/components/ui/EmptyState";

/** 404 en español (antes salía la página por defecto de Next, en inglés). */
export default function NoEncontrada() {
  return (
    <div className="mx-auto max-w-lg py-16">
      <EmptyState
        icono={SearchX}
        titulo="Esta página no existe"
        descripcion="Puede que el link esté mal escrito, o que eso ya no exista o no sea de tu negocio."
        accion={{ href: "/", texto: "Volver al inicio" }}
      />
    </div>
  );
}
