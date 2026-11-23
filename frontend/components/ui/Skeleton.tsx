export default function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden="true"
      className={`animate-brillo rounded-lg bg-[linear-gradient(90deg,#12151c_0%,#1c2029_50%,#12151c_100%)] bg-[length:200%_100%] ${className}`}
    />
  );
}

/** Esqueleto genérico de página: encabezado + métricas + bloques. */
export function SkeletonPagina() {
  return (
    <div role="status" aria-live="polite">
      <span className="sr-only">Cargando...</span>
      <Skeleton className="h-9 w-56" />
      <Skeleton className="mt-3 h-4 w-full max-w-md" />
      <div className="mt-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-28 rounded-2xl" />
        ))}
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Skeleton className="h-64 rounded-2xl" />
        <Skeleton className="h-64 rounded-2xl" />
      </div>
    </div>
  );
}
