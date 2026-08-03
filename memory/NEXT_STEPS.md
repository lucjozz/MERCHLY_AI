# MERCHLY AI NEXT STEPS


## Prioridad actual

Elegir el siguiente foco de trabajo: especificar un nuevo agente, o documentar docs/004-Backend con lo ya construido. Ver "Objetivo siguiente etapa" abajo.


---

# Próximas tareas


## 1

Especificar el siguiente agente:

- Candidatos, según docs/007-Agentes/04-Registro-de-Agentes.md: SEO, contenido, atención al cliente (primer nivel), analítica básica, marketing.
- Seguir el mismo proceso ya validado: contrato técnico (007-Agentes) → esquema de datos si hace falta (006-BaseDatos) → prompt (010-Prompts) → implementación en código.


---

## 2

Evaluar próximo volumen de documentación:

- docs/004-Backend y docs/005-Frontend siguen vacíos (placeholders). El código de backend ya avanzó bastante sin que exista su volumen de documentación formal — conviene documentar lo ya construido antes de seguir agregando funcionalidad, para no acumular deuda de documentación.


---

# Objetivo siguiente etapa

Con el primer agente operando de punta a punta (validación → investigación → persistencia → API), su integración real a Gemini implementada y verificada contra la API real (ver DEC-023), y el entorno local (Docker Compose + Alembic) documentado con los comandos reales, el proyecto tiene ya un patrón repetible para agregar agentes nuevos, sin pendientes bloqueantes conocidos. El siguiente foco es decidir si conviene reforzar ese patrón (documentar 004-Backend con lo ya construido) antes de escalarlo a más agentes.
