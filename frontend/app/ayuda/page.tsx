import { LifeBuoy, MessageCircle } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Card from "@/components/ui/Card";

export const dynamic = "force-dynamic";

const NUMERO = (process.env.NEXT_PUBLIC_SOPORTE_WHATSAPP ?? "").replace(/\D/g, "");

const PREGUNTAS: [string, string][] = [
  ["¿Cómo encuentro productos para vender?", "En Productos escribí una categoría (por ejemplo, \"mochilas antirrobo\") y elegí tu país. La IA te sugiere productos con demanda, competencia, precios estimados y riesgos."],
  ["¿La IA decide por mí?", "No. La IA solo recomienda. Vos aprobás o descartás cada producto, y esa decisión queda guardada con tu motivo."],
  ["¿Cómo veo los precios en bolivianos?", "En Configuración elegí \"Bolivianos\" y cargá el tipo de cambio que pagás. Desde ahí todos los precios se muestran en Bs."],
  ["¿Cómo calculo si me conviene un producto?", "En el detalle del producto está la calculadora de margen: cargá tu costo, el envío y los impuestos, y ves cuánto ganás por unidad."],
  ["¿Dónde se guardan mis campañas?", "En Mis campañas. Cada campaña que generás se guarda sola; podés editar los textos y compartirlos por WhatsApp o email."],
  ["¿MERCHLY publica en mis redes?", "No publica nada por su cuenta. Copiás o compartís el texto y vos decidís dónde y cuándo publicarlo."],
  ["¿Cómo sumo a mi socio o a un empleado?", "Si sos el administrador, en Equipo creás una invitación y le mandás el link. Elegís qué rol tiene."],
  ["¿Qué significa \"Simulado\"?", "Que ese resultado se generó sin IA real (modo de prueba). No lo uses para decisiones reales."],
  ["¿Mis datos los ven otros negocios?", "No. Cada negocio está aislado: ni otros clientes ni sus empleados pueden ver tus productos, decisiones o campañas."],
];

export default function Ayuda() {
  return (
    <>
      <PageHeader titulo="Ayuda" icono={LifeBuoy} descripcion="Respuestas rápidas a las dudas más comunes." />
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="space-y-3">
          {PREGUNTAS.map(([pregunta, respuesta]) => (
            <details key={pregunta} className="group rounded-2xl border border-borde bg-superficie p-4 open:border-borde-fuerte">
              <summary className="cursor-pointer list-none font-medium text-texto marker:hidden">
                <span className="mr-2 inline-block text-acento-claro transition-transform group-open:rotate-90">›</span>
                {pregunta}
              </summary>
              <p className="mt-2 pl-5 text-sm leading-relaxed text-texto-2">{respuesta}</p>
            </details>
          ))}
        </div>
        <Card className="h-fit">
          <p className="flex items-center gap-2 font-semibold text-texto">
            <MessageCircle className="h-4 w-4 text-verde" aria-hidden="true" /> ¿No encontrás lo que buscás?
          </p>
          {NUMERO ? (
            <>
              <p className="mt-2 text-sm text-texto-2">Escribinos por WhatsApp y te ayudamos.</p>
              <a
                href={`https://wa.me/${NUMERO}?text=${encodeURIComponent("Hola, necesito ayuda con MERCHLY AI.")}`}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-verde px-4 py-2.5 text-sm font-semibold text-fondo"
              >
                <MessageCircle className="h-4 w-4" aria-hidden="true" /> Escribir por WhatsApp
              </a>
            </>
          ) : (
            <p className="mt-2 text-sm text-texto-2">El canal de soporte por WhatsApp todavía no está configurado. Consultá con el administrador de tu negocio.</p>
          )}
        </Card>
      </div>
    </>
  );
}
