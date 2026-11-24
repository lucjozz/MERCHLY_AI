"use client";

/** Re-verificación antes de confirmar o rechazar un pago real (vale 10 minutos). */
import { useState } from "react";
import { Loader2, ShieldCheck } from "lucide-react";
import Dialogo from "@/components/Dialogo";
import { BOTON_PRIMARIO, BOTON_SECUNDARIO, CAMPO, ETIQUETA_CAMPO } from "@/components/ui/estilos";
import { fetchJson } from "@/lib/api/cliente";

export const REAUTENTICACION_REQUERIDA = "Confirmá que sos vos para continuar.";

export default function ConfirmarQueSosVos({ conDosPasos, onListo, onCancelar }: {
  conDosPasos: boolean; onListo: () => void; onCancelar: () => void;
}) {
  const [valor, setValor] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function confirmar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setOcupado(true);
    try {
      await fetchJson<void>("/auth/reautenticar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(conDosPasos ? { codigo: valor.trim() } : { password: valor }),
      });
      onListo();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo verificar.");
      setOcupado(false);
    }
  }

  return (
    <Dialogo titulo="Confirmá que sos vos" descripcion="Para confirmar pagos te lo pedimos de nuevo. Vale por 10 minutos." onCerrar={onCancelar} ancho="max-w-md">
      <form onSubmit={confirmar} className="space-y-4">
        <div>
          <label htmlFor="rv-valor" className={ETIQUETA_CAMPO}>
            {conDosPasos ? "Código de tu app de autenticación" : "Tu contraseña"}
          </label>
          <input
            id="rv-valor"
            type={conDosPasos ? "text" : "password"}
            inputMode={conDosPasos ? "numeric" : undefined}
            autoComplete={conDosPasos ? "one-time-code" : "current-password"}
            maxLength={conDosPasos ? 12 : 128}
            value={valor}
            onChange={(e) => setValor(e.target.value)}
            autoFocus
            required
            className={CAMPO}
          />
          {!conDosPasos && (
            <p className="mt-2 text-xs text-texto-3">Si entrás con Google y no tenés contraseña, activá la verificación en dos pasos en Configuración.</p>
          )}
        </div>
        {error && <p role="alert" className="text-sm text-rojo">{error}</p>}
        <div className="flex justify-end gap-2">
          <button type="button" onClick={onCancelar} className={BOTON_SECUNDARIO}>Cancelar</button>
          <button type="submit" disabled={ocupado || !valor} className={BOTON_PRIMARIO}>
            {ocupado ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <ShieldCheck className="h-4 w-4" aria-hidden="true" />}
            Confirmar
          </button>
        </div>
      </form>
    </Dialogo>
  );
}
