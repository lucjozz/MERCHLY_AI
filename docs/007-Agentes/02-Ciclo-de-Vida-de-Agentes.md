# 02-Ciclo-de-Vida-de-Agentes.md

---

title: Ciclo de Vida de Agentes IA
document: 007-02
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-07-26
next_review: 2027-01-26
related:

* 01-Contrato-Tecnico-Estandar.md
* ../002-CTO/02-Metodologia-Desarrollo.md
* ../100-Organizacion/06-Agentes-IA.md

---

# Ciclo de Vida de Agentes IA

## Propósito

Definir las etapas por las que pasa un agente IA desde que se propone hasta que se retira, y quién es responsable de aprobar cada transición.

---

# 1. Etapas del Ciclo

```text
Propuesto
    ↓
Contrato en Diseño
    ↓
Contrato Aprobado
    ↓
Implementado (código)
    ↓
En Prueba (staging)
    ↓
Activo (producción)
    ↓
En Revisión / Deprecado
    ↓
Retirado
```

## 1.1 Propuesto

Cualquier persona identifica una necesidad no cubierta por los agentes existentes (ver `100-Organizacion/06-Agentes-IA.md`, sección "Escalabilidad del Catálogo"). Se registra como propuesta informal, sin contrato todavía.

## 1.2 Contrato en Diseño

Se redacta el contrato técnico completo siguiendo `01-Contrato-Tecnico-Estandar.md`. Puede ejecutarse en colaboración con un agente IA (ej. Arquitecto IA), pero la responsabilidad de aprobación es humana (CTO).

## 1.3 Contrato Aprobado

El CTO verifica que las 10 secciones del contrato están completas y coherentes con la arquitectura (`001-Arquitectura`) y la Constitución. Se documenta en `007-Agentes/0X-Agente-[Nombre].md` y se registra en `04-Registro-de-Agentes.md`.

## 1.4 Implementado

El agente se construye en código dentro de `004-Backend`, siguiendo el ciclo de trabajo técnico de `002-CTO/02-Metodologia-Desarrollo.md` (Especificación → Diseño → Implementación → Verificación → Documentación → Registro).

## 1.5 En Prueba

El agente se ejecuta en un entorno controlado (staging o equivalente local), con datos reales o representativos, sin afectar operación en vivo. Se valida contra las métricas definidas en la sección 2.9 del contrato.

## 1.6 Activo

El agente opera en producción, dentro de los límites y permisos definidos en su contrato. Toda ejecución se registra conforme a la sección 2.10 del contrato.

## 1.7 En Revisión / Deprecado

Un agente entra en revisión cuando: sus métricas caen por debajo del umbral aceptable, cambia el proveedor que lo implementa (ver reglas de sustitución en `100-Organizacion/06-Agentes-IA.md`), o su propósito queda cubierto por otro agente. Se marca como "Deprecado" mientras se decide su destino.

## 1.8 Retirado

El agente deja de ejecutarse. Se conserva su contrato y su historial de actividad con fines de auditoría, pero no se le asignan nuevas tareas.

---

# 2. Responsables por Etapa

| Etapa | Responsable de aprobar la transición |
|---|---|
| Propuesto → Contrato en Diseño | CTO |
| Contrato en Diseño → Contrato Aprobado | CTO |
| Contrato Aprobado → Implementado | CTO |
| Implementado → En Prueba | CTO |
| En Prueba → Activo | CTO (con validación de métricas) |
| Activo → En Revisión | CTO o responsable humano del agente (sección 2.1 del contrato) |
| En Revisión → Retirado | CTO |

Ningún agente puede aprobar su propia transición de etapa (coherente con DEC-008: los agentes IA nunca ocupan el rol de Aprobador).

---

# 3. Registro de Transiciones

Cada cambio de etapa de un agente con impacto relevante (Contrato Aprobado, Activo, Retirado) se refleja en `04-Registro-de-Agentes.md`. Cambios de etapa que impliquen una decisión estratégica (ej. retirar un agente que ya está en producción) se registran también en `memory/DECISIONS.md`.

---

# Resumen Ejecutivo para IA

Un agente IA pasa por 8 etapas: Propuesto, Contrato en Diseño, Contrato Aprobado, Implementado, En Prueba, Activo, En Revisión/Deprecado y Retirado. Toda transición relevante requiere aprobación humana del CTO; ningún agente puede auto-aprobar su propio avance de etapa.
