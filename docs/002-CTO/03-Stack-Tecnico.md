# 03-Stack-Tecnico.md

---

title: Stack Técnico Definitivo de Merchly AI
document: 002-03
version: 1.0.0
status: Draft
owner: CTO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* ../001-Arquitectura/05-Arquitectura-Tecnologica.md
* ../000-Constitucion/08-Normas-de-Ingenieria.md

---

# Stack Técnico Definitivo

## Propósito

Fijar el stack tecnológico definitivo de la Fase 0 (Fundación), heredado de `README.md` y de `001-Arquitectura/05-Arquitectura-Tecnologica.md`, con justificación explícita para que cualquier cambio futuro sea una decisión consciente y no una deriva.

Este documento no reabre la elección de arquitectura general; la asume como dada y la aterriza en versiones y herramientas concretas.

---

# 1. Backend

| Componente | Elección | Justificación |
|---|---|---|
| Lenguaje | Python 3.12+ | Ecosistema maduro para IA/automatización; coherente con agentes IA. |
| Framework | FastAPI | Tipado, rendimiento asíncrono, documentación OpenAPI automática. |
| Validación | Pydantic v2 | Integración nativa con FastAPI, contratos de datos claros. |
| Tareas asíncronas | Celery o alternativa nativa async de FastAPI (a definir en implementación) | Necesario para automatización y agentes de larga duración. |

**Alternativas descartadas:** Node.js/Express (menor afinidad con el ecosistema de IA/ML que se usará en `agents/`), Django (más pesado de lo necesario para una arquitectura de microservicios/agentes).

---

# 2. Frontend

| Componente | Elección | Justificación |
|---|---|---|
| Framework | Next.js | SSR/SSG, buen soporte de rendimiento y SEO para tiendas. |
| Librería UI | React | Estándar de facto, gran disponibilidad de componentes. |
| Lenguaje | TypeScript | Tipado obligatorio por Norma 6 de `08-Normas-de-Ingenieria.md`. |

---

# 3. Datos

| Componente | Elección | Justificación |
|---|---|---|
| Base relacional | PostgreSQL | Robustez, extensibilidad, estándar de la industria. |
| Extensión vectorial | pgvector | Permite búsqueda semántica sin sumar un motor de datos adicional. |
| Caché / colas | Redis | Caché, sesiones y backend de colas de tareas. |

---

# 4. Infraestructura

| Componente | Elección | Justificación |
|---|---|---|
| Contenedores | Docker | Portabilidad y paridad dev/producción. |
| Sistema base | Ubuntu LTS | Estabilidad y soporte extendido. |
| CI/CD | GitHub Actions | Integrado con el repositorio, sin infraestructura adicional. |
| Automatización de procesos de negocio | n8n | Bajo código, permite iterar automatizaciones sin desarrollo dedicado en fases tempranas. |

---

# 5. Agentes IA

Definido por rol y no por proveedor, conforme a DEC-007. La capa de agentes se implementará sobre el backend Python, con acceso a los proveedores de IA listados en `README.md` (ChatGPT, Claude, Gemini, Perplexity) mediante integraciones intercambiables.

---

# 6. Criterio para Cambiar el Stack

Un componente del stack solo se sustituye si:

* Existe un problema real y medido (no hipotético), conforme a Norma 16 de `08-Normas-de-Ingenieria.md`.
* La alternativa se documenta en `memory/DECISIONS.md` con motivo y fecha.
* Se actualiza este documento y `001-Arquitectura/05-Arquitectura-Tecnologica.md`.

---

# Resumen Ejecutivo para IA

Stack de Fase 0: Python + FastAPI (backend), Next.js + React + TypeScript (frontend), PostgreSQL + pgvector + Redis (datos), Docker + GitHub Actions + Ubuntu (infraestructura), n8n (automatización). Ningún componente se cambia sin registrar la decisión.
