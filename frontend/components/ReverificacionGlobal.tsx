"use client";

/** Ventana única de "Confirmá que sos vos" (montada en el layout). */
import { useEffect, useState } from "react";
import ConfirmarQueSosVos from "@/components/atencion/ConfirmarQueSosVos";
import { EVENTO_REVERIFICAR, type PedidoReverificacion } from "@/lib/api/reverificacion";

export default function ReverificacionGlobal() {
  const [pedido, setPedido] = useState<PedidoReverificacion | null>(null);
  const [conDosPasos, setConDosPasos] = useState(false);

  useEffect(() => {
    function abrir(e: Event) {
      const detalle = (e as CustomEvent<PedidoReverificacion>).detail;
      // Saber si pedir el código del celular o la contraseña.
      fetch("/api/backend/auth/me", { credentials: "same-origin", cache: "no-store" })
        .then((r) => (r.ok ? r.json() : null))
        .then((u) => setConDosPasos(Boolean(u?.totp_activado)))
        .catch(() => setConDosPasos(false))
        .finally(() => setPedido(detalle));
    }
    window.addEventListener(EVENTO_REVERIFICAR, abrir);
    return () => window.removeEventListener(EVENTO_REVERIFICAR, abrir);
  }, []);

  if (!pedido) return null;
  const cerrar = (ok: boolean) => {
    pedido.resolver(ok);
    setPedido(null);
  };
  return <ConfirmarQueSosVos conDosPasos={conDosPasos} onListo={() => cerrar(true)} onCancelar={() => cerrar(false)} />;
}
