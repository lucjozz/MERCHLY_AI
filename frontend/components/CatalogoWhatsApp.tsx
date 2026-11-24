"use client";

/**
 * Arma el mensaje del catálogo con formato de WhatsApp (docs/004-Backend/05, sección 2).
 * La selección y los precios se recuerdan solo en este navegador (comodidad, no dato del negocio).
 */
import { useEffect, useMemo, useState } from "react";
import { Check, Copy, MessageCircle } from "lucide-react";
import Card from "@/components/ui/Card";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";
import { armarMensajeCatalogo, enlaceWhatsApp } from "@/lib/whatsapp";

interface Producto {
  id: string;
  nombre: string;
  /** Ya en la moneda del negocio. */
  precio: number | null;
}

interface Props {
  negocio: string;
  simbolo: string;
  productos: Producto[];
}

const CLAVE = "merchly:catalogo-whatsapp";

interface Guardado {
  encabezado?: string;
  nota?: string;
  incluidos?: Record<string, boolean>;
  precios?: Record<string, string>;
}

function leer(): Guardado {
  try {
    return JSON.parse(localStorage.getItem(CLAVE) ?? "{}") as Guardado;
  } catch {
    return {};
  }
}

export default function CatalogoWhatsApp({ negocio, simbolo, productos }: Props) {
  const precioInicial = (p: Producto) => (p.precio === null ? "" : String(Number.isInteger(p.precio) ? p.precio : p.precio.toFixed(2)));

  const [encabezado, setEncabezado] = useState(negocio ? `Catálogo de ${negocio}` : "Nuestro catálogo");
  const [nota, setNota] = useState("Hacemos envíos. Pagás por QR o en efectivo. ¡Escribinos para hacer tu pedido!");
  const [incluidos, setIncluidos] = useState<Record<string, boolean>>(() => Object.fromEntries(productos.map((p) => [p.id, true])));
  const [precios, setPrecios] = useState<Record<string, string>>(() => Object.fromEntries(productos.map((p) => [p.id, precioInicial(p)])));
  const [copiado, setCopiado] = useState(false);
  const [cargado, setCargado] = useState(false);

  // Recupera lo que la persona dejó armado la última vez (solo de productos que siguen en el catálogo).
  useEffect(() => {
    const g = leer();
    /* eslint-disable react-hooks/set-state-in-effect -- lectura única de localStorage al montar */
    if (g.encabezado) setEncabezado(g.encabezado);
    if (g.nota !== undefined) setNota(g.nota);
    if (g.incluidos) setIncluidos((a) => Object.fromEntries(Object.keys(a).map((id) => [id, g.incluidos![id] ?? a[id]])));
    if (g.precios) setPrecios((a) => Object.fromEntries(Object.keys(a).map((id) => [id, g.precios![id] ?? a[id]])));
    setCargado(true);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  useEffect(() => {
    if (!cargado) return;
    try {
      localStorage.setItem(CLAVE, JSON.stringify({ encabezado, nota, incluidos, precios }));
    } catch {
      /* sin almacenamiento disponible: no pasa nada */
    }
  }, [cargado, encabezado, nota, incluidos, precios]);

  const elegidos = productos.filter((p) => incluidos[p.id]);
  const mensaje = useMemo(
    () =>
      armarMensajeCatalogo({
        encabezado,
        nota,
        simbolo,
        items: productos.filter((p) => incluidos[p.id]).map((p) => ({ nombre: p.nombre, precio: precios[p.id] ?? "" })),
      }),
    [encabezado, nota, simbolo, productos, incluidos, precios]
  );
  const cantidad = elegidos.length;

  async function copiar() {
    try {
      await navigator.clipboard.writeText(mensaje);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      setCopiado(false);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
      <Card>
        <div className="space-y-4">
          <div>
            <label htmlFor="c-encabezado" className={ETIQUETA_CAMPO}>Título del mensaje</label>
            <input id="c-encabezado" value={encabezado} maxLength={80} onChange={(e) => setEncabezado(e.target.value)} className={CAMPO} />
          </div>
          <fieldset>
            <legend className={ETIQUETA_CAMPO}>Productos y precio de venta ({simbolo})</legend>
            <ul className="space-y-2">
              {productos.map((p) => (
                <li key={p.id} className="flex items-center gap-3 rounded-xl border border-borde bg-fondo px-3 py-2">
                  <input
                    id={`c-${p.id}`}
                    type="checkbox"
                    checked={Boolean(incluidos[p.id])}
                    onChange={(e) => setIncluidos({ ...incluidos, [p.id]: e.target.checked })}
                    className="h-4 w-4 shrink-0"
                  />
                  <label htmlFor={`c-${p.id}`} className="min-w-0 flex-1 truncate text-sm text-texto">{p.nombre}</label>
                  <input
                    aria-label={`Precio de ${p.nombre}`}
                    inputMode="decimal"
                    value={precios[p.id] ?? ""}
                    onChange={(e) => setPrecios({ ...precios, [p.id]: e.target.value })}
                    className={`${CAMPO} !w-24 text-right`}
                  />
                </li>
              ))}
            </ul>
          </fieldset>
          <div>
            <label htmlFor="c-nota" className={ETIQUETA_CAMPO}>Nota al final (envíos, pagos, contacto)</label>
            <textarea id="c-nota" rows={3} value={nota} maxLength={400} onChange={(e) => setNota(e.target.value)} className={CAMPO} />
          </div>
        </div>
      </Card>

      <div className="space-y-4">
        <Card>
          <p className="mb-3 text-sm font-semibold text-texto">Vista previa</p>
          <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap rounded-xl bg-fondo p-4 font-sans text-sm leading-relaxed text-texto">{mensaje}</pre>
          <p className="mt-2 text-xs text-texto-3">
            {cantidad === 1 ? "1 producto" : `${cantidad} productos`} · En WhatsApp, el texto entre asteriscos se ve en negrita.
          </p>
        </Card>
        <div className="flex flex-wrap gap-3">
          <button type="button" onClick={copiar} disabled={cantidad === 0} className={BOTON_SECUNDARIO}>
            {copiado ? <Check className="h-4 w-4 text-verde" aria-hidden="true" /> : <Copy className="h-4 w-4" aria-hidden="true" />}
            {copiado ? "Copiado" : "Copiar"}
          </button>
          {cantidad > 0 ? (
            <a href={enlaceWhatsApp(mensaje)} target="_blank" rel="noopener noreferrer" className={BOTON_PRIMARIO}>
              <MessageCircle className="h-4 w-4" aria-hidden="true" />
              Abrir en WhatsApp
            </a>
          ) : (
            <span className={`${BOTON_PRIMARIO} pointer-events-none opacity-50`}>
              <MessageCircle className="h-4 w-4" aria-hidden="true" />
              Abrir en WhatsApp
            </span>
          )}
        </div>
        <p className="text-xs text-texto-3">WhatsApp se abre para que elijas a quién mandarlo. Nosotros no enviamos nada.</p>
      </div>
    </div>
  );
}
