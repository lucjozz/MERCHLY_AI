"use client";

/** Lo que controla el dueño (docs/007-Agentes/09, sección 2): encendido, completar ventas, QR y zonas de envío. */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ImagePlus, Loader2, Plus, Trash2, X } from "lucide-react";
import Card, { TituloCard } from "@/components/ui/Card";
import { BOTON_PRIMARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";
import { urlQr, type AtencionConfig, type QrPago, type ZonaEnvio } from "@/lib/api/atencion-tipos";
import { borrarQr, guardarConfigAtencion, guardarZonas, prepararQr, subirQr } from "@/lib/api/atencion-acciones";

function Interruptor({ id, activo, onCambio, titulo, detalle }: { id: string; activo: boolean; onCambio: (v: boolean) => void; titulo: string; detalle: string }) {
  return (
    <label htmlFor={id} className="flex cursor-pointer items-start justify-between gap-4 rounded-xl border border-borde bg-fondo p-4">
      <span>
        <span className="block font-medium text-texto">{titulo}</span>
        <span className="mt-0.5 block text-sm text-texto-2">{detalle}</span>
      </span>
      <input id={id} type="checkbox" role="switch" checked={activo} onChange={(e) => onCambio(e.target.checked)} className="mt-1 h-5 w-5 shrink-0" />
    </label>
  );
}

export default function FormularioAtencion({ config, qrs, zonas, moneda, puedeEditar }: {
  config: AtencionConfig; qrs: QrPago[]; zonas: ZonaEnvio[]; moneda: string; puedeEditar: boolean;
}) {
  const router = useRouter();
  const simbolo = moneda === "USD" ? "US$" : "Bs";
  const [encendido, setEncendido] = useState(config.encendido);
  const [completar, setCompletar] = useState(config.completar_ventas);
  const [presentacion, setPresentacion] = useState(config.presentacion ?? "");
  const [info, setInfo] = useState(config.info_negocio ?? "");
  const [minutos, setMinutos] = useState(String(config.minutos_reserva));
  const [listaZonas, setListaZonas] = useState(zonas.map((z) => ({ nombre: z.nombre, precio: String(z.precio), notas: z.notas ?? "" })));
  const [etiquetaQr, setEtiquetaQr] = useState("");
  const [estado, setEstado] = useState<{ tipo: "ok" | "error"; texto: string } | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [subiendo, setSubiendo] = useState(false);

  async function guardar(e: React.FormEvent) {
    e.preventDefault();
    setEstado(null);
    const reserva = Number(minutos);
    if (!Number.isInteger(reserva) || reserva < 15 || reserva > 2880) return setEstado({ tipo: "error", texto: "La reserva tiene que durar entre 15 y 2880 minutos." });
    const zonasValidas = [];
    for (const z of listaZonas) {
      if (!z.nombre.trim() && !z.precio.trim()) continue;
      const precio = Number(z.precio.replace(",", "."));
      if (!z.nombre.trim() || !Number.isFinite(precio) || precio < 0) return setEstado({ tipo: "error", texto: "Cada zona necesita nombre y un precio válido." });
      zonasValidas.push({ nombre: z.nombre.trim(), precio: Math.round(precio * 100) / 100, notas: z.notas.trim() || null });
    }
    setGuardando(true);
    try {
      await guardarConfigAtencion({ encendido, completar_ventas: completar, presentacion: presentacion.trim() || null, info_negocio: info.trim() || null, minutos_reserva: reserva });
      await guardarZonas(zonasValidas);
      setEstado({ tipo: "ok", texto: "Guardado." });
      router.refresh();
    } catch (err) {
      setEstado({ tipo: "error", texto: err instanceof Error ? err.message : "No se pudo guardar." });
    } finally {
      setGuardando(false);
    }
  }

  async function agregarQr(archivos: FileList | null) {
    const archivo = archivos?.[0];
    if (!archivo) return;
    setEstado(null);
    setSubiendo(true);
    try {
      await subirQr(etiquetaQr.trim() || "QR de pago", await prepararQr(archivo));
      setEtiquetaQr("");
      router.refresh();
    } catch (err) {
      setEstado({ tipo: "error", texto: err instanceof Error ? err.message : "No se pudo subir el QR." });
    } finally {
      setSubiendo(false);
    }
  }

  async function quitarQr(id: string) {
    if (!window.confirm("¿Quitar este QR? El asistente deja de mandarlo.")) return;
    try {
      await borrarQr(id);
      router.refresh();
    } catch (err) {
      setEstado({ tipo: "error", texto: err instanceof Error ? err.message : "No se pudo quitar el QR." });
    }
  }

  return (
    <form onSubmit={guardar} className="space-y-6">
      <fieldset disabled={!puedeEditar} className="space-y-6">
        <Card>
          <TituloCard descripcion="Vos decidís hasta dónde llega el asistente.">Cómo trabaja el asistente</TituloCard>
          <div className="space-y-3">
            <Interruptor id="a-encendido" activo={encendido} onCambio={setEncendido} titulo="Asistente encendido"
              detalle="Responde los mensajes de tus canales conectados (WhatsApp llega en la próxima fase). Apagado: los mensajes te llegan a vos sin respuesta automática. El simulador funciona siempre." />
            <Interruptor id="a-completar" activo={completar} onCambio={setCompletar} titulo="Completar ventas"
              detalle="SÍ: confirma el pedido, reserva el stock y manda tu QR. NO: arma el pedido y te lo pasa para que lo cierres vos. En los dos casos, el pago lo confirmás siempre vos." />
            {completar && qrs.length === 0 && <p className="text-sm text-ambar">Cargá un QR abajo: sin QR, el asistente te pasa el pedido para que lo cierres vos.</p>}
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label htmlFor="a-pres" className={ETIQUETA_CAMPO}>Cómo se presenta</label>
              <input id="a-pres" value={presentacion} onChange={(e) => setPresentacion(e.target.value)} maxLength={300} placeholder="¡Hola! Soy el asistente virtual de Mi Tienda." className={CAMPO} />
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="a-info" className={ETIQUETA_CAMPO}>Datos del negocio que puede contar</label>
              <textarea id="a-info" rows={3} value={info} onChange={(e) => setInfo(e.target.value)} maxLength={2000} placeholder="Horario: lunes a sábado de 9 a 19. Estamos en Av. ... Aceptamos QR y efectivo. Cambios dentro de 7 días con boleta." className={CAMPO} />
            </div>
            <div>
              <label htmlFor="a-min" className={ETIQUETA_CAMPO}>Cuánto dura la reserva (minutos)</label>
              <input id="a-min" inputMode="numeric" value={minutos} onChange={(e) => setMinutos(e.target.value)} className={CAMPO} />
            </div>
          </div>
        </Card>

        <Card>
          <TituloCard descripcion={`Costo estimado que el asistente le dice al cliente, en ${simbolo}. Más adelante se suma la cotización con Yango.`}>Zonas de envío</TituloCard>
          <ul className="space-y-2">
            {listaZonas.map((z, i) => (
              <li key={i} className="flex gap-2">
                <input aria-label="Zona" placeholder="Equipetrol" maxLength={80} value={z.nombre} onChange={(e) => setListaZonas(listaZonas.map((x, j) => (j === i ? { ...x, nombre: e.target.value } : x)))} className={CAMPO} />
                <input aria-label="Precio" placeholder="15" inputMode="decimal" value={z.precio} onChange={(e) => setListaZonas(listaZonas.map((x, j) => (j === i ? { ...x, precio: e.target.value } : x)))} className={`${CAMPO} !w-28`} />
                <button type="button" onClick={() => setListaZonas(listaZonas.filter((_, j) => j !== i))} className="px-2 text-texto-2 hover:text-rojo" aria-label="Quitar zona">
                  <X className="h-4 w-4" aria-hidden="true" />
                </button>
              </li>
            ))}
          </ul>
          {listaZonas.length < 30 && (
            <button type="button" onClick={() => setListaZonas([...listaZonas, { nombre: "", precio: "", notas: "" }])} className="mt-2 inline-flex items-center gap-1 text-sm text-acento-claro hover:text-texto">
              <Plus className="h-4 w-4" aria-hidden="true" /> Agregar zona
            </button>
          )}
        </Card>

        {puedeEditar && (
          <div className="flex items-center gap-3">
            <button type="submit" disabled={guardando} className={BOTON_PRIMARIO}>
              {guardando && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />} Guardar
            </button>
            {estado && <p role={estado.tipo === "error" ? "alert" : "status"} className={`text-sm ${estado.tipo === "error" ? "text-rojo" : "text-verde"}`}>{estado.texto}</p>}
          </div>
        )}
      </fieldset>

      <Card>
        <TituloCard descripcion="El asistente lo manda cuando el cliente confirma la compra (solo si «Completar ventas» está activado).">QR de pago</TituloCard>
        <div className="flex flex-wrap gap-3">
          {qrs.map((q) => (
            <div key={q.id} className="relative rounded-xl border border-borde bg-fondo p-2 text-center">
              {/* eslint-disable-next-line @next/next/no-img-element -- imagen privada servida por el BFF con sesión */}
              <img src={urlQr(q.id)} alt={`QR ${q.etiqueta}`} className="h-32 w-32 rounded-lg bg-white object-contain p-1" />
              <p className="mt-1 text-xs text-texto-2">{q.etiqueta}</p>
              {puedeEditar && (
                <button type="button" onClick={() => quitarQr(q.id)} className="absolute right-1 top-1 rounded-md bg-black/70 p-1 text-white" aria-label={`Quitar QR ${q.etiqueta}`}>
                  <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                </button>
              )}
            </div>
          ))}
          {puedeEditar && qrs.length < 5 && (
            <div className="flex flex-col gap-2">
              <label htmlFor="qr-etiqueta" className="sr-only">Banco o cuenta del QR</label>
              <input id="qr-etiqueta" value={etiquetaQr} onChange={(e) => setEtiquetaQr(e.target.value)} maxLength={80} placeholder="Banco (ej. BNB)" className={`${CAMPO} !w-40`} />
              <label className="flex h-24 w-40 cursor-pointer flex-col items-center justify-center gap-1 rounded-xl border border-dashed border-borde-fuerte text-xs text-texto-2 hover:border-acento-borde hover:text-texto">
                {subiendo ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" /> : <ImagePlus className="h-5 w-5" aria-hidden="true" />}
                {subiendo ? "Subiendo…" : "Subir foto del QR"}
                <input type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" disabled={subiendo} onChange={(e) => agregarQr(e.target.files)} />
              </label>
            </div>
          )}
        </div>
        {!puedeEditar && <p className="mt-3 text-sm text-texto-2">Solo el administrador o el responsable de negocio cambian esta configuración.</p>}
      </Card>
    </form>
  );
}
