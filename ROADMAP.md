# ROADMAP.md

---

title: Roadmap General de Merchly AI (AICOS)
document: ROADMAP
version: 1.0.0
status: Aprobado
owner: CEO & CTO
last_updated: 2026-07-26
next_review: 2027-01-26
related:

* README.md (raíz del proyecto)
* docs/000-Constitucion/05-Objetivos.md
* docs/003-CEO/03-Criterios-de-Exito-Fase0.md
* memory/CURRENT_STATE.md
* memory/DECISIONS.md
* memory/NEXT_STEPS.md

---

# Roadmap General de AICOS

## Propósito

Este documento traduce el roadmap general descrito en `README.md` (Fundación → Arquitectura → Infraestructura → Núcleo de Plataforma → Agentes IA → Automatización → Motor de Marketing → Analítica → Escalabilidad → Empresa Autónoma) en fases concretas, con volúmenes documentales asociados, criterios de cierre verificables y estimaciones de tiempo.

Conforme a `docs/003-CEO/03-Criterios-de-Exito-Fase0.md`, el cierre de cada fase se decide por **criterios verificables**, no únicamente por fecha calendario. Las fechas aquí son estimaciones de planificación, sujetas a ajuste; los criterios son la referencia real de avance.

---

# 1. Estado Actual

| Fase | Nombre | Estado |
|---|---|---|
| 0 | Fundación | En cierre (ver sección 2) |
| 1 | Infraestructura | No iniciada |
| 2 | Núcleo de Plataforma | No iniciada |
| 3 | Agentes IA | No iniciada |
| 4 | Automatización | No iniciada |
| 5 | Motor de Marketing | No iniciada |
| 6 | Analítica | No iniciada |
| 7 | Escalabilidad | No iniciada |
| 8 | Empresa Autónoma | No iniciada |

---

# 2. Fase 0 — Fundación (incluye Arquitectura documental)

**Objetivo:** establecer la base documental, organizacional y de decisión antes de escribir código (OBJ-001, OBJ-002).

**Volúmenes:** `000-Constitucion`, `001-Arquitectura`, `100-Organizacion`, `002-CTO`, `003-CEO`.

**Periodo real:** 2026-07-20 – 2026-07-26.

**Criterios de cierre** (detalle completo en `docs/003-CEO/03-Criterios-de-Exito-Fase0.md`):

* [x] `000-Constitucion` completo
* [x] `001-Arquitectura` completo
* [x] `100-Organizacion` completo
* [x] `002-CTO` completo
* [x] `003-CEO` completo, incluyendo decisión de modelo de negocio (Opción C — Híbrido, DEC-014)
* [x] `ROADMAP.md` completado (este documento)
* [x] `CHANGELOG.md` completado
* [ ] Entorno local mínimo funcional (`docker compose up -d`)
* [ ] Al menos un endpoint `/health` funcionando
* [x] Al menos un agente IA con contrato técnico completo (Agente Investigador de Producto, `docs/007-Agentes/03-Agente-Investigador-de-Producto.md`)

**Estado:** los criterios documentales están cumplidos. Faltan los criterios técnicos mínimos y `CHANGELOG.md` para declarar el cierre formal de Fase 0.

---

# 3. Fase 1 — Infraestructura

**Objetivo:** dejar un entorno técnico mínimo reproducible, sin todavía construir funcionalidad de negocio.

**Volúmenes:** `007-Agentes` (contrato técnico, no implementación completa), inicio de `004-Backend` y `006-BaseDatos`.

**Hitos:**

1. ~~Definir el contrato técnico de agentes IA (entradas, salidas, límites) en `docs/007-Agentes`.~~ Completado anticipadamente dentro de Fase 0 (ver `docs/007-Agentes`).
2. Levantar entorno local con Docker (`docker compose up -d`) conforme a `002-CTO/06-Entorno-Desarrollo.md`.
3. Primer endpoint de backend (`/health`) funcionando en FastAPI.
4. Base de datos PostgreSQL + pgvector conectada, sin esquema de negocio aún.

**Estimación:** 2–3 semanas desde el cierre de Fase 0.

