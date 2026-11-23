import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Sidebar from "@/components/Sidebar";
import BotonSoporte from "@/components/BotonSoporte";
import IndicadorDolar from "@/components/IndicadorDolar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Todo se renderiza por request: la Content-Security-Policy usa un nonce
// distinto en cada respuesta (proxy.ts) y Next solo puede inyectarlo en
// páginas dinámicas. Una página estática quedaría con sus scripts bloqueados.
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "MERCHLY AI",
  description:
    "La IA te recomienda qué vender y cómo promocionarlo. Vos decidís.",
};

export const viewport: Viewport = {
  themeColor: "#0B0D12",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full bg-fondo">
        <a
          href="#contenido"
          className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-lg focus:bg-acento-boton focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
        >
          Saltar al contenido
        </a>
        <Sidebar />
        <BotonSoporte />
        <main
          id="contenido"
          className="min-w-0 flex-1 pb-24 md:ml-16 md:pb-0"
        >
          <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 md:py-10 lg:px-10">
            <IndicadorDolar />
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
