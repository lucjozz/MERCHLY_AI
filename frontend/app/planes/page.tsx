import { Check, CreditCard, Lock, ShieldCheck, Sparkles } from "lucide-react";
import PageHeader from "@/components/ui/PageHeader";
import Card, { TituloCard } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Alerta from "@/components/ui/Alerta";
import { obtenerUsuarioActual, type UsuarioActual } from "@/lib/api/usuario";
import { mensajeDeErrorDePagina } from "@/lib/api/errores-pagina";
import UsoDelPlan from "@/components/UsoDelPlan";
import { obtenerUsoPlan, type UsoPlan } from "@/lib/api/organizacion";

export const dynamic = "force-dynamic";

/**
 * Plan y pagos. Los cobros TODAVÍA NO están activos: falta elegir la
 * pasarela (ver docs/013-Seguridad/05). Todas las organizaciones están hoy
 * en la beta gratuita; los precios de los planes pagos no están definidos y
 * por eso no se muestran números inventados.
 */

interface Plan {
  id: string;
  nombre: string;
  para: string;
  precio: string;
  actual?: boolean;
  destacado?: boolean;
  incluye: string[];
}

const NOMBRE_PLAN: Record<string, string> = { beta: "Beta gratuita", emprendedor: "Emprendedor", negocio: "Negocio" };

const PLANES: Plan[] = [
  {
    id: "beta",
    nombre: "Beta",
    para: "Para probar MERCHLY con tu negocio",
    precio: "Gratis",
    actual: true,
    incluye: [
      "IA estándar para buscar productos y crear campañas",
      "Investigador de productos (hasta 30 búsquedas por hora)",
      "Campañas de marketing (hasta 60 por hora)",
      "Decisiones con historial",
      "Analytics básico",
      "Tu equipo dentro de tu negocio",
    ],
  },
  {
    id: "emprendedor",
    nombre: "Emprendedor",
    para: "Para tiendas que ya venden",
    precio: "Precio a definir",
    destacado: true,
    incluye: ["Todo lo de Beta", "IA avanzada: mejores búsquedas y textos", "Más búsquedas y campañas por mes", "Soporte por email"],
  },
  {
    id: "negocio",
    nombre: "Negocio",
    para: "Para equipos con varias personas",
    precio: "Precio a definir",
    incluye: ["Todo lo de Emprendedor", "IA premium: el modelo más potente", "Más usuarios y roles", "Soporte prioritario"],
  },
];

export default async function Planes() {
  let usuario: UsuarioActual | undefined;
  let uso: UsoPlan | null = null;
  let error: string | null = null;
  try {
    [usuario, uso] = await Promise.all([obtenerUsuarioActual(), obtenerUsoPlan().catch(() => null)]);
  } catch (e) {
    error = mensajeDeErrorDePagina(e);
  }
  const esAdmin = usuario?.rol === "admin_principal";

  return (
    <>
      <PageHeader
        titulo="Plan y pagos"
        icono={CreditCard}
        descripcion="Tu plan actual y cómo vas a poder pagar cuando abramos los planes pagos."
        ayuda="Por ahora todos los negocios usan la beta gratuita. Cuando activemos los pagos, el dueño del negocio va a poder elegir un plan desde acá."
      />

      {error && <Alerta>{error}</Alerta>}

      <Card className="mb-6 animate-aparecer">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-texto-2">Plan actual de {usuario?.organizacion_nombre ?? "tu negocio"}</p>
            <p className="mt-1 flex items-center gap-2 text-xl font-bold text-texto">
              <Sparkles className="h-5 w-5 text-acento-claro" aria-hidden="true" />
              {NOMBRE_PLAN[uso?.plan ?? "beta"] ?? "Beta gratuita"}
            </p>
          </div>
          <Badge tono="verde">Activo</Badge>
        </div>
      </Card>

      {uso && (
        <div className="mb-6">
          <UsoDelPlan uso={uso} />
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        {PLANES.map((plan) => (
          <Card
            key={plan.id}
            as="article"
            aria-label={`Plan ${plan.nombre}`}
            className={`flex flex-col ${plan.destacado ? "border-acento-borde" : ""}`}
          >
            <div className="flex items-center justify-between gap-2">
              <h2 className="text-lg font-semibold text-texto">{plan.nombre}</h2>
              {plan.id === (uso?.plan ?? "beta") && <Badge tono="verde">Tu plan</Badge>}
              {plan.destacado && plan.id !== (uso?.plan ?? "beta") && <Badge tono="azul">Recomendado</Badge>}
            </div>
            <p className="mt-1 text-sm text-texto-2">{plan.para}</p>
            <p className="mt-4 text-2xl font-bold text-texto">{plan.precio}</p>
            <ul className="mt-4 flex-1 space-y-2 text-sm">
              {plan.incluye.map((item) => (
                <li key={item} className="flex gap-2 text-texto-2">
                  <Check className="mt-0.5 h-4 w-4 shrink-0 text-verde" aria-hidden="true" />
                  {item}
                </li>
              ))}
            </ul>
            <button
              type="button"
              disabled
              className="mt-6 w-full cursor-not-allowed rounded-lg border border-borde px-4 py-2.5 text-sm font-semibold text-texto-3"
            >
              {plan.id === (uso?.plan ?? "beta") ? "Plan actual" : "Próximamente"}
            </button>
          </Card>
        ))}
      </div>

      <Card className="mt-6">
        <TituloCard descripcion="Así va a funcionar el cobro cuando lo activemos.">
          Pagos seguros
        </TituloCard>
        <ul className="grid gap-4 text-sm sm:grid-cols-3">
          <li className="flex gap-3">
            <Lock className="mt-0.5 h-4 w-4 shrink-0 text-acento-claro" aria-hidden="true" />
            <span className="text-texto-2">
              <span className="font-medium text-texto">MERCHLY nunca ve tu tarjeta.</span> Pagás en la página
              segura de la pasarela de pagos.
            </span>
          </li>
          <li className="flex gap-3">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-acento-claro" aria-hidden="true" />
            <span className="text-texto-2">
              <span className="font-medium text-texto">Solo el dueño paga.</span> Únicamente el administrador del
              negocio puede cambiar el plan.
            </span>
          </li>
          <li className="flex gap-3">
            <CreditCard className="mt-0.5 h-4 w-4 shrink-0 text-acento-claro" aria-hidden="true" />
            <span className="text-texto-2">
              <span className="font-medium text-texto">Cancelás cuando quieras</span> desde esta misma pantalla.
            </span>
          </li>
        </ul>
        <p className="mt-5 rounded-lg border border-borde bg-fondo px-4 py-3 text-sm text-texto-2">
          Los pagos todavía no están activos: estamos eligiendo la pasarela de pagos.
          {esAdmin
            ? " Como sos el administrador, te vamos a avisar cuando puedas elegir un plan."
            : " Cuando estén disponibles, el administrador de tu negocio va a poder elegir un plan."}
        </p>
      </Card>
    </>
  );
}
