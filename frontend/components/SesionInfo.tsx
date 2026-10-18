"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { borrarToken, obtenerTokenCliente } from "@/lib/auth";

interface Sesion {
  emitido: number;
  vence: number;
}

function leerSesion(): Sesion | null {
  const token = obtenerTokenCliente();
  if (!token) return null;
  try {
    const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const relleno = base64 + "=".repeat((4 - (base64.length % 4)) % 4);
    const datos = JSON.parse(atob(relleno));
    return { emitido: datos.iat * 1000, vence: datos.exp * 1000 };
  } catch {
    return null;
  }
}

function fecha(ms: number): string {
  return new Date(ms).toLocaleString("es-BO", {
    timeZone: "America/La_Paz",
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function reloj(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000));
  const h = String(Math.floor(total / 3600)).padStart(2, "0");
  const m = String(Math.floor((total % 3600) / 60)).padStart(2, "0");
  const s = String(total % 60).padStart(2, "0");
  return `${h}:${m}:${s}`;
}

export default function SesionInfo() {
  const router = useRouter();
  const [sesion, setSesion] = useState<Sesion | null>(null);
  const [ahora, setAhora] = useState(0);

  useEffect(() => {
    setSesion(leerSesion());
    setAhora(Date.now());
    const intervalo = setInterval(() => setAhora(Date.now()), 1000);
    return () => clearInterval(intervalo);
  }, []);

  const restante = sesion ? sesion.vence - ahora : 0;

  useEffect(() => {
    if (sesion && ahora > 0 && restante <= 0) {
      borrarToken();
      router.push("/login");
    }
  }, [sesion, ahora, restante, router]);

  if (!sesion || ahora === 0) {
    return <p className="text-sm text-[#5B6272]">Leyendo sesión...</p>;
  }

  const total = sesion.vence - sesion.emitido;
  const horas = Math.round(total / 3600000);
  const avance = Math.min(100, Math.max(0, ((ahora - sesion.emitido) / total) * 100));
  const porVencer = restante < 15 * 60 * 1000;

  return (
    <div className="space-y-4 text-sm">
      <div className="flex justify-between">
        <span className="text-[#7C8699]">Iniciada</span>
        <span className="text-[#F5F7FA]">{fecha(sesion.emitido)}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-[#7C8699]">Vence</span>
        <span className="text-[#F5F7FA]">{fecha(sesion.vence)}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-[#7C8699]">Duración total</span>
        <span className="text-[#F5F7FA]">{horas} h</span>
      </div>
      <div className="flex justify-between items-center">
        <span className="text-[#7C8699]">Tiempo restante</span>
        <span
          className={`font-mono text-base ${
            porVencer ? "text-[#E8B84B]" : "text-[#4ADE80]"
          }`}
        >
          {reloj(restante)}
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-[#0B0D12]">
        <div
          className={`h-1.5 rounded-full transition-all duration-1000 ${
            porVencer ? "bg-[#E8B84B]" : "bg-[#3D7DD8]"
          }`}
          style={{ width: `${avance}%` }}
        />
      </div>
    </div>
  );
}