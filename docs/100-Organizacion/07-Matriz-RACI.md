---
title: Matriz RACI de Merchly AI
document: 100-07
version: 1.0.0
status: Approved
owner: CEO & CTO
last_updated: 2026-07-22
next_review: 2027-01-22
related:
  - 03-Roles-Ejecutivos.md
  - 04-Departamentos.md
  - 06-Agentes-IA.md
  - ../000-Constitucion/07-Gobernanza.md
---

# Matriz RACI de Merchly AI

## Propósito

Este documento define, mediante el modelo RACI, quién es Responsable, quién Aprueba, a quién se Consulta y a quién se Informa para cada tipo de decisión dentro de Merchly AI.

Complementa a `07-Gobernanza.md` (que define los niveles de decisión) y a `03-Roles-Ejecutivos.md` (que define la autoridad de cada rol), respondiendo la pregunta operativa: ante una decisión concreta, ¿qué hace cada rol?

---

# Cómo Leer esta Matriz

- **R — Responsable**: ejecuta o elabora el trabajo.
- **A — Aprueba**: autoridad final; solo puede haber un A por decisión.
- **C — Consultado**: su opinión se solicita antes de decidir.
- **I — Informado**: se le comunica la decisión una vez tomada.

Todo agente IA que participe en una fila de esta matriz actúa siempre como **R** (ejecuta o propone) nunca como **A** (aprueba), conforme al principio de control humano definido en `07-Gobernanza.md` y `09-Uso-de-IA.md`.

---

# RACI por Nivel de Decisión

Corresponde a los niveles definidos en `07-Gobernanza.md`.

| Tipo de decisión | CEO | CTO | CMO / COO / CFO | Agente IA correspondiente |
|---|---|---|---|---|
| Nivel 1 — Estratégico (visión, misión, modelo de negocio) | A | C | C | I |
| Nivel 2 — Táctico (selección tecnológica, priorización, procesos) | I | A (técnico) / C (resto) | R / A según área | C |
| Nivel 3 — Operativo (funcionalidades, documentación, testing) | I | A | R | R |
| Nivel 4 — Automatizado (reportes, clasificación, ejecución de flujos) | I | I | I | R |

---

# RACI por Departamento

## Backend / Frontend / Base de Datos / Infraestructura / DevOps / Testing / Arquitectura

| Actividad | CTO | Equipo técnico | Backend IA / Frontend IA / Arquitecto IA |
|---|---|---|---|
| Diseño de arquitectura | A | C | R |
| Implementación | I | A | R |
| Revisión de calidad | C | R | C |
| Documentación técnica | I | R | R |

## Marketing / SEO / Publicidad / Branding / Contenido / Redes Sociales

| Actividad | CMO | Equipo de marketing | Marketing IA / Analista IA |
|---|---|---|---|
| Estrategia de marketing | A | C | C |
| Ejecución de campañas | I | A | R |
| Investigación de mercado | C | I | R |
| Reportes de desempeño | I | I | R |

## Operaciones / SOP / Atención al Cliente / Automatizaciones

| Actividad | COO | Equipo operativo | Agentes de automatización |
|---|---|---|---|
| Diseño de procesos (SOP) | A | R | C |
| Automatización de tareas | C | A | R |
| Atención al cliente | I | A | R |

## Finanzas / Costos / Analytics / Cumplimiento

| Actividad | CFO | CEO | Analista IA |
|---|---|---|---|
| Presupuesto y planificación financiera | A | C | C |
| Control de costos | R | I | R |
| Reportes financieros | R | I | R |
| Cumplimiento normativo | A | I | C |

---

# Regla de Ambigüedad

Cuando una decisión no encaje claramente en una fila de esta matriz, se resolverá así:

1. Se identifica la Dirección Ejecutiva más cercana según `03-Roles-Ejecutivos.md`.
2. Esa Dirección asume el rol de **A**.
3. Los agentes IA relacionados asumen el rol de **R** o **C**, nunca **A**.
4. Si la decisión afecta a más de una Dirección, se aplica el criterio de coordinación definido en `04-Departamentos.md` ("Relación entre Departamentos").

---

# Actualización de la Matriz

Esta matriz deberá actualizarse cuando:

- Se cree un nuevo departamento o rol ejecutivo.
- Se incorpore un nuevo rol IA al catálogo (`06-Agentes-IA.md`).
- Cambie el nivel de autoridad de un rol existente.

Toda modificación deberá registrarse en `14-Historial.md`.

---

# Resumen Ejecutivo para IA

Antes de ejecutar una tarea, la IA debe ubicarse en esta matriz e identificar si su función es **R** o **C**.

Ningún agente IA puede actuar como **A**. Si una tarea requiere aprobación y no existe un responsable humano identificado, la IA debe detenerse y escalar la decisión conforme al flujo definido en `07-Gobernanza.md`.

---

# Fin del Documento
