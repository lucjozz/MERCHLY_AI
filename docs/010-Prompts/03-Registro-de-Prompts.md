# 03-Registro-de-Prompts.md

---

title: Registro de Prompts en Uso
document: 010-03
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-07-27
next_review: 2027-01-27
related:

* 01-Convenciones-de-Prompts.md
* 02-Prompt-Investigador-de-Producto.md
* ../007-Agentes/04-Registro-de-Agentes.md

---

# Registro de Prompts en Uso

## Propósito

Mantener un catálogo vivo de qué prompt está activo por agente, en qué versión, y con qué proveedor de IA — el equivalente, para prompts, de lo que `007-Agentes/04-Registro-de-Agentes.md` es para contratos técnicos de agentes.

---

# Tabla de Registro

| Agente | Documento de prompt | Versión | Proveedor destino | Estado |
|---|---|---|---|---|
| Agente Investigador de Producto | `02-Prompt-Investigador-de-Producto.md` | 1.0.0 | Gemini (`ProveedorInvestigacionGemini`) | Activo en código (validado con cliente mockeado); pendiente verificación final contra la API real de Gemini. |

---

# Reglas de Actualización

* Cada vez que se documenta el prompt de un agente nuevo, se agrega una fila a esta tabla.
* Cuando un prompt cambia de versión (`01-Convenciones-de-Prompts.md`, sección 3), se actualiza la columna "Versión" aquí también.
* La columna "Estado" distingue entre: *Documentado* (existe el prompt pero el proveedor real que lo usa todavía no está integrado en código), *Activo* (el proveedor real ya lo usa en producción), y *Deprecado* (ya no se usa, se conserva por trazabilidad).

---

# Resumen Ejecutivo para IA

Este documento es el índice de prompts documentados. Hoy hay un solo prompt: el del Agente Investigador de Producto, en estado "Documentado" — existe el texto pero el proveedor real (Gemini) todavía no está implementado en código; el agente sigue operando con un proveedor simulado que no usa este prompt. Cuando se implemente `ProveedorInvestigacionGemini`, este registro debe actualizarse a "Activo".
