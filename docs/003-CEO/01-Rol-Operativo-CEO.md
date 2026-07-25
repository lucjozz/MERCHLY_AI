# 01-Rol-Operativo-CEO.md

---

title: Rol Operativo del CEO
document: 003-01
version: 1.0.0
status: Draft
owner: CEO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* ../100-Organizacion/03-Roles-Ejecutivos.md
* ../000-Constitucion/07-Gobernanza.md
* ../002-CTO/01-Rol-Tecnico-Operativo.md

---

# Rol Operativo del CEO

## Propósito

`100-Organizacion/03-Roles-Ejecutivos.md` define al CEO como máxima autoridad estratégica. Este documento define su actuación concreta mientras el proyecto está en Fase 0, cuando no existe aún equipo humano más allá del fundador y los agentes IA.

---

# 1. Decisiones de Autoridad Directa

El CEO decide sin aprobación adicional:

* Prioridades comerciales dentro de la fase vigente.
* Aprobación o rechazo de propuestas técnicas con impacto estratégico presentadas por el CTO (conforme a `002-CTO/01-Rol-Tecnico-Operativo.md`, sección 3).
* Mensaje institucional y posicionamiento del proyecto hacia afuera.
* Criterios de éxito de cada fase (documentados en `03-Criterios-de-Exito-Fase0.md` y sucesivos).

---

# 2. Decisiones que Requieren Registro en DECISIONS.md

* Cambios al modelo de negocio definido en `02-Modelo-de-Negocio.md`.
* Cambios en el orden de fases del roadmap.
* Definición de métricas oficiales de éxito del proyecto.

---

# 3. Límites del CEO

Conforme a `100-Organizacion/03-Roles-Ejecutivos.md`:

* No participa en decisiones técnicas de implementación salvo impacto estratégico.
* No puede aprobar gasto de infraestructura sin que el CTO haya evaluado la opción técnica correspondiente (evita decisiones de negocio desconectadas de la realidad técnica).

---

# 4. Relación con los Agentes IA

El CEO es responsable de:

* Definir qué preguntas de mercado o negocio se delegan al Agente Investigación / rol "CEO IA" descrito en `prompts/MASTER_CONTEXT_PROMPT.md`.
* Revisar y aprobar (nunca delegar la aprobación final) cualquier análisis de mercado, pricing o estrategia producido por un agente IA, conforme a DEC-003 (control humano sobre decisiones estratégicas).

---

# 5. Entregables del CEO por Fase

Al cierre de cada fase del roadmap, el CEO debe dejar actualizado:

* `memory/CURRENT_STATE.md` (sección de negocio, si aplica).
* Los criterios de éxito de la fase siguiente en `03-Criterios-de-Exito-Fase0.md` (o el documento equivalente de la fase en curso).

---

# Resumen Ejecutivo para IA

El CEO decide directamente sobre prioridades comerciales y aprueba/rechaza propuestas técnicas con impacto estratégico; documenta cualquier cambio de modelo de negocio o de fases del roadmap; no toma decisiones técnicas de implementación. Ningún agente IA aprueba de forma final una decisión estratégica.
