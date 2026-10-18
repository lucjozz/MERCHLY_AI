"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Loader2 } from "lucide-react";
import { iniciarSesion } from "@/lib/api/auth";
import { guardarToken } from "@/lib/auth";

export default function Login() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function entrar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setCargando(true);

    try {
      const sesion = await iniciarSesion(email.trim(), password);
      guardarToken(sesion.access_token, sesion.expira_en);
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "No se pudo iniciar sesión."
      );
      setCargando(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 bg-[#0B0D12] flex items-center justify-center px-6">
      <form
        onSubmit={entrar}
        className="w-full max-w-sm bg-[#12151C] border border-[#1F2430] rounded-lg p-8"
      >
        <div className="flex items-center gap-2 mb-1">
          <Sparkles className="h-5 w-5 text-[#F5F7FA]" aria-hidden="true" />
          <span className="text-[#F5F7FA] font-bold text-xl">MERCHLY</span>
        </div>
        <p className="text-[#5B6272] text-xs mb-8 ml-7">AI COMMERCE OS</p>

        <label className="text-[#7C8699] text-xs uppercase tracking-wide block mb-2">
          Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="username"
          required
          className="w-full bg-[#0B0D12] border border-[#242938] text-[#F5F7FA] rounded-md px-3 py-2.5 text-sm outline-none focus:border-[#3D7DD8] focus:ring-1 focus:ring-[#3D7DD8] mb-5"
        />

        <label className="text-[#7C8699] text-xs uppercase tracking-wide block mb-2">
          Contraseña
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
          className="w-full bg-[#0B0D12] border border-[#242938] text-[#F5F7FA] rounded-md px-3 py-2.5 text-sm outline-none focus:border-[#3D7DD8] focus:ring-1 focus:ring-[#3D7DD8] mb-6"
        />

        {error && (
          <p className="mb-4 text-sm text-[#E88B8B] bg-[#2A1414] border border-[#4A2020] rounded-md px-3 py-2">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={cargando}
          className="w-full inline-flex items-center justify-center gap-2 bg-[#1E3A5F] hover:bg-[#28507F] border border-[#2B4A73] text-white px-5 py-2.5 rounded-md text-sm font-semibold transition-colors disabled:opacity-50"
        >
          {cargando && (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          )}
          {cargando ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </div>
  );
}