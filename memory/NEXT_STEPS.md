# MERCHLY AI NEXT STEPS


## Prioridad actual

Verificar el proveedor real de Gemini (ProveedorInvestigacionGemini) contra la API real de Google. Esta verificación requiere una GEMINI_API_KEY válida y acceso de red a Google — no puede completarse desde el entorno de ejecución del asistente; corresponde al usuario, en su máquina o en un pipeline de CI/CD.


---

# Próximas tareas


## 1

Verificación real de Gemini:

- Configurar GEMINI_API_KEY en backend/.env (nunca en .env.example).
- Levantar el backend (docker compose up -d) y probar POST /agentes/investigador-producto con una categoría real.
- Confirmar que la respuesta viene de Gemini (no del proveedor simulado) y que respeta el prompt documentado en docs/010-Prompts/02-Prompt-Investigador-de-Producto.md (no inventa evidencia, respeta restricciones).
- Actualizar docs/007-Agentes/04-Registro-de-Agentes.md y docs/010-Prompts/03-Registro-de-Prompts.md quitando la nota de "pendiente verificación final" una vez confirmado.


---

## 2

Especificar el siguiente agente:

- Candidatos, según docs/007-Agentes/04-Registro-de-Agentes.md: SEO, contenido, atención al cliente (primer nivel), analítica básica, marketing.
- Seguir el mismo proceso ya validado: contrato técnico (007-Agentes) → esquema de datos si hace falta (006-BaseDatos) → prompt (010-Prompts) → implementación en código.


---

## 3

Evaluar próximo volumen de documentación:

- docs/004-Backend y docs/005-Frontend siguen vacíos (placeholders). El código de backend ya avanzó bastante sin que exista su volumen de documentación formal — conviene documentar lo ya construido antes de seguir agregando funcionalidad, para no acumular deuda de documentación.


---

# Objetivo siguiente etapa

Con el primer agente operando de punta a punta (validación → investigación → persistencia → API) y su integración real a Gemini implementada (pendiente solo de verificación con credenciales reales), el proyecto tiene ya un patrón repetible para agregar agentes nuevos. El siguiente foco es decidir si conviene reforzar ese patrón (documentar 004-Backend con lo ya construido) antes de escalarlo a más agentes.
