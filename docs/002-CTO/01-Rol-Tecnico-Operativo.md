# 01-Rol-Tecnico-Operativo.md

---

title: Rol Técnico-Operativo del CTO
document: 002-01
version: 1.0.0
status: Draft
owner: CTO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* ../100-Organizacion/03-Roles-Ejecutivos.md
* ../000-Constitucion/06-Roles.md
* ../000-Constitucion/07-Gobernanza.md

---

# Rol Técnico-Operativo del CTO

## Propósito

`100-Organizacion/03-Roles-Ejecutivos.md` define al CTO como autoridad ejecutiva. Este documento define su actuación en el día a día técnico: qué decide directamente, qué delega, y qué debe escalar.

---

# 1. Decisiones de Autoridad Directa

El CTO decide sin necesidad de aprobación adicional:

* Selección de librerías y herramientas dentro del stack ya aprobado (`03-Stack-Tecnico.md`).
* Estructura de carpetas y organización del código.
* Estándares de estilo y convenciones de código.
* Configuración de CI/CD y entornos de desarrollo.
* Asignación de agentes IA a tareas técnicas.
* Priorización técnica dentro de una fase ya aprobada.

---

# 2. Decisiones que Requieren Registro en DECISIONS.md

El CTO puede decidir, pero debe documentar la decisión y su justificación en `memory/DECISIONS.md`:

* Cambio de un componente del stack definitivo (ej. sustituir PostgreSQL).
* Introducción de una nueva dependencia externa crítica.
* Cambios en la arquitectura ya documentada en `001-Arquitectura`.
* Cambios en el flujo Git o en la política de ramas.

---

# 3. Decisiones que Requieren Aprobación del CEO

Conforme a `000-Constitucion/07-Gobernanza.md` y DEC-003:

* Adopción de infraestructura con costo recurrente significativo.
* Contratación de servicios de terceros con acceso a datos de negocio.
* Cambios que afecten el roadmap general (`ROADMAP.md`).
* Cualquier decisión con impacto estratégico, aunque su origen sea técnico.

---

# 4. Relación con los Agentes IA

El CTO es responsable de:

* Definir qué rol de agente IA (Arquitecto IA, Revisor IA, etc., según `100-Organizacion/06-Agentes-IA.md`) ejecuta cada tarea técnica.
* Revisar el trabajo producido por agentes IA antes de integrarlo, conforme a `000-Constitucion/08-Normas-de-Ingenieria.md`, norma 8.
* Mantener actualizados los prompts operativos en `prompts/`.

El CTO **no delega en un agente IA** la aprobación final de código que se integra al proyecto: esa responsabilidad es siempre humana.

---

# 5. Entregables del CTO por Fase

Al cierre de cada fase del roadmap, el CTO debe dejar actualizado:

* `memory/CURRENT_STATE.md`
* `memory/NEXT_STEPS.md`
* El historial correspondiente del volumen documental afectado.

---

# Resumen Ejecutivo para IA

El CTO decide directamente sobre implementación técnica dentro de lo ya aprobado; documenta cualquier desviación del stack o la arquitectura; y escala al CEO toda decisión con impacto estratégico o de costo recurrente. Ningún agente IA puede ejercer estas funciones de aprobación.
