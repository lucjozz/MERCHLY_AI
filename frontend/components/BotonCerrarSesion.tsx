"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { borrarToken } from "@/lib/auth";

export default function BotonCerrarSesion() {
  const router = useRouter();

  function cerrarSesion() {
    borrarToken();
    router.push("/login");
    router.refresh();
  }

  return (
    <button
      onClick={cerrarSesion}
      className="inline-flex items-center gap-2 bg-[#2A1414] hover:bg-[#4A2020] border border-[#4A2020] text-[#E88B8B] px-5 py-2.5 rounded-md text-sm font-semibold transition-colors"
    >
      <LogOut className="h-4 w-4" aria-hidden="true" />
      Cerrar Sesión 
    </button>
  );
}