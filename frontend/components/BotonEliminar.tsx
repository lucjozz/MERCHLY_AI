"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Trash2, Loader2 } from "lucide-react";
import { eliminarProductoCandidato } from "@/lib/api/productos-acciones";

interface BotonEliminarProps {
  productoId: string;
  nombreProducto: string;
}

export default function BotonEliminar({
  productoId,
  nombreProducto,
}: BotonEliminarProps) {
  const router = useRouter();
  const [eliminando, setEliminando] = useState(false);

  async function eliminar(e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();

    const confirmado = window.confirm(
      `¿Eliminar "${nombreProducto}"? Esta acción no se puede deshacer.`
    );
    if (!confirmado) return;

    setEliminando(true);
    try {
      await eliminarProductoCandidato(productoId);
      router.refresh();
    } catch (e) {
      window.alert(e instanceof Error ? e.message : "No se pudo eliminar el producto. Probá de nuevo en unos segundos.");
      setEliminando(false);
    }
  }

  return (
    <button
      type="button"
      onClick={eliminar}
      disabled={eliminando}
      className="rounded-lg p-2 text-texto-2 transition-colors hover:bg-rojo-fondo hover:text-rojo disabled:opacity-50"
      aria-label={`Eliminar ${nombreProducto}`}
      title="Eliminar producto"
    >
      {eliminando ? (
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
      ) : (
        <Trash2 className="h-4 w-4" aria-hidden="true" />
      )}
    </button>
  );
}
