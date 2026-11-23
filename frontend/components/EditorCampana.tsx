"use client";

/** Ver, editar, compartir y borrar una campaña guardada (docs/004-Backend/03, secciones 1 y 2). */
import { useState } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, Lightbulb, Pencil, Save, Trash2, Users, X } from "lucide-react";
import AccionesCanal from "@/components/AccionesCanal";
import DescargarCampana from "@/components/DescargarCampana";
import { editarCampana, eliminarCampana } from "@/lib/api/acciones";
import type { CampanaDetalle, CopyTexto } from "@/lib/api/campanas";
import { etiquetaCanal } from "@/lib/etiquetas";
import { BOTON_PRIMARIO, CAMPO } from "@/components/ui/estilos";

interface EditorCampanaProps {
  campana: CampanaDetalle;
  puedeEditar: boolean;
}

export default function EditorCampana({ campana, puedeEditar }: EditorCampanaProps) {
  const router = useRouter();
  const [editando, setEditando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [titulo, setTitulo] = useState(campana.titulo);
  const [angulos, setAngulos] = useState<string[]>(campana.contenido.angulos);
  const [publico, setPublico] = useState(campana.contenido.publico_objetivo);
  const [copy, setCopy] = useState<Record<string, CopyTexto[]>>(campana.contenido.copy_por_canal);

  function cambiarCopy(canal: string, i: number, campo: keyof CopyTexto, valor: string) {
    setCopy((actual) => ({
      ...actual,
      [canal]: actual[canal].map((t, j) => (j === i ? { ...t, [campo]: valor } : t)),
    }));
  }

  async function guardar() {
    setGuardando(true);
    setError(null);
    try {
      await editarCampana(campana.id, {
        titulo: titulo.trim() || campana.titulo,
        angulos: angulos.map((a) => a.trim()).filter(Boolean),
        publico_objetivo: publico,
        copy_por_canal: copy,
      });
      setEditando(false);
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo guardar.");
    } finally {
      setGuardando(false);
    }
  }

  async function borrar() {
    if (!window.confirm("¿Borrar esta campaña de tu historial?")) return;
    try {
      await eliminarCampana(campana.id);
      router.push("/campanas");
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo borrar.");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-2">
        {editando ? (
          <input
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            maxLength={150}
            aria-label="Título de la campaña"
            className={`${CAMPO} max-w-xl flex-1`}
          />
        ) : (
          <h2 className="flex-1 text-xl font-bold text-texto">{campana.titulo}</h2>
        )}
        <DescargarCampana titulo={titulo} angulos={angulos} publico={publico} copyPorCanal={copy} />
        {puedeEditar && !editando && (
          <button type="button" onClick={() => setEditando(true)} className="inline-flex items-center gap-2 rounded-lg border border-borde px-3 py-2 text-sm text-texto-2 hover:text-texto">
            <Pencil className="h-4 w-4" aria-hidden="true" /> Editar
          </button>
        )}
        {puedeEditar && !editando && (
          <button type="button" onClick={borrar} className="inline-flex items-center gap-2 rounded-lg border border-rojo-borde px-3 py-2 text-sm text-rojo hover:bg-rojo-fondo">
            <Trash2 className="h-4 w-4" aria-hidden="true" /> Borrar
          </button>
        )}
      </div>

      {error && (
        <p role="alert" className="rounded-lg border border-rojo-borde bg-rojo-fondo px-3 py-2 text-sm text-rojo">
          {error}
        </p>
      )}

      <section>
        <p className="mb-3 flex items-center gap-2 text-sm font-semibold text-texto">
          <Lightbulb className="h-4 w-4 text-ambar" aria-hidden="true" /> Ideas para la campaña
        </p>
        <ol className="space-y-2">
          {angulos.map((angulo, i) => (
            <li key={i} className="flex gap-3 rounded-xl bg-fondo/60 px-4 py-3 text-sm text-texto">
              <span className="font-mono text-acento-claro">{String(i + 1).padStart(2, "0")}</span>
              {editando ? (
                <input
                  value={angulo}
                  maxLength={300}
                  aria-label={`Idea ${i + 1}`}
                  onChange={(e) => setAngulos((a) => a.map((x, j) => (j === i ? e.target.value : x)))}
                  className={`${CAMPO} flex-1`}
                />
              ) : (
                <span className="min-w-0 break-words">{angulo}</span>
              )}
            </li>
          ))}
        </ol>
      </section>

      <section>
        <p className="mb-2 flex items-center gap-2 text-sm font-semibold text-texto">
          <Users className="h-4 w-4 text-acento-claro" aria-hidden="true" /> A quién le hablás
        </p>
        {editando ? (
          <textarea value={publico} maxLength={600} rows={3} onChange={(e) => setPublico(e.target.value)} aria-label="Público" className={CAMPO} />
        ) : (
          <p className="break-words rounded-xl bg-fondo/60 px-4 py-3 text-sm leading-relaxed text-texto">{publico}</p>
        )}
      </section>

      {Object.entries(copy).map(([canal, textos]) => (
        <section key={canal}>
          <p className="mb-2 text-sm font-semibold text-texto">Textos para {etiquetaCanal(canal)}</p>
          <div className="space-y-2">
            {textos.map((t, i) => (
              <div key={i} className="rounded-xl border border-borde bg-fondo p-4">
                {editando ? (
                  <div className="space-y-2">
                    <input value={t.titulo} maxLength={150} aria-label="Título del texto" onChange={(e) => cambiarCopy(canal, i, "titulo", e.target.value)} className={CAMPO} />
                    <textarea value={t.cuerpo} maxLength={1500} rows={4} aria-label="Cuerpo del texto" onChange={(e) => cambiarCopy(canal, i, "cuerpo", e.target.value)} className={CAMPO} />
                  </div>
                ) : (
                  <>
                    <p className="break-words text-sm font-semibold text-texto">{t.titulo}</p>
                    <p className="mt-1 whitespace-pre-line break-words text-sm leading-relaxed text-texto-2">{t.cuerpo}</p>
                    <AccionesCanal titulo={t.titulo} cuerpo={t.cuerpo} />
                  </>
                )}
              </div>
            ))}
          </div>
        </section>
      ))}

      {campana.contenido.advertencias.length > 0 && (
        <div className="space-y-1.5 rounded-xl border border-ambar-borde bg-ambar-fondo/60 p-4">
          <p className="flex items-center gap-2 text-sm font-semibold text-ambar">
            <AlertTriangle className="h-4 w-4" aria-hidden="true" /> Antes de publicar
          </p>
          {campana.contenido.advertencias.map((a, i) => (
            <p key={i} className="break-words text-sm text-texto">{a}</p>
          ))}
        </div>
      )}

      {editando && (
        <div className="flex flex-wrap gap-2">
          <button type="button" onClick={guardar} disabled={guardando} className={`px-5 py-2.5 ${BOTON_PRIMARIO}`}>
            <Save className="h-4 w-4" aria-hidden="true" /> {guardando ? "Guardando…" : "Guardar cambios"}
          </button>
          <button
            type="button"
            onClick={() => {
              setEditando(false);
              setTitulo(campana.titulo);
              setAngulos(campana.contenido.angulos);
              setPublico(campana.contenido.publico_objetivo);
              setCopy(campana.contenido.copy_por_canal);
            }}
            className="inline-flex items-center gap-2 rounded-lg border border-borde px-4 py-2.5 text-sm text-texto-2"
          >
            <X className="h-4 w-4" aria-hidden="true" /> Cancelar
          </button>
        </div>
      )}
    </div>
  );
}
