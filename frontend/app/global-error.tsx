"use client"; // Reemplaza al layout raíz si falla: tiene que tener su propio <html> y <body>

export default function ErrorGlobal({ retry }: { error: unknown; retry: () => void }) {
  return (
    <html lang="es">
      <body style={{ background: "#0b0d12", color: "#f5f7fa", fontFamily: "system-ui, sans-serif", display: "grid", placeItems: "center", minHeight: "100vh", margin: 0 }}>
        <div style={{ textAlign: "center", padding: 24 }}>
          <h1 style={{ fontSize: 20 }}>MERCHLY AI tuvo un problema</h1>
          <p style={{ color: "#7c8699" }}>Probá de nuevo en unos segundos.</p>
          <button type="button" onClick={() => retry()} style={{ marginTop: 16, padding: "10px 16px", borderRadius: 8, border: 0, background: "#2f6bc4", color: "white", cursor: "pointer" }}>
            Reintentar
          </button>
        </div>
      </body>
    </html>
  );
}
