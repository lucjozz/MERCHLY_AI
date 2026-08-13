# 04-Registro-de-Agentes.md

---

title: Registro de Agentes con Contrato Técnico
document: 007-04
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-08-11
next_review: 2027-01-26
related:

* 01-Contrato-Tecnico-Estandar.md
* 02-Ciclo-de-Vida-de-Agentes.md
* ../100-Organizacion/06-Agentes-IA.md

---

# Registro de Agentes con Contrato Técnico

## Propósito

Mantener un catálogo vivo y actualizado de todos los agentes que cuentan con contrato técnico bajo `007-Agentes`, su etapa actual en el ciclo de vida (`02-Ciclo-de-Vida-de-Agentes.md`) y el documento donde se especifica cada uno.

Este registro es el punto de entrada rápido; el detalle completo de cada agente vive en su propio documento de contrato.

---

# Tabla de Registro

| Agente | Rol organizacional (100-06) | Documento de contrato | Versión | Etapa actual |
|---|---|---|---|---|
| Agente Investigador de Producto | Investigador IA | `03-Agente-Investigador-de-Producto.md` | 1.0.0 | Implementado (proveedor real Gemini + fallback simulado) |
| Agente de Analítica Básica | Analista IA | `05-Agente-Analitica-Basica.md` | 1.0.0 | Implementado (sin proveedor de IA — agregación pura sobre `productos_candidatos`) |
| Agente de Marketing | Marketing IA | `06-Agente-de-Marketing.md` | 1.0.0 | Implementado (proveedor simulado; sin integración real con ChatGPT todavía) |

---

# Pendientes Conocidos

## Agente Investigador de Producto

* La integración real con Gemini (`ProveedorInvestigacionGemini`) fue verificada contra la API real (2026-08-03), además de los tests con cliente mockeado. Ya no hay pendiente de verificación.
* Mientras no haya `GEMINI_API_KEY` configurada en el entorno, el endpoint sigue usando `ProveedorInvestigacionSimulado` automáticamente (ver `backend/app/api/agentes.py`, `_obtener_proveedor`) — esto es comportamiento esperado, no una limitación pendiente.
* La lista de categorías prohibidas (`CATEGORIAS_PROHIBIDAS` en `backend/app/schemas/investigador_producto.py`) es provisional y corta; debe evolucionar junto con una política formal en `013-Seguridad` o un anexo de `000-Constitucion/03-Valores.md`.

## Agente de Marketing

* El proveedor real (ChatGPT, rol "Marketing IA") todavía no está integrado. `backend/app/services/proveedores/marketing_simulado.py` devuelve contenido sintético, marcado explícitamente como tal en `advertencias`. **No usar en campañas reales hasta reemplazarlo** — mismo criterio ya aplicado al Investigador de Producto antes de integrar Gemini.
* La distribución de presupuesto sugerida es un reparto uniforme entre canales (simplificación deliberada de v1); no pondera por canal ni por producto.

---

# Reglas de Actualización

* Cada vez que un agente cambia de etapa (`02-Ciclo-de-Vida-de-Agentes.md`), se actualiza la columna "Etapa actual" en este registro.
* Cada vez que se aprueba un nuevo contrato de agente, se agrega una fila a esta tabla y se crea el documento correspondiente (`0X-Agente-[Nombre].md`) siguiendo el esquema de `01-Contrato-Tecnico-Estandar.md`.
* Un agente retirado no se elimina de la tabla; se marca como "Retirado" para conservar trazabilidad histórica.

---

# Próximos Agentes a Especificar

Conforme a `ROADMAP.md`, Fase 3 (Agentes IA), las siguientes áreas todavía no tienen contrato técnico y deberán especificarse antes de su implementación:

* SEO.
* Atención al cliente (primer nivel).

Contenido quedó descartado como segundo agente (ver DEC-026/027) — retomarlo requiere una nueva decisión explícita y volver a redactar su contrato, que ya no está en el repo.

Ninguno de estos agentes se implementa en `004-Backend` sin pasar primero por este mismo proceso de contrato.

---

# Resumen Ejecutivo para IA

Este documento es el índice de agentes con contrato técnico. Hay tres agentes registrados: el Agente Investigador de Producto ("Implementado", proveedor real Gemini verificado + fallback simulado), el Agente de Analítica Básica ("Implementado", agregación pura en Python, sin proveedor de IA), y el Agente de Marketing ("Implementado", proveedor simulado — pendiente integrar ChatGPT real). Todo nuevo agente debe agregarse aquí al momento de redactar su contrato, y su etapa debe mantenerse sincronizada con el ciclo de vida definido en `02-Ciclo-de-Vida-de-Agentes.md`.
