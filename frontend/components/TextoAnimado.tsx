"use client";

import { useState, useEffect } from "react";

interface TextoAnimadoProps {
  texto: string;
  velocidad?: number;
}

/** Efecto "máquina de escribir". El texto se renderiza siempre como texto plano. */
export default function TextoAnimado({ texto, velocidad = 15 }: TextoAnimadoProps) {
  const [avance, setAvance] = useState({ texto, caracteres: 0 });
  // Si cambia el texto, el avance anterior deja de valer y arranca de cero.
  const caracteres = avance.texto === texto ? avance.caracteres : 0;

  useEffect(() => {
    let indice = 0;
    const intervalo = setInterval(() => {
      indice++;
      setAvance({ texto, caracteres: indice });
      if (indice >= texto.length) clearInterval(intervalo);
    }, velocidad);

    return () => clearInterval(intervalo);
  }, [texto, velocidad]);

  return <span>{texto.slice(0, caracteres)}</span>;
}
