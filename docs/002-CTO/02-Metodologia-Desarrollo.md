# 02-Metodologia-Desarrollo.md

---

title: Metodología de Desarrollo de Merchly AI
document: 002-02
version: 1.0.0
status: Draft
owner: CTO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* 01-Rol-Tecnico-Operativo.md
* ../000-Constitucion/08-Normas-de-Ingenieria.md
* ../001-Arquitectura/01-Arquitectura-General.md

---

# Metodología de Desarrollo

## Propósito

Definir cómo se planifica, ejecuta y cierra el trabajo técnico en Merchly AI, de forma aplicable tanto a colaboradores humanos como a agentes IA.

---

# 1. Enfoque General

Merchly AI adopta un enfoque **iterativo por fases documentales**, no un sprint tradicional de duración fija.

Cada fase corresponde a un volumen o subconjunto de `docs/` (ej. 002-CTO, luego 004-Backend), y se cierra solo cuando cumple el criterio de finalización de `000-Constitucion/08-Normas-de-Ingenieria.md`, sección 19.

Motivo: en esta etapa del proyecto (Fundación), el ritmo lo marca la calidad de la documentación y arquitectura, no un calendario fijo.

---

# 2. Ciclo de Trabajo por Tarea

Toda tarea técnica, sea ejecutada por un humano o por un agente IA, sigue este ciclo:

```text
1. Especificación   → objetivo, alcance, criterios de aceptación
2. Diseño            → decisión técnica documentada si aplica
3. Implementación    → código o documento
4. Verificación      → pruebas, revisión, checklist de la Constitución
5. Documentación      → actualización de docs/ y memory/
6. Registro           → commit + actualización de memory/CURRENT_STATE.md
```

Este ciclo es una instancia concreta del flujo general definido en `MERCHLY_AI_ROOT.md`, sección 13 (Flujo Oficial de Trabajo).

---

# 3. Definición de "Listo para Empezar"

Una tarea no debe comenzar si falta alguno de estos elementos:

* Objetivo claro en una sola frase.
* Documento relacionado identificado (a qué volumen pertenece).
* Criterios de aceptación explícitos.
* Impacto identificado sobre otros módulos.

---

# 4. Definición de "Terminado"

Se reutiliza íntegramente el checklist de `000-Constitucion/08-Normas-de-Ingenieria.md` §19. Ningún volumen o módulo se marca como `Completado` en `memory/CURRENT_STATE.md` sin cumplirlo.

---

# 5. Rol de la IA en el Ciclo

* Los agentes IA pueden ejecutar las fases 2 a 5 bajo supervisión.
* La fase 1 (especificación) y la aprobación final de la fase 6 son responsabilidad humana, salvo delegación explícita del CTO documentada en `memory/DECISIONS.md`.

---

# 6. Gestión de Prioridades

El orden de trabajo sigue el Roadmap General (`README.md`) y el detalle de `ROADMAP.md`. Cambios de prioridad dentro de una fase ya iniciada son decisión directa del CTO (ver `01-Rol-Tecnico-Operativo.md`, sección 1); cambios que alteren el orden de fases requieren registro en `memory/DECISIONS.md`.

---

# Resumen Ejecutivo para IA

Toda tarea sigue el ciclo Especificación → Diseño → Implementación → Verificación → Documentación → Registro. Ninguna tarea se considera terminada sin cumplir el checklist constitucional. El avance se mide por fases documentales, no por tiempo fijo.
