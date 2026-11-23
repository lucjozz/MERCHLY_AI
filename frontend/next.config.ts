import type { NextConfig } from "next";

/**
 * Headers de seguridad (docs/013-Seguridad/04, sección 8). La
 * Content-Security-Policy con nonce la pone proxy.ts en cada request.
 */
const esProduccion = process.env.NODE_ENV === "production";

const headersSeguridad = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=(), usb=()" },
  // "allow-popups": la ventana de "Continuar con Google" necesita comunicarse
  // con esta página. Con "same-origin" queda colgada para siempre.
  { key: "Cross-Origin-Opener-Policy", value: "same-origin-allow-popups" },
  // HSTS solo con HTTPS real (producción). Empezar corto y subir después.
  ...(esProduccion ? [{ key: "Strict-Transport-Security", value: "max-age=86400; includeSubDomains" }] : []),
];

const nextConfig: NextConfig = {
  poweredByHeader: false,
  async headers() {
    return [{ source: "/:path*", headers: headersSeguridad }];
  },
};

export default nextConfig;
