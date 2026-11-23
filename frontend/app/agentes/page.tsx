import { Bot, Search, Megaphone, BarChart3, type LucideIcon } from "lucide-react";
import { obtenerReporteAnalitica } from "@/lib/api/analitica";
import PageHeader from "@/components/ui/PageHeader";
import Alerta from "@/components/ui/Alerta";
import Badge, { BadgeSimulado } from "@/components/ui/Badge";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

const ROLES_NEGOCIO = [
  "Administrador principal",
  "Responsable técnico",
  "Responsable de negocio",
];

interface AgenteInfo {
  nombre: string;
  descripcion: string;
  queHace: string;
  icono: LucideIcon;
  colorIcono: string;
  nivel: string;
  proveedor: string;
  /** "si": siempre simulado; "puede": depende de la configuración; "no": no usa IA. */
  simulado: "si" | "puede" | "no";
  roles: string[];
  metricas: { valor: string; etiqueta: string }[];
  nota?: string;
}

export default async function Agentes() {
  let reporte;
  let error: string | null = null;

  try {
    reporte = await obtenerReporteAnalitica();
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  const investigaciones = reporte
    ? String(reporte.actividad_agente_investigador.total_investigaciones)
    : "—";
  const productos = reporte
    ? String(reporte.resumen_catalogo.total_productos_candidatos)
    : "—";

  const agentes: AgenteInfo[] = [
    {
      nombre: "Investigador de Producto",
      descripcion:
        "Dado un nicho, identifica productos con potencial de venta y devuelve evidencia de demanda y competencia.",
      queHace: "Te sugiere qué vender",
      icono: Search,
      colorIcono: "text-acento-claro bg-acento-hondo/60",
      nivel: "Solo analiza y recomienda",
      proveedor: "Gemini si hay clave configurada; si no, simulado",
      simulado: "puede",
      roles: ROLES_NEGOCIO,
      metricas: [
        { valor: investigaciones, etiqueta: "búsquedas en los últimos 30 días" },
        { valor: productos, etiqueta: "productos encontrados en los últimos 30 días" },
      ],
    },
    {
      nombre: "Marketing IA",
      descripcion:
        "Propone ángulos, copys y público objetivo para productos ya aprobados. Nunca publica ni gasta.",
      queHace: "Te propone campañas",
      icono: Megaphone,
      colorIcono: "text-ambar bg-ambar-fondo",
      nivel: "Solo analiza y recomienda",
      proveedor: "Simulado (integración con ChatGPT pendiente)",
      simulado: "si",
      roles: ROLES_NEGOCIO,
      metricas: [],
      nota: "Las campañas generadas no se guardan todavía.",
    },
    {
      nombre: "Analítica Básica",
      descripcion:
        "Resume el catálogo: distribución por categoría, estado y conversión a catálogo.",
      queHace: "Te resume tus números",
      icono: BarChart3,
      colorIcono: "text-verde bg-verde-fondo",
      nivel: "Solo lectura",
      proveedor: "Sin IA: cuenta y agrupa tus datos",
      simulado: "no",
      roles: [...ROLES_NEGOCIO, "Usuario operativo"],
      metricas: [
        { valor: productos, etiqueta: "productos analizados en los últimos 30 días" },
      ],
    },
  ];

  return (
    <>
      <PageHeader
        titulo="Agentes"
        icono={Bot}
        descripcion="Tu equipo digital. La IA recomienda; las personas deciden."
        ayuda="Cada agente hace una tarea concreta. Ninguno puede aprobar productos, publicar ni gastar dinero: eso siempre lo hace una persona."
      />

      {error && <Alerta className="mb-6">{error}</Alerta>}

      <div className="grid gap-4 lg:grid-cols-3">
        {agentes.map((agente, i) => {
          const Icono = agente.icono;
          return (
            <article
              key={agente.nombre}
              className="flex flex-col rounded-3xl border border-borde bg-superficie p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-borde-fuerte sm:p-6 animate-aparecer"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="flex items-start justify-between gap-3">
                <span className={`flex h-12 w-12 items-center justify-center rounded-2xl ${agente.colorIcono}`}>
                  <Icono className="h-6 w-6" aria-hidden="true" />
                </span>
                <div className="flex flex-wrap justify-end gap-1.5">
                  <Badge tono="verde" punto>
                    Disponible
                  </Badge>
                  {agente.simulado === "si" && <BadgeSimulado />}
                </div>
              </div>

              <p className="mt-4 text-xs font-semibold uppercase tracking-wider text-texto-2">
                {agente.queHace}
              </p>
              <h2 className="mt-1 text-lg font-semibold text-texto">{agente.nombre}</h2>
              <p className="mt-2 text-sm leading-relaxed text-texto-2">{agente.descripcion}</p>

              <dl className="mt-5 space-y-3 rounded-2xl bg-fondo/60 p-4 text-sm">
                <div>
                  <dt className="text-xs text-texto-2">Qué puede hacer</dt>
                  <dd className="mt-0.5 text-texto">{agente.nivel}</dd>
                </div>
                <div>
                  <dt className="text-xs text-texto-2">Motor</dt>
                  <dd className="mt-0.5 text-texto">
                    {agente.proveedor}
                    {agente.simulado === "puede" && (
                      <span className="mt-1 block text-xs text-texto-2">
                        Si es simulado, sus resultados llevan la marca “Simulado”.
                      </span>
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-texto-2">Quién puede usarlo</dt>
                  <dd className="mt-0.5 text-texto">{agente.roles.join(", ")}</dd>
                </div>
              </dl>

              {agente.metricas.length > 0 && (
                <div className="mt-5 flex flex-wrap gap-6 border-t border-borde pt-5">
                  {agente.metricas.map((metrica) => (
                    <div key={metrica.etiqueta} className="min-w-0 flex-1">
                      <p className="text-2xl font-bold tabular-nums text-texto">{metrica.valor}</p>
                      <p className="text-xs leading-snug text-texto-2">{metrica.etiqueta}</p>
                    </div>
                  ))}
                </div>
              )}

              {agente.nota && (
                <p className="mt-5 border-t border-borde pt-5 text-xs text-texto-2">
                  {agente.nota}
                </p>
              )}
            </article>
          );
        })}
      </div>
    </>
  );
}
