"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, Loader2 } from "lucide-react";
import { investigarProductos } from "@/lib/api/investigador";

export default function BuscarProductos() {
  const router = useRouter();
  const [categoria, setCategoria] = useState("");
  const [mercado, setMercado] = useState("MX");
  const [buscando, setBuscando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function buscar(e: React.FormEvent) {
    e.preventDefault();

    if (categoria.trim().length === 0) {
      setError("Escribí una categoría para buscar.");
      return;
    }

    setError(null);
    setBuscando(true);

    try {
      await investigarProductos(categoria, mercado);
      setCategoria("");
      router.refresh();
    } catch {
      setError("No se pudo completar la búsqueda. ¿Está corriendo el backend?");
    } finally {
      setBuscando(false);
    }
  }

  return (
    <form
      onSubmit={buscar}
      className="flex flex-wrap gap-3 mb-6 bg-[#12151C] border border-[#1E3A5F] p-4 rounded-lg"
    >
      <div className="flex-1 min-w-[200px]">
        <input
          type="text"
          value={categoria}
          onChange={(e) => setCategoria(e.target.value)}
          placeholder="Ej: mochilas antirrobo, lámparas de escritorio..."
          disabled={buscando}
          className="w-full bg-[#0B0D12] border border-[#242938] text-[#F5F7FA] placeholder-[#5B6272] rounded-md px-3 py-2 text-sm outline-none focus:border-[#3D7DD8] focus:ring-1 focus:ring-[#3D7DD8] transition-colors disabled:opacity-50"
        />
      </div>
      <select
        value={mercado}
        onChange={(e) => setMercado(e.target.value)}
        disabled={buscando}
        className="bg-[#0B0D12] border border-[#242938] text-[#F5F7FA] rounded-md px-3 py-2 text-sm outline-none focus:border-[#3D7DD8] focus:ring-1 focus:ring-[#3D7DD8] transition-colors disabled:opacity-50"
      >
        <option value="MX">México</option>
        <option value="US">Estados Unidos</option>
        <option value="BO">Bolivia</option>
        <option value="AR">Argentina</option>
      </select>
      <button
        type="submit"
        disabled={buscando}
        className="inline-flex items-center gap-2 bg-[#1E3A5F] hover:bg-[#28507F] border border-[#2B4A73] text-white px-5 py-2 rounded-md text-sm font-semibold transition-all hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100"
      >
        {buscando ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            Buscando...
          </>
        ) : (
          <>
            <Search className="h-4 w-4" aria-hidden="true" />
            Buscar Productos
          </>
        )}
      </button>
      {error && <p className="w-full text-[#E88B8B] text-sm">{error}</p>}
    </form>
  );
}