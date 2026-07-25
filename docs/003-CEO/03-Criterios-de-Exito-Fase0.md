# 03-Criterios-de-Exito-Fase0.md

---

title: Criterios de Éxito de la Fase 0 (Fundación)
document: 003-03
version: 1.0.0
status: Draft
owner: CEO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* README.md (raíz del proyecto)
* ../002-CTO/02-Metodologia-Desarrollo.md
* memory/CURRENT_STATE.md

---

# Criterios de Éxito de la Fase 0 (Fundación)

## Propósito

Definir, de forma verificable, cuándo la Fase 0 (Fundación) se considera cerrada y el proyecto puede avanzar a Fase 1 (Infraestructura), según el roadmap general descrito en `README.md`.

Este documento existe porque `ROADMAP.md` está actualmente vacío: mientras no se complete con fechas e hitos detallados, estos criterios son la referencia operativa de cierre de fase.

---

# 1. Criterios Documentales (condición necesaria)

☐ `docs/000-Constitucion` completo (✅ ya cumplido).

☐ `docs/001-Arquitectura` completo (✅ ya cumplido).

☐ `docs/100-Organizacion` completo (✅ ya cumplido).

☐ `docs/002-CTO` completo (✅ ya cumplido).

☐ `docs/003-CEO` completo (este volumen).

☐ `ROADMAP.md` completado con hitos y fechas estimadas por fase.

☐ Modelo de negocio decidido y registrado en `memory/DECISIONS.md` (ver `02-Modelo-de-Negocio.md`).

---

# 2. Criterios Técnicos (condición necesaria)

☐ `docker compose up -d` levanta un entorno local funcional, conforme al objetivo descrito en `002-CTO/06-Entorno-Desarrollo.md`.

☐ Existe al menos un endpoint de backend funcionando (`/health`).

☐ Existe al menos un agente IA definido con contrato técnico completo (entradas, salidas, límites), conforme al criterio que se establecerá en `docs/007-Agentes`.

---

# 3. Criterios de Negocio (condición necesaria)

☐ Decisión tomada sobre modelo de negocio (Opción A/B/C de `02-Modelo-de-Negocio.md`).

☐ Al menos una hipótesis de mercado inicial documentada en `04-Estrategia-Comercial-Preliminar.md`.

---

# 4. Lo que NO es criterio de cierre de Fase 0

Para evitar sobre-alcance (coherente con Norma 4, Simplicidad):

* No se requiere una tienda operando con ventas reales.
* No se requiere multi-tenancy ni soporte a terceros.
* No se requiere automatización de marketing/publicidad funcionando end-to-end.

Esos elementos corresponden a fases posteriores (Núcleo de Plataforma, Agentes IA, Motor de Marketing, según el roadmap general).

---

# 5. Proceso de Cierre de Fase

1. El CTO verifica los criterios técnicos y documentales.
2. El CEO verifica los criterios de negocio.
3. Ambos registran el cierre en `memory/CURRENT_STATE.md` y en `memory/DECISIONS.md`.
4. Se actualiza `ROADMAP.md` con la fecha real de cierre y se define el criterio de éxito de la siguiente fase.

---

# Resumen Ejecutivo para IA

La Fase 0 cierra cuando: (1) todos los volúmenes documentales base están completos, (2) existe un entorno técnico mínimo funcional con un agente IA con contrato definido, y (3) el CEO tomó y registró la decisión de modelo de negocio. No se exige aún producto en producción ni ventas.
