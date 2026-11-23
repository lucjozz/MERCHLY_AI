"use client";

/** Equipo del negocio: invitar, cambiar rol, desactivar (solo admin; docs/004-Backend/03, sección 5). */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Check, Copy, Link2, UserPlus, X } from "lucide-react";
import { cambiarMiembro, invitarMiembro, revocarInvitacion } from "@/lib/api/acciones";
import type { Invitacion, Miembro } from "@/lib/api/equipo";
import { etiquetaRol, formatearFecha } from "@/lib/etiquetas";
import Badge from "@/components/ui/Badge";
import { BOTON_PRIMARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";

const ROLES = ["usuario_operativo", "responsable_negocio", "responsable_tecnico", "admin_principal"];

interface PanelEquipoProps {
  miembros: Miembro[];
  invitaciones: Invitacion[];
  miId: string;
}

export default function PanelEquipo({ miembros, invitaciones, miId }: PanelEquipoProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [rol, setRol] = useState("usuario_operativo");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [link, setLink] = useState<string | null>(null);
  const [codigo, setCodigo] = useState<string | null>(null);
  const [copiado, setCopiado] = useState(false);

  async function invitar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLink(null);
    setEnviando(true);
    try {
      const inv = await invitarMiembro(email.trim(), rol);
      // El token va en el fragmento (#): el navegador no lo manda al servidor ni a los logs.
      setCodigo(inv.token);
      setLink(`${window.location.origin}/invitacion#${inv.token}`);
      setEmail("");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo crear la invitación.");
    } finally {
      setEnviando(false);
    }
  }

  async function ejecutar(accion: () => Promise<unknown>) {
    setError(null);
    try {
      await accion();
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo completar la acción.");
    }
  }

  async function copiar() {
    if (!link) return;
    await navigator.clipboard.writeText(link).catch(() => window.prompt("Copiá el link:", link));
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  }

  const pendientes = invitaciones.filter(
    (i) => !i.aceptada_en && !i.revocada_en && new Date(i.expira_en) > new Date()
  );

  return (
    <div className="space-y-8">
      <form onSubmit={invitar} className="grid gap-4 rounded-2xl border border-borde bg-superficie p-5 sm:grid-cols-[1fr_220px_auto] sm:items-end">
        <div>
          <label htmlFor="inv-email" className={ETIQUETA_CAMPO}>Email de la persona</label>
          <input id="inv-email" type="email" required maxLength={255} value={email} onChange={(e) => setEmail(e.target.value)} placeholder="socio@tutienda.com" className={CAMPO} />
        </div>
        <div>
          <label htmlFor="inv-rol" className={ETIQUETA_CAMPO}>Rol</label>
          <select id="inv-rol" value={rol} onChange={(e) => setRol(e.target.value)} className={CAMPO}>
            {ROLES.map((r) => (
              <option key={r} value={r}>{etiquetaRol(r)}</option>
            ))}
          </select>
        </div>
        <button type="submit" disabled={enviando} className={`px-5 py-2.5 ${BOTON_PRIMARIO}`}>
          <UserPlus className="h-4 w-4" aria-hidden="true" /> {enviando ? "Creando…" : "Invitar"}
        </button>
      </form>

      {link && (
        <div role="status" className="rounded-2xl border border-verde-borde bg-verde-fondo/40 p-4">
          <p className="flex items-center gap-2 text-sm font-semibold text-verde">
            <Link2 className="h-4 w-4" aria-hidden="true" /> Invitación creada
          </p>
          <p className="mt-1 text-sm text-texto-2">
            Mandale el link por WhatsApp, o pasale el código para que lo escriba en la pantalla de invitación. Vale 7 días y se usa una sola vez.
          </p>
          {codigo && (
            <p className="mt-3 select-all font-mono text-2xl font-bold tracking-widest text-texto" aria-label="Código de invitación">
              {codigo}
            </p>
          )}
          <div className="mt-3 flex flex-wrap gap-2">
            <code className="min-w-0 flex-1 truncate rounded-lg bg-fondo px-3 py-2 text-xs text-texto">{link}</code>
            <button type="button" onClick={copiar} className="inline-flex items-center gap-1.5 rounded-lg border border-borde px-3 py-2 text-sm text-texto">
              {copiado ? <Check className="h-4 w-4 text-verde" aria-hidden="true" /> : <Copy className="h-4 w-4" aria-hidden="true" />}
              {copiado ? "¡Copiado!" : "Copiar"}
            </button>
            <a
              href={`https://wa.me/?text=${encodeURIComponent(`Te invito a nuestro negocio en MERCHLY AI: ${link}`)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center rounded-lg border border-borde px-3 py-2 text-sm text-texto"
            >
              WhatsApp
            </a>
          </div>
        </div>
      )}

      {error && <p role="alert" className="rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">{error}</p>}

      <section>
        <h2 className="mb-3 text-base font-semibold text-texto">Miembros ({miembros.length})</h2>
        <ul className="divide-y divide-borde rounded-2xl border border-borde bg-superficie">
          {miembros.map((m) => {
            const soyYo = m.id === miId;
            return (
              <li key={m.id} className="flex flex-wrap items-center gap-3 p-4">
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-texto">
                    {m.nombre} {soyYo && <span className="text-xs text-texto-3">(vos)</span>}
                  </p>
                  <p className="truncate text-sm text-texto-2">{m.email}</p>
                </div>
                {!m.activo && <Badge tono="gris">Desactivado</Badge>}
                {soyYo ? (
                  <Badge tono="azul">{etiquetaRol(m.rol)}</Badge>
                ) : (
                  <>
                    <select
                      aria-label={`Rol de ${m.nombre}`}
                      value={m.rol}
                      onChange={(e) => ejecutar(() => cambiarMiembro(m.id, { rol: e.target.value }))}
                      className={`${CAMPO} w-auto`}
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>{etiquetaRol(r)}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => {
                        if (m.activo && !window.confirm(`¿Desactivar a ${m.nombre}? Se cierran todas sus sesiones.`)) return;
                        ejecutar(() => cambiarMiembro(m.id, { activo: !m.activo }));
                      }}
                      className="rounded-lg border border-borde px-3 py-2 text-sm text-texto-2 hover:text-texto"
                    >
                      {m.activo ? "Desactivar" : "Reactivar"}
                    </button>
                  </>
                )}
              </li>
            );
          })}
        </ul>
      </section>

      {pendientes.length > 0 && (
        <section>
          <h2 className="mb-3 text-base font-semibold text-texto">Invitaciones pendientes</h2>
          <ul className="divide-y divide-borde rounded-2xl border border-borde bg-superficie">
            {pendientes.map((i) => (
              <li key={i.id} className="flex flex-wrap items-center gap-3 p-4">
                <div className="min-w-0 flex-1">
                  <p className="truncate text-texto">{i.email}</p>
                  <p className="text-xs text-texto-3">{etiquetaRol(i.rol)} · vence {formatearFecha(i.expira_en)}</p>
                </div>
                <button type="button" onClick={() => ejecutar(() => revocarInvitacion(i.id))} className="inline-flex items-center gap-1.5 rounded-lg border border-borde px-3 py-2 text-sm text-texto-2 hover:text-rojo">
                  <X className="h-4 w-4" aria-hidden="true" /> Revocar
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
