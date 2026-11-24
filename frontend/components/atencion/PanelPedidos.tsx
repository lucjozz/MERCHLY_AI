"use client";

/** Pedidos del asistente y avisos al vendedor. Solo una persona confirma un pago (docs/007-Agentes/09, sección 3.5). */
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bell, CheckCheck, Loader2, PackageCheck, ShoppingBag } from "lucide-react";
import Badge from "@/components/ui/Badge";
import EmptyState from "@/components/ui/EmptyState";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO } from "@/components/ui/estilos";
import { ESTADO_PEDIDO, type Notificacion, type Pedido } from "@/lib/api/atencion-tipos";
import { decidirPedido, marcarAvisosLeidos } from "@/lib/api/atencion-acciones";
import { formatearPrecioLocal } from "@/lib/moneda";

type Accion = "confirmar-pago" | "rechazar-pago" | "entregado" | "cancelar";
const ACCIONES: Record<string, { accion: Accion; texto: string; primario?: boolean; confirmar?: string }[]> = {
  pedido_armado: [
    { accion: "confirmar-pago", texto: "Ya cobré", primario: true, confirmar: "¿Confirmás que ya viste la plata en tu cuenta? Se descuenta el stock." },
    { accion: "cancelar", texto: "Cancelar" },
  ],
  reservado: [
    { accion: "confirmar-pago", texto: "Confirmar pago", primario: true, confirmar: "¿Viste la plata en tu cuenta? Se descuenta el stock y se le avisa al comprador." },
    { accion: "cancelar", texto: "Cancelar" },
  ],
  pago_por_confirmar: [
    { accion: "confirmar-pago", texto: "Confirmar pago", primario: true, confirmar: "¿Viste la plata en tu cuenta? Se descuenta el stock y se le avisa al comprador." },
    { accion: "rechazar-pago", texto: "No me llegó", confirmar: "Se libera el stock reservado y se le avisa al comprador." },
  ],
  pagado: [{ accion: "entregado", texto: "Marcar entregado", primario: true }],
};

