"use client";

import { useState, useEffect } from "react";

interface TextoAnimadoProps {
  texto: string;
  velocidad?: number;
}

export default function TextoAnimado({ texto, velocidad = 15 }: TextoAnimadoProps) {
  const [mostrado, setMostrado] = useState("");

  useEffect(() => {
    setMostrado("");
    let indice = 0;
    const intervalo = setInterval(() => {
      indice++;
      setMostrado(texto.slice(0, indice));
      if (indice >= texto.length) clearInterval(intervalo);
    }, velocidad);

    return () => clearInterval(intervalo);
  }, [texto, velocidad]);

  return <span>{mostrado}</span>;
}