**Criterio de cierre:** los 3 criterios técnicos pendientes de Fase 0 (Docker, `/health`, contrato de agente) quedan resueltos y versionados.

---

# 4. Fase 2 — Núcleo de Plataforma

**Objetivo:** primera versión funcional de AICOS operando una tienda propia (OBJ-003), coherente con Opción C del modelo de negocio.

**Volúmenes:** `004-Backend`, `005-Frontend`, `006-BaseDatos` completos; inicio de `012-Testing`.

**Hitos:**

1. Backend operativo con API principal.
2. Frontend funcional (Next.js) para operación básica.
3. Sistema de autenticación.
4. Al menos una tienda propia operando en entorno controlado (no producción con ventas reales todavía).

**Estimación:** 4–8 semanas desde el cierre de Fase 1.

---

# 5. Fase 3 — Agentes IA

**Objetivo:** implementar agentes especializados con responsabilidades claras (OBJ-004).

**Volúmenes:** `007-Agentes` (implementación completa), `010-Prompts`.

**Áreas iniciales:** investigación de productos, SEO, contenido, atención al cliente de primer nivel, analítica básica.

**Estimación:** 6–10 semanas desde el cierre de Fase 2, en paralelo parcial con Fase 4.

---

# 6. Fase 4 — Automatización

**Objetivo:** reducir progresivamente la intervención humana mediante flujos supervisados (OBJ-005).

**Volúmenes:** `008-Automatizacion` (n8n), `011-SOP`.

**Estimación:** en paralelo con Fase 3, consolidándose 2–4 semanas después.

---

# 7. Fase 5 — Motor de Marketing

**Objetivo:** automatizar marketing y publicidad sobre la base de agentes ya operativos.

**Volúmenes:** `009-Marketing`.

**Estimación:** a definir una vez cerradas Fases 3-4; depende de tracción real de la(s) tienda(s) propia(s).

---

# 8. Fase 6 — Analítica

**Objetivo:** métricas y seguimiento de negocio y plataforma a escala (OBJ-004, OBJ-005).

**Volúmenes:** `014-Analytics`.

**Estimación:** a definir; puede adelantarse parcialmente si hay necesidad temprana de métricas (ya existe una versión mínima en `003-CEO/05-Metricas-y-Seguimiento.md`).

---

# 9. Fase 7 — Escalabilidad

**Objetivo:** evaluar formalmente la apertura de AICOS como plataforma a terceros (Opción B), conforme a lo previsto en la Opción C del modelo de negocio (DEC-014). Esta fase **no se ejecuta automáticamente** — requiere nueva decisión explícita del CEO basada en tracción real.

**Volúmenes:** `013-Seguridad` (reforzada para multi-tenant), revisión de `006-BaseDatos` para soportar multi-tenancy si se aprueba.

**Estimación:** condicionada a resultados de Fases 2-6. Sin fecha objetivo mientras no exista la decisión.

---

# 10. Fase 8 — Empresa Autónoma

**Objetivo:** visión de largo plazo (OBJ-009 a OBJ-012) — sistema operativo empresarial con máxima automatización.

**Estimación:** 1–3+ años, sujeta a revisión continua conforme evoluciona el proyecto.

---

# 11. Principios de Planificación

* Ninguna fase avanza sin cerrar los criterios verificables de la fase anterior (coherente con DEC-003: control humano sobre decisiones estratégicas).
* Las estimaciones de tiempo son orientativas; los criterios de cierre son la referencia real de avance.
* La Fase 7 (Escalabilidad hacia terceros) es la única que depende de una decisión de negocio adicional, no solo de trabajo técnico completado.

---

# Resumen Ejecutivo para IA

El roadmap define 9 fases (0 a 8) desde Fundación hasta Empresa Autónoma. La Fase 0 está prácticamente cerrada (falta `CHANGELOG.md` y 3 criterios técnicos mínimos). Las Fases 1-6 construyen y operan AICOS sobre tiendas propias, conforme a la Opción C del modelo de negocio. La Fase 7 (apertura a terceros) requiere una decisión explícita adicional del CEO y no se asume por defecto. Toda fase se cierra por criterios verificables, no solo por fecha.
