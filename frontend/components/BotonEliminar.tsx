"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Trash2, Loader2 } from "lucide-react";
import { eliminarProductoCandidato } from "@/lib/api/productos-candidatos";

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
    } catch {
      window.alert("No se pudo eliminar el producto. ¿Está corriendo el backend?");
      setEliminando(false);
    }
  }

  return (
    <button
      onClick={eliminar}
      disabled={eliminando}
      className="p-2 text-[#7C8699] hover:text-[#E88B8B] hover:bg-[#2A1414] rounded-md transition-colors disabled:opacity-50"
      aria-label={`Eliminar ${nombreProducto}`}
    >
      {eliminando ? (
        <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
      ) : (
        <Trash2 className="h-4 w-4" aria-hidden="true" />
      )}
    </button>
  );
}