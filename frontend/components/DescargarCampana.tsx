"use client";

import { Download } from "lucide-react";
import { etiquetaCanal } from "@/lib/etiquetas";

interface DescargarCampanaProps {
  titulo: string;
  angulos: string[];
  publico: string;
  copyPorCanal: Record<string, { titulo: string; cuerpo: string }[]>;
}

/** Descarga la campaña como texto plano (.txt) para pegarla donde quieras. */
export default function DescargarCampana({ titulo, angulos, publico, copyPorCanal }: DescargarCampanaProps) {
  function descargar() {
    const partes = [
      titulo,
      "",
      "IDEAS",
      ...angulos.map((a, i) => `${i + 1}. ${a}`),
      "",
      "PÚBLICO",
      publico,
      ...Object.entries(copyPorCanal).flatMap(([canal, textos]) => [
        "",
        `TEXTOS PARA ${etiquetaCanal(canal).toUpperCase()}`,
        ...textos.flatMap((t) => [`- ${t.titulo}`, `  ${t.cuerpo}`]),
      ]),
    ];
    const blob = new Blob([partes.join("\n")], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = `${titulo.replace(/[^\p{L}\p{N} _-]/gu, "").trim().slice(0, 60) || "campana"}.txt`;
    enlace.click();
    URL.revokeObjectURL(url);
  }

  return (
    <button
      type="button"
      onClick={descargar}
      className="inline-flex items-center gap-2 rounded-lg border border-borde px-3 py-2 text-sm text-texto-2 transition-colors hover:border-borde-fuerte hover:text-texto"
    >
      <Download className="h-4 w-4" aria-hidden="true" />
      Descargar
    </button>
  );
}
