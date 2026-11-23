import { CircleCheck, Clock, ShieldCheck, Workflow, Sprout } from "lucide-react";
import {
  listarProductosCandidatos,
  type ProductoCandidato,
} from "@/lib/api/productos-candidatos";
import PageHeader from "@/components/ui/PageHeader";
import Card, { TituloCard } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Alerta from "@/components/ui/Alerta";
import { PISTA_BARRA } from "@/components/ui/estilos";
import { etiquetaNivel } from "@/lib/etiquetas";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";

export const dynamic = "force-dynamic";

const MUESTRA_MINIMA = 3;
const DECISIONES_MINIMAS = 5;

type Atributo = "nivel_demanda_estimado" | "nivel_competencia_estimado";

const ATRIBUTOS: { clave: Atributo; etiqueta: string }[] = [
  { clave: "nivel_demanda_estimado", etiqueta: "Demanda" },
  { clave: "nivel_competencia_estimado", etiqueta: "Competencia" },
];

const PASOS = [
  { titulo: "Una persona decide", activo: true },
  { titulo: "Se registra el motivo y la evidencia", activo: true },
  { titulo: "El sistema detecta patrones", activo: true },
  { titulo: "Se miden resultados reales de venta", activo: false },
  { titulo: "Una persona aprueba la regla", activo: false },
];

interface Patron {
  etiqueta: string;
  nivel: string;
  muestra: number;
  aprobados: number;
  tasa: number;
}

function detectarPatrones(decididos: ProductoCandidato[]): Patron[] {
  const patrones: Patron[] = [];
  for (const { clave, etiqueta } of ATRIBUTOS) {
    for (const nivel of ["alto", "medio", "bajo"]) {
      const grupo = decididos.filter((p) => p[clave] === nivel);
      if (grupo.length < MUESTRA_MINIMA) continue;
      const aprobados = grupo.filter((p) => p.estado === "en_catalogo").length;
      patrones.push({
        etiqueta,
        nivel,
        muestra: grupo.length,
        aprobados,
        tasa: Math.round((aprobados / grupo.length) * 100),
      });
    }
  }
  return patrones.sort((a, b) => b.tasa - a.tasa);
}

export default async function Automatizacion() {
  let decididos: ProductoCandidato[] = [];
  let error: string | null = null;

  try {
    const [aprobados, descartados] = await Promise.all([
      listarProductosCandidatos(1, 100, undefined, "en_catalogo"),
      listarProductosCandidatos(1, 100, undefined, "descartado"),
    ]);
    decididos = [...aprobados.productos, ...descartados.productos];
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }

  const patrones = detectarPatrones(decididos);
  const avance = Math.min(100, Math.round((decididos.length / DECISIONES_MINIMAS) * 100));

  return (
    <>
      <PageHeader
        titulo="Automatización"
        icono={Workflow}
        descripcion="Qué está aprendiendo el sistema de tus decisiones."
        ayuda="Con cada producto que aprobás o descartás, el sistema busca patrones (por ejemplo: “apruebo más los de demanda alta”). Son solo propuestas: nada se automatiza sin que una persona lo apruebe."
      />

      {error && <Alerta className="mb-6">{error}</Alerta>}

      <div className="mb-6 grid gap-6 lg:grid-cols-[300px_1fr]">
        <Card className="h-fit">
          <TituloCard>Cómo aprende</TituloCard>
          <ol className="relative space-y-4 before:absolute before:bottom-2 before:left-[7px] before:top-2 before:w-px before:bg-borde">
            {PASOS.map((paso) => (
              <li key={paso.titulo} className="relative flex items-start gap-3 text-sm">
                <span className="relative z-10 bg-superficie">
                  {paso.activo ? (
                    <CircleCheck className="h-4 w-4 text-verde" aria-hidden="true" />
                  ) : (
                    <Clock className="h-4 w-4 text-texto-3" aria-hidden="true" />
                  )}
                </span>
                <span className={paso.activo ? "text-texto" : "text-texto-2"}>
                  {paso.titulo}
                  {!paso.activo && (
                    <span className="block text-xs text-texto-2">Todavía no disponible</span>
                  )}
                </span>
              </li>
            ))}
          </ol>
        </Card>

        <Card>
          <TituloCard
            descripcion="Qué tipo de productos tendés a aprobar."
            accion={<Badge tono="azul">Propuestas · requieren revisión humana</Badge>}
          >
            Patrones detectados
          </TituloCard>

          {!error && decididos.length < DECISIONES_MINIMAS && (
            <div className="rounded-2xl border border-dashed border-borde-fuerte bg-fondo/50 p-5 text-center">
              <Sprout className="mx-auto h-6 w-6 text-verde" aria-hidden="true" />
              <p className="mt-3 font-medium text-texto">Todavía está aprendiendo</p>
              <p className="mt-1 text-sm text-texto-2">
                Llevás {decididos.length} de {DECISIONES_MINIMAS} decisiones necesarias
                para empezar a detectar patrones.
              </p>
              <div className={`mx-auto mt-4 max-w-xs ${PISTA_BARRA}`}>
                <div
                  className="h-full rounded-full bg-gradient-to-r from-acento to-verde transition-[width] duration-700"
                  style={{ width: `${avance}%` }}
                />
              </div>
            </div>
          )}

          {decididos.length >= DECISIONES_MINIMAS && patrones.length === 0 && (
            <p className="text-sm text-texto-2">
              Ningún grupo tiene todavía al menos {MUESTRA_MINIMA} decisiones para comparar.
            </p>
          )}

          <div className="space-y-5">
            {patrones.map((p) => (
              <div key={`${p.etiqueta}-${p.nivel}`}>
                <div className="mb-1.5 flex flex-wrap justify-between gap-2 text-sm">
                  <span className="text-texto">
                    {p.etiqueta} {etiquetaNivel(p.nivel).toLowerCase()}
                  </span>
                  <span className="tabular-nums text-texto-2">
                    Aprobaste {p.aprobados} de {p.muestra} · {p.tasa}%
                  </span>
                </div>
                <div className={PISTA_BARRA}>
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-acento-boton to-acento-claro transition-[width] duration-700"
                    style={{ width: `${p.tasa}%` }}
                  />
                </div>
                {p.muestra < 10 && (
                  <p className="mt-1 text-xs text-texto-2">
                    Pocos casos todavía: tomalo como orientativo.
                  </p>
                )}
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="flex items-start gap-3 rounded-2xl border border-verde-borde bg-verde-fondo/40 p-5">
        <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-verde" aria-hidden="true" />
        <p className="text-sm leading-relaxed text-texto">
          La IA aprende de las decisiones humanas, pero no convierte ese
          aprendizaje en reglas sin la aprobación de una persona.
        </p>
      </div>
    </>
  );
}
