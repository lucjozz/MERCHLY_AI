"use client";

/**
 * Activar / desactivar la verificación en dos pasos (docs/013-Seguridad/09).
 * Activar: QR → código del celular → 10 códigos de respaldo (se muestran UNA sola vez).
 */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Copy, KeyRound, Loader2, ShieldCheck, ShieldOff } from "lucide-react";
import Card, { TituloCard } from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";
import { fetchJson } from "@/lib/api/cliente";

const J = { "Content-Type": "application/json" };

export default function DosPasos({ activado, esAdmin }: { activado: boolean; esAdmin: boolean }) {
  const router = useRouter();
  const [inicio, setInicio] = useState<{ secreto: string; qr: string } | null>(null);
  const [codigo, setCodigo] = useState("");
  const [respaldo, setRespaldo] = useState<string[] | null>(null);
  const [desactivando, setDesactivando] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function hacer(accion: () => Promise<void>) {
    setError(null);
    setOcupado(true);
    try {
      await accion();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo completar.");
    } finally {
      setOcupado(false);
    }
  }

  const empezar = () =>
    hacer(async () => setInicio(await fetchJson<{ secreto: string; qr: string }>("/auth/2fa/iniciar", { method: "POST" })));
  const activar = () =>
    hacer(async () => {
      const r = await fetchJson<{ codigos: string[] }>("/auth/2fa/activar", { method: "POST", headers: J, body: JSON.stringify({ codigo: codigo.trim() }) });
      setRespaldo(r.codigos);
      setInicio(null);
      setCodigo("");
    });
  const desactivar = () =>
    hacer(async () => {
      await fetchJson<void>("/auth/2fa/desactivar", { method: "POST", headers: J, body: JSON.stringify({ codigo: codigo.trim() }) });
      setDesactivando(false);
      setCodigo("");
      router.refresh();
    });

  return (
    <Card className="lg:col-span-2">
      <TituloCard
        descripcion="Además de tu contraseña, te pedimos un código que genera tu celular. Si alguien roba tu contraseña, igual no puede entrar ni confirmar pagos."
        accion={activado || respaldo ? <Badge tono="verde" punto>Activada</Badge> : <Badge tono="ambar" punto>Desactivada</Badge>}
      >
        <span className="inline-flex items-center gap-2"><ShieldCheck className="h-4 w-4 text-verde" aria-hidden="true" /> Verificación en dos pasos</span>
      </TituloCard>

      {respaldo && (
        <div className="rounded-xl border border-ambar-borde bg-ambar-fondo/40 p-4">
          <p className="font-semibold text-texto">¡Listo! Guardá estos códigos de respaldo</p>
          <p className="mt-1 text-sm text-texto-2">
            Sirven si perdés el celular. Cada uno se usa una sola vez y <strong className="text-texto">no los vamos a mostrar de nuevo</strong>. Guardalos en tu gestor de contraseñas o en papel.
          </p>
          <ul className="mt-3 grid grid-cols-2 gap-2 font-mono text-sm sm:grid-cols-5">
            {respaldo.map((c) => <li key={c} className="rounded-lg bg-fondo px-2 py-1.5 text-center text-texto">{c}</li>)}
          </ul>
          <div className="mt-3 flex gap-2">
            <button type="button" onClick={() => navigator.clipboard.writeText(respaldo.join("\n")).catch(() => undefined)} className={BOTON_SECUNDARIO}>
              <Copy className="h-4 w-4" aria-hidden="true" /> Copiar
            </button>
            <button type="button" onClick={() => { setRespaldo(null); router.refresh(); }} className={BOTON_PRIMARIO}>Ya los guardé</button>
          </div>
        </div>
      )}

      {!activado && !respaldo && !inicio && (
        <div>
          {esAdmin && <p className="mb-3 text-sm text-ambar">Como administrador, te recomendamos activarla: tu cuenta puede confirmar pagos y cambiar el equipo.</p>}
          <button type="button" onClick={empezar} disabled={ocupado} className={BOTON_PRIMARIO}>
            {ocupado ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <KeyRound className="h-4 w-4" aria-hidden="true" />}
            Activar
          </button>
        </div>
      )}

      {inicio && (
        <div className="grid gap-5 sm:grid-cols-[auto_1fr]">
          {/* eslint-disable-next-line @next/next/no-img-element -- QR generado por el backend (data URI SVG) */}
          <img src={inicio.qr} alt="Código QR para la app de autenticación" className="h-48 w-48 rounded-xl bg-white p-2" />
          <div className="space-y-3 text-sm">
            <ol className="list-decimal space-y-1 pl-5 text-texto-2">
              <li>Instalá Google Authenticator, Microsoft Authenticator o similar en tu celular.</li>
              <li>Tocá «Agregar» y escaneá este QR.</li>
              <li>Escribí el código de 6 dígitos que aparece.</li>
            </ol>
            <p className="text-xs text-texto-3">¿No podés escanear? Clave manual: <code className="break-all text-texto">{inicio.secreto}</code></p>
            <div>
              <label htmlFor="dp-codigo" className={ETIQUETA_CAMPO}>Código</label>
              <div className="flex gap-2">
                <input id="dp-codigo" value={codigo} onChange={(e) => setCodigo(e.target.value)} inputMode="numeric" maxLength={6} autoComplete="one-time-code" placeholder="123456" className={`${CAMPO} !w-36 text-center tracking-[0.3em]`} />
                <button type="button" onClick={activar} disabled={ocupado || codigo.trim().length !== 6} className={BOTON_PRIMARIO}>
                  {ocupado && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />} Activar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activado && !respaldo && (
        desactivando ? (
          <div className="flex flex-wrap items-end gap-2">
            <div>
              <label htmlFor="dp-off" className={ETIQUETA_CAMPO}>Código del celular (o de respaldo)</label>
              <input id="dp-off" value={codigo} onChange={(e) => setCodigo(e.target.value)} maxLength={12} autoComplete="one-time-code" className={`${CAMPO} !w-44`} />
            </div>
            <button type="button" onClick={desactivar} disabled={ocupado || codigo.trim().length < 6} className={BOTON_SECUNDARIO}>
              {ocupado && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />} Desactivar
            </button>
            <button type="button" onClick={() => { setDesactivando(false); setCodigo(""); }} className="text-sm text-texto-2 hover:text-texto">Cancelar</button>
          </div>
        ) : (
          <button type="button" onClick={() => setDesactivando(true)} className={BOTON_SECUNDARIO}>
            <ShieldOff className="h-4 w-4" aria-hidden="true" /> Desactivar
          </button>
        )
      )}

      {error && <p role="alert" className="mt-3 text-sm text-rojo">{error}</p>}
    </Card>
  );
}