export default function PanelPedidos({ pedidos, avisos, sinLeer, moneda, puedeDecidir }: {
  pedidos: Pedido[]; avisos: Notificacion[]; sinLeer: number; moneda: string; puedeDecidir: boolean;
}) {
  const router = useRouter();
  const [ocupado, setOcupado] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const precio = (v: string) => formatearPrecioLocal(v, moneda);

  async function decidir(pedido: Pedido, a: (typeof ACCIONES)[string][number]) {
    if (a.confirmar && !window.confirm(a.confirmar)) return;
    setError(null);
    setOcupado(pedido.id + a.accion);
    try {
      await decidirPedido(pedido.id, a.accion);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo actualizar el pedido.");
    } finally {
      setOcupado(null);
    }
  }

  async function leerTodo() {
    await marcarAvisosLeidos().catch(() => undefined);
    router.refresh();
  }

  const abiertos = pedidos.filter((p) => ["pedido_armado", "reservado", "pago_por_confirmar", "pagado"].includes(p.estado));
  const cerrados = pedidos.filter((p) => !abiertos.includes(p));

  return (
    <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
      <section aria-labelledby="t-pedidos">
        <h2 id="t-pedidos" className="mb-3 flex items-center gap-2 text-base font-semibold text-texto">
          <ShoppingBag className="h-4 w-4 text-acento-claro" aria-hidden="true" /> Pedidos abiertos
        </h2>
        {error && <p role="alert" className="mb-3 rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">{error}</p>}
        {abiertos.length === 0 ? (
          <EmptyState compacto icono={PackageCheck} titulo="No hay pedidos abiertos" descripcion="Cuando el asistente arme un pedido, aparece acá para que lo cierres." accion={{ href: "/atencion/simulador", texto: "Probar el asistente" }} />
        ) : (
          <ul className="space-y-3">
            {abiertos.map((p) => (
              <li key={p.id} className="rounded-2xl border border-borde bg-superficie p-4">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-texto">{p.nombre_comprador ?? "Comprador"} · {precio(p.total)}</p>
                    <p className="text-xs text-texto-3">{new Date(p.creado_en).toLocaleString("es-BO", { dateStyle: "short", timeStyle: "short" })}</p>
                  </div>
                  <div className="flex gap-1.5">
                    {p.simulado && <Badge tono="gris">Simulado</Badge>}
                    <Badge tono={ESTADO_PEDIDO[p.estado]?.tono ?? "gris"} punto>{ESTADO_PEDIDO[p.estado]?.texto ?? p.estado}</Badge>
                  </div>
                </div>
                <ul className="mt-3 space-y-1 text-sm text-texto-2">
                  {p.items.map((i) => <li key={i.producto_id}>{i.cantidad} × {i.nombre} — {precio(i.precio_unitario)} c/u</li>)}
                  <li>Envío: {p.zona_envio ? `${p.zona_envio} · ${precio(p.costo_envio)}` : "a coordinar"}</li>
                  {p.reservado_hasta && p.estado === "reservado" && (
                    <li className="text-ambar">Reservado hasta las {new Date(p.reservado_hasta).toLocaleTimeString("es-BO", { hour: "2-digit", minute: "2-digit" })}</li>
                  )}
                </ul>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  {puedeDecidir && (ACCIONES[p.estado] ?? []).map((a) => (
                    <button key={a.accion} type="button" onClick={() => decidir(p, a)} disabled={ocupado !== null} className={a.primario ? BOTON_PRIMARIO : BOTON_SECUNDARIO}>
                      {ocupado === p.id + a.accion && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
                      {a.texto}
                    </button>
                  ))}
                  {p.conversacion_id && <Link href={`/atencion/conversaciones/${p.conversacion_id}`} className="text-sm text-acento-claro hover:text-texto">Ver conversación</Link>}
                </div>
              </li>
            ))}
          </ul>
        )}
        {cerrados.length > 0 && (
          <details className="mt-4 rounded-2xl border border-borde bg-superficie p-4 text-sm">
            <summary className="cursor-pointer text-texto-2">Pedidos cerrados ({cerrados.length})</summary>
            <ul className="mt-3 space-y-2">
              {cerrados.map((p) => (
                <li key={p.id} className="flex flex-wrap justify-between gap-2 text-texto-2">
                  <span>{p.nombre_comprador ?? "Comprador"} · {precio(p.total)}{p.simulado ? " · simulado" : ""}</span>
                  <Badge tono={ESTADO_PEDIDO[p.estado]?.tono ?? "gris"}>{ESTADO_PEDIDO[p.estado]?.texto ?? p.estado}</Badge>
                </li>
              ))}
            </ul>
          </details>
        )}
      </section>

      <section aria-labelledby="t-avisos">
        <div className="mb-3 flex items-center justify-between">
          <h2 id="t-avisos" className="flex items-center gap-2 text-base font-semibold text-texto">
            <Bell className="h-4 w-4 text-ambar" aria-hidden="true" /> Avisos {sinLeer > 0 && <Badge tono="ambar">{sinLeer} nuevos</Badge>}
          </h2>
          {sinLeer > 0 && (
            <button type="button" onClick={leerTodo} className="inline-flex items-center gap-1 text-xs text-acento-claro hover:text-texto">
              <CheckCheck className="h-3.5 w-3.5" aria-hidden="true" /> Marcar leídos
            </button>
          )}
        </div>
        {avisos.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-borde-fuerte p-6 text-center text-sm text-texto-2">Sin avisos por ahora.</p>
        ) : (
          <ul className="space-y-2">
            {avisos.map((n) => (
              <li key={n.id} className={`rounded-xl border p-3 text-sm ${n.leida_en ? "border-borde bg-superficie" : "border-ambar-borde bg-ambar-fondo/40"}`}>
                <p className="font-medium text-texto">{n.titulo}</p>
                {n.cuerpo && <p className="mt-0.5 text-texto-2">{n.cuerpo}</p>}
                <p className="mt-1 flex gap-3 text-xs text-texto-3">
                  {new Date(n.creado_en).toLocaleString("es-BO", { dateStyle: "short", timeStyle: "short" })}
                  {n.conversacion_id && <Link href={`/atencion/conversaciones/${n.conversacion_id}`} className="text-acento-claro">Ver conversación</Link>}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
