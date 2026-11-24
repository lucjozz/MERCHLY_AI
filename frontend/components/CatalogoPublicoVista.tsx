/** La cara pública del inventario: exactamente lo que ve la IA (docs/007-Agentes/08, sección 2). */
import { Eye, ImageOff } from "lucide-react";
import Alerta from "@/components/ui/Alerta";
import EmptyState from "@/components/ui/EmptyState";
import Badge from "@/components/ui/Badge";
import { urlFoto, type ItemCatalogoPublico } from "@/lib/api/inventario";
import { formatearPrecioLocal } from "@/lib/moneda";

export default function CatalogoPublicoVista({ productos, moneda }: { productos: ItemCatalogoPublico[]; moneda: string }) {
  return (
    <>
      <Alerta tipo="info" className="mb-6">
        Así ve tus productos la IA. <strong className="text-texto">Nunca ve</strong> el costo, los gastos, el proveedor, tus notas ni tu stock real: solo cuántos hay disponibles para vender.
      </Alerta>
      {productos.length === 0 ? (
        <EmptyState
          icono={Eye}
          titulo="Tu catálogo público está vacío"
          descripcion="En «Mi inventario», marcá «Publicado» en los productos que quieras que la IA ofrezca a tus clientes."
          accion={{ href: "/inventario", texto: "Ir a mi inventario" }}
        />
      ) : (
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {productos.map((p) => (
            <li key={p.id} className="overflow-hidden rounded-2xl border border-borde bg-superficie">
              {p.foto_ids[0] ? (
                // eslint-disable-next-line @next/next/no-img-element -- foto privada servida por el BFF con sesión
                <img src={urlFoto(p.foto_ids[0])} alt={p.nombre} className="aspect-[4/3] w-full object-cover" />
              ) : (
                <div className="flex aspect-[4/3] items-center justify-center bg-superficie-2 text-texto-3">
                  <ImageOff className="h-6 w-6" aria-hidden="true" />
                  <span className="sr-only">Sin foto</span>
                </div>
              )}
              <div className="p-4">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-semibold text-texto">{p.nombre}</p>
                  <p className="whitespace-nowrap font-semibold tabular-nums text-texto">{formatearPrecioLocal(p.precio_venta, moneda)}</p>
                </div>
                <div className="mt-2">
                  {p.disponibles > 0 ? (
                    <Badge tono="verde" punto>{p.disponibles} disponibles</Badge>
                  ) : (
                    <Badge tono="rojo" punto>Agotado</Badge>
                  )}
                </div>
                {p.descripcion && <p className="mt-3 line-clamp-3 text-sm text-texto-2">{p.descripcion}</p>}
                {Object.keys(p.especificaciones).length > 0 && (
                  <dl className="mt-3 space-y-1 text-xs">
                    {Object.entries(p.especificaciones).map(([k, v]) => (
                      <div key={k} className="flex gap-2">
                        <dt className="text-texto-3">{k}:</dt>
                        <dd className="text-texto">{v}</dd>
                      </div>
                    ))}
                  </dl>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}
