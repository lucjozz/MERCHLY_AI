import { ExternalLink, ShoppingCart } from "lucide-react";

/**
 * "¿Dónde lo compro?": enlaces de BÚSQUEDA en mercados mayoristas con el
 * nombre del producto (docs/004-Backend/03, sección 4). No recomiendan a un
 * vendedor concreto: la persona compara y elige.
 */
const MERCADOS = [
  { nombre: "AliExpress", url: (q: string) => `https://www.aliexpress.com/wholesale?SearchText=${q}` },
  { nombre: "Alibaba", url: (q: string) => `https://www.alibaba.com/trade/search?SearchText=${q}` },
  { nombre: "Mercado Libre", url: (q: string) => `https://listado.mercadolibre.com.ar/${q}` },
];

export default function EnlacesProveedor({ producto }: { producto: string }) {
  const consulta = encodeURIComponent(
    producto.replace(/\(simulado\)/gi, "").replace(/—.*$/, "").trim().slice(0, 80)
  );
  return (
    <div className="rounded-2xl border border-borde bg-superficie p-5">
      <p className="flex items-center gap-2 font-semibold text-texto">
        <ShoppingCart className="h-4 w-4 text-acento-claro" aria-hidden="true" />
        ¿Dónde lo compro?
      </p>
      <p className="mt-1 text-sm text-texto-2">Buscá proveedores y compará precios, envíos y reputación antes de comprar.</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {MERCADOS.map((m) => (
          <a
            key={m.nombre}
            href={m.url(consulta)}
            target="_blank"
            rel="noopener noreferrer nofollow"
            className="inline-flex items-center gap-1.5 rounded-lg border border-borde px-3 py-2 text-sm text-texto-2 transition-colors hover:border-borde-fuerte hover:text-texto"
          >
            {m.nombre}
            <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
          </a>
        ))}
      </div>
    </div>
  );
}
