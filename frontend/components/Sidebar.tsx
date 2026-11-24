"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Package,
  Bot,
  Workflow,
  Megaphone,
  BarChart3,
  Scale,
  Clock,
  Settings,
  CreditCard,
  History,
  Users,
  LifeBuoy,
  Sparkles,
  MessageCircle,
  Boxes,
  Headset,
  Menu,
  X,
  type LucideIcon,
} from "lucide-react";

interface ItemNav {
  href: string;
  label: string;
  /** Texto corto para la barra inferior en móvil. */
  corto?: string;
  icono: LucideIcon;
}

/** Ordenado como el flujo principal: buscar → decidir → promocionar. */
const FLUJO: ItemNav[] = [
  { href: "/", label: "Inicio", icono: LayoutDashboard },
  { href: "/productos", label: "Productos", icono: Package },
  { href: "/decisiones", label: "Decisiones", icono: Scale },
  { href: "/marketing", label: "Marketing", icono: Megaphone },
  { href: "/campanas", label: "Mis campañas", icono: History },
  { href: "/inventario", label: "Inventario", icono: Boxes },
  { href: "/atencion", label: "Atención al cliente", icono: Headset },
  { href: "/catalogo", label: "Catálogo WhatsApp", icono: MessageCircle },
];

const INTELIGENCIA: ItemNav[] = [
  { href: "/analytics", label: "Analytics", icono: BarChart3 },
  { href: "/agentes", label: "Agentes", icono: Bot },
  { href: "/automatizacion", label: "Automatización", icono: Workflow },
  { href: "/actividad", label: "Actividad", icono: Clock },
];

const CUENTA: ItemNav[] = [
  { href: "/equipo", label: "Equipo", icono: Users },
  { href: "/planes", label: "Plan y pagos", icono: CreditCard },
  { href: "/configuracion", label: "Configuración", icono: Settings },
  { href: "/ayuda", label: "Ayuda", icono: LifeBuoy },
];

