"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Package,
  Bot,
  Workflow,
  Sparkles,
  BarChart3,
  Zap,
  Clock,
  Settings,
} from "lucide-react";

const ITEMS_NAV = [
  { href: "/", label: "Dashboard", icono: LayoutDashboard },
  { href: "/productos", label: "Productos", icono: Package },
  { href: "/agentes", label: "Agentes", icono: Bot },
  { href: "/automatizacion", label: "Automatización", icono: Workflow },
  { href: "/marketing", label: "Marketing", icono: Sparkles },
  { href: "/analytics", label: "Analytics", icono: BarChart3 },
];

const ITEMS_NAV_INFERIOR = [
  { href: "/decisiones", label: "Decisiones", icono: Zap },
  { href: "/actividad", label: "Actividad", icono: Clock },
  { href: "/configuracion", label: "Configuración", icono: Settings },
];

function estiloItem(activo: boolean) {
  return `flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors ${
    activo
      ? "bg-[#1E3A5F] text-[#F5F7FA] font-medium"
      : "text-[#7C8699] hover:bg-[#12151C] hover:text-[#F5F7FA]"
  }`;
}

const ETIQUETA =
  "whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200";

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="group fixed left-0 top-0 z-40 h-screen w-16 hover:w-60 overflow-hidden bg-[#0B0D12] border-r border-[#1F2430] flex flex-col px-3 py-6 transition-[width] duration-300 ease-out">
      <div className="mb-8 px-3">
        <div className="flex items-center gap-3">
          <Sparkles
            className="h-4 w-4 shrink-0 text-[#F5F7FA]"
            aria-hidden="true"
          />
          <span className={`text-[#F5F7FA] font-bold text-lg ${ETIQUETA}`}>
            MERCHLY
          </span>
        </div>
        <p className={`text-[#5B6272] text-xs mt-0.5 ml-7 ${ETIQUETA}`}>
          AI COMMERCE OS
        </p>
      </div>

      <nav className="flex flex-col gap-1">
        {ITEMS_NAV.map((item) => {
          const Icono = item.icono;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={estiloItem(pathname === item.href)}
            >
              <Icono className="h-4 w-4 shrink-0" aria-hidden="true" />
              <span className={ETIQUETA}>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-[#1F2430] my-4" />

      <nav className="flex flex-col gap-1">
        {ITEMS_NAV_INFERIOR.map((item) => {
          const Icono = item.icono;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={estiloItem(pathname === item.href)}
            >
              <Icono className="h-4 w-4 shrink-0" aria-hidden="true" />
              <span className={ETIQUETA}>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}