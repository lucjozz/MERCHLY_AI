/** Tarjeta del panel: las fechas comerciales que se vienen (docs/004-Backend/05, sección 3). */
import Link from "next/link";
import { CalendarDays } from "lucide-react";
import Card, { TituloCard } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import type { Temporada } from "@/lib/api/temporadas";

function cuando(dias: number): string {
  if (dias === 0) return "Es hoy";
  if (dias === 1) return "Mañana";
  return `En ${dias} días`;
}

function fechaCorta(iso: string): string {
  const [, mes, dia] = iso.split("-");
  return `${Number(dia)}/${Number(mes)}`;
}

export default function ProximasTemporadas({ temporadas }: { temporadas: Temporada[] }) {
  if (temporadas.length === 0) return null;
  return (
    <Card as="section" aria-label="Próximas temporadas">
      <TituloCard descripcion="Fechas en las que más se vende en Bolivia. Si importás, preparate con tiempo.">
        <span className="inline-flex items-center gap-2">
          <CalendarDays className="h-4 w-4 text-acento-claro" aria-hidden="true" />
          Próximas temporadas
        </span>
      </TituloCard>
      <div className="grid gap-3 md:grid-cols-3">
        {temporadas.slice(0, 3).map((t) => (
          <div key={t.clave} className="rounded-xl border border-borde bg-fondo p-4">
            <div className="flex items-start justify-between gap-2">
              <p className="font-semibold text-texto">{t.nombre}</p>
              {t.preparar_ya && <Badge tono="ambar" punto>Empezá ya</Badge>}
            </div>
            <p className="mt-1 text-sm text-texto-2">
              {cuando(t.dias_faltantes)} · {t.aproximada ? "aprox. " : ""}{fechaCorta(t.fecha)}
            </p>
            <ul className="mt-3 flex flex-wrap gap-1.5">
              {t.ideas.map((idea) => (
                <li key={idea}>
                  <Link
                    href={`/productos?buscar=${encodeURIComponent(idea)}`}
                    className="inline-block rounded-full border border-borde-fuerte px-2.5 py-1 text-xs text-texto transition-colors hover:border-acento-borde hover:text-acento-claro"
                  >
                    {idea}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </Card>
  );
}