function estaActivo(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

const ETIQUETA =
  "whitespace-nowrap opacity-0 transition-opacity duration-200 group-hover:opacity-100 group-focus-within:opacity-100";

function LinkEscritorio({ item, activo }: { item: ItemNav; activo: boolean }) {
  const Icono = item.icono;
  return (
    <Link
      href={item.href}
      aria-current={activo ? "page" : undefined}
      title={item.label}
      className={`relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
        activo
          ? "bg-acento-hondo font-medium text-texto"
          : "text-texto-2 hover:bg-superficie hover:text-texto"
      }`}
    >
      {activo && (
        <span
          className="absolute -left-3 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-acento"
          aria-hidden="true"
        />
      )}
      <Icono className="h-4 w-4 shrink-0" aria-hidden="true" />
      <span className={ETIQUETA}>{item.label}</span>
    </Link>
  );
}

function Grupo({
  titulo,
  items,
  pathname,
}: {
  titulo: string;
  items: ItemNav[];
  pathname: string;
}) {
  return (
    <div>
      <p
        className={`mb-1 px-3 text-[11px] font-semibold uppercase tracking-wider text-texto-3 ${ETIQUETA}`}
      >
        {titulo}
      </p>
      <div className="flex flex-col gap-1">
        {items.map((item) => (
          <LinkEscritorio
            key={item.href}
            item={item}
            activo={estaActivo(pathname, item.href)}
          />
        ))}
      </div>
    </div>
  );
}

function Logo({ siempreVisible = false }: { siempreVisible?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-acento to-acento-hondo shadow-lg shadow-acento/20">
        <Sparkles className="h-4 w-4 text-white" aria-hidden="true" />
      </span>
      <span className={siempreVisible ? "" : ETIQUETA}>
        <span className="block text-base font-bold leading-tight text-texto">
          MERCHLY
        </span>
        <span className="block text-[10px] font-medium tracking-widest text-texto-2">
          AI COMMERCE OS
        </span>
      </span>
    </div>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const [menuAbierto, setMenuAbierto] = useState(false);

  useEffect(() => {
    if (!menuAbierto) return;
    function alPresionar(e: KeyboardEvent) {
      if (e.key === "Escape") setMenuAbierto(false);
    }
    window.addEventListener("keydown", alPresionar);
    return () => window.removeEventListener("keydown", alPresionar);
  }, [menuAbierto]);

  // La pantalla de login ocupa toda la vista: sin navegación.
  if (["/login", "/invitacion", "/olvide", "/restablecer"].some((r) => pathname.startsWith(r))) return null;

  const enMenuMas = [...INTELIGENCIA, ...CUENTA].some((i) =>
    estaActivo(pathname, i.href)
  );

  return (
    <>
      {/* Escritorio: barra lateral fija que se expande al pasar el mouse o con foco de teclado. */}
      <aside
        aria-label="Navegación principal"
        className="group fixed left-0 top-0 z-40 hidden h-screen w-16 flex-col overflow-hidden border-r border-borde bg-fondo/95 px-3 py-5 backdrop-blur transition-[width] duration-300 ease-out hover:w-60 focus-within:w-60 hover:shadow-2xl hover:shadow-black/50 md:flex"
      >
        <div className="mb-8 px-1">
          <Logo />
        </div>

        <nav className="flex flex-1 flex-col gap-6">
          <Grupo titulo="Tu flujo" items={FLUJO} pathname={pathname} />
          <Grupo titulo="Inteligencia" items={INTELIGENCIA} pathname={pathname} />
          <div className="mt-auto">
            <Grupo titulo="Cuenta" items={CUENTA} pathname={pathname} />
          </div>
        </nav>
      </aside>

      {/* Móvil: barra inferior con el flujo principal + menú "Más". */}
      <nav
        aria-label="Navegación principal"
        className="fixed inset-x-0 bottom-0 z-40 border-t border-borde bg-fondo/95 pb-[env(safe-area-inset-bottom)] backdrop-blur md:hidden"
      >
        <ul className="grid grid-cols-5">
          {FLUJO.map((item) => {
            const Icono = item.icono;
            const activo = estaActivo(pathname, item.href);
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  aria-current={activo ? "page" : undefined}
                  className={`flex flex-col items-center gap-1 px-1 py-2.5 text-[11px] font-medium transition-colors ${
                    activo ? "text-acento-claro" : "text-texto-2 hover:text-texto"
                  }`}
                >
                  <span
                    className={`flex h-7 w-12 items-center justify-center rounded-full transition-colors ${
                      activo ? "bg-acento-hondo" : ""
                    }`}
                  >
                    <Icono className="h-5 w-5" aria-hidden="true" />
                  </span>
                  {item.corto ?? item.label}
                </Link>
              </li>
            );
          })}
          <li>
            <button
              type="button"
              onClick={() => setMenuAbierto(true)}
              aria-expanded={menuAbierto}
              aria-controls="menu-movil"
              className={`flex w-full flex-col items-center gap-1 px-1 py-2.5 text-[11px] font-medium transition-colors ${
                enMenuMas ? "text-acento-claro" : "text-texto-2 hover:text-texto"
              }`}
            >
              <span
                className={`flex h-7 w-12 items-center justify-center rounded-full ${
                  enMenuMas ? "bg-acento-hondo" : ""
                }`}
              >
                <Menu className="h-5 w-5" aria-hidden="true" />
              </span>
              Más
            </button>
          </li>
        </ul>
      </nav>

      {menuAbierto && (
        <div className="fixed inset-0 z-50 md:hidden" id="menu-movil">
          <button
            type="button"
            aria-label="Cerrar menú"
            onClick={() => setMenuAbierto(false)}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-aparecer"
          />
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Más secciones"
            className="absolute inset-x-0 bottom-0 max-h-[85vh] overflow-y-auto rounded-t-3xl border-t border-borde bg-superficie px-5 pb-[calc(1.5rem+env(safe-area-inset-bottom))] pt-5 animate-aparecer"
          >
            <div className="mb-6 flex items-center justify-between">
              <Logo siempreVisible />
              <button
                type="button"
                onClick={() => setMenuAbierto(false)}
                autoFocus
                className="rounded-lg p-2 text-texto-2 hover:bg-superficie-2 hover:text-texto"
                aria-label="Cerrar menú"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>

            {[
              { titulo: "Tu flujo", items: FLUJO },
              { titulo: "Inteligencia", items: INTELIGENCIA },
              { titulo: "Cuenta", items: CUENTA },
            ].map((grupo) => (
              <div key={grupo.titulo} className="mb-5">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-texto-2">
                  {grupo.titulo}
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {grupo.items.map((item) => {
                    const Icono = item.icono;
                    const activo = estaActivo(pathname, item.href);
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setMenuAbierto(false)}
                        aria-current={activo ? "page" : undefined}
                        className={`flex items-center gap-3 rounded-xl border px-3 py-3 text-sm transition-colors ${
                          activo
                            ? "border-acento-borde bg-acento-hondo text-texto"
                            : "border-borde bg-fondo text-texto-2 hover:text-texto"
                        }`}
                      >
                        <Icono className="h-4 w-4 shrink-0" aria-hidden="true" />
                        {item.label}
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
