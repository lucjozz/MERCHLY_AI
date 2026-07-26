# Volumen 007 - Agentes

> **Versión:** 0.1 Alpha
> **Estado:** Activo
> **Propietario:** CTO
> **Última actualización:** 2026-07-26

---

## Propósito

Este volumen define el **contrato técnico** de los agentes IA de Merchly AI: la especificación concreta e implementable de entradas, salidas, herramientas, permisos, límites y manejo de errores que todo agente debe cumplir antes de ser construido.

Ya existen dos documentos relacionados que **no** duplica:

- `001-Arquitectura/03-Arquitectura-de-Agentes.md` responde **cómo está diseñado conceptualmente** el sistema de agentes (anatomía, categorías, memoria, comunicación, permisos como concepto).
- `100-Organizacion/06-Agentes-IA.md` responde **quién ocupa cada rol** y qué proveedor lo implementa hoy (catálogo organizacional).

`007-Agentes` responde una tercera pregunta, más concreta: **¿qué contrato técnico exacto debe cumplir un agente para poder implementarse en código?** Es el puente entre el diseño conceptual (001) y la implementación real en `004-Backend`.

---

## Objetivos

- Fijar un contrato técnico estándar, aplicable a cualquier agente presente o futuro.
- Definir el ciclo de vida de un agente (creación, prueba, despliegue, retiro), coherente con `002-CTO/02-Metodologia-Desarrollo.md`.
- Especificar el primer agente completo bajo este contrato, cumpliendo el criterio técnico de cierre de Fase 0 (`003-CEO/03-Criterios-de-Exito-Fase0.md`).
- Definir cómo se registran y versionan los contratos de agentes.

---

## Estructura

| Archivo | Descripción |
|---|---|
| 01-Contrato-Tecnico-Estandar.md | El esquema obligatorio que todo agente debe cumplir: entradas, salidas, herramientas, permisos, límites, errores. |
| 02-Ciclo-de-Vida-de-Agentes.md | Cómo nace, se prueba, se despliega y se retira un agente. |
| 03-Agente-Investigador-de-Producto.md | Primer agente especificado íntegramente bajo el contrato estándar (satisface el criterio técnico de Fase 0). |
| 04-Registro-de-Agentes.md | Catálogo vivo de agentes con contrato completo y su estado. |

---

## Relación con otros volúmenes

- `001-Arquitectura/03-Arquitectura-de-Agentes.md`: diseño conceptual que este volumen aterriza en un contrato implementable.
- `100-Organizacion/06-Agentes-IA.md`: catálogo de roles y proveedores; este volumen no reemplaza esa tabla, la referencia.
- `002-CTO/02-Metodologia-Desarrollo.md`: ciclo de trabajo técnico que aplica a la construcción de cada agente.
- `004-Backend`: implementación real de los agentes especificados aquí (aún no iniciado).
- `010-Prompts`: prompts concretos que usará cada agente (aún no iniciado); este volumen define el contrato, no el prompt en sí.

## Principio Rector

> **Ningún agente se implementa en código sin un contrato técnico completo y aprobado en este volumen. El contrato se escribe antes que el código, nunca después.**
