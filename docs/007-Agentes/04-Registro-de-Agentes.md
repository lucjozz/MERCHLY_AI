# 04-Registro-de-Agentes.md

---

title: Registro de Agentes con Contrato Técnico
document: 007-04
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-07-26
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
| Agente Investigador de Producto | Investigador IA | `03-Agente-Investigador-de-Producto.md` | 1.0.0 | Implementado (con proveedor provisional simulado) |

---

# Pendientes Conocidos

## Agente Investigador de Producto

* El proveedor real de investigación (Gemini) todavía no está integrado. `backend/app/services/proveedores/simulado.py` devuelve resultados sintéticos, marcados explícitamente como tales en `riesgos_identificados`. **No usar en decisiones de negocio reales hasta reemplazarlo.**
* La lista de categorías prohibidas (`CATEGORIAS_PROHIBIDAS` en `backend/app/schemas/investigador_producto.py`) es provisional y corta; debe evolucionar junto con una política formal en `013-Seguridad` o un anexo de `000-Constitucion/03-Valores.md`.

---

# Reglas de Actualización

* Cada vez que un agente cambia de etapa (`02-Ciclo-de-Vida-de-Agentes.md`), se actualiza la columna "Etapa actual" en este registro.
* Cada vez que se aprueba un nuevo contrato de agente, se agrega una fila a esta tabla y se crea el documento correspondiente (`0X-Agente-[Nombre].md`) siguiendo el esquema de `01-Contrato-Tecnico-Estandar.md`.
* Un agente retirado no se elimina de la tabla; se marca como "Retirado" para conservar trazabilidad histórica.

---

# Próximos Agentes a Especificar

Conforme a `ROADMAP.md`, Fase 3 (Agentes IA), las siguientes áreas todavía no tienen contrato técnico y deberán especificarse antes de su implementación:

* SEO.
* Contenido.
* Atención al cliente (primer nivel).
* Analítica básica.
* Marketing y publicidad.

Ninguno de estos agentes se implementa en `004-Backend` sin pasar primero por este mismo proceso de contrato.

---

# Resumen Ejecutivo para IA

Este documento es el índice de agentes con contrato técnico completo. Actualmente hay un agente registrado: el Agente Investigador de Producto, en etapa "Contrato Aprobado". Todo nuevo agente debe agregarse aquí al momento de aprobar su contrato, y su etapa debe mantenerse sincronizada con el ciclo de vida definido en `02-Ciclo-de-Vida-de-Agentes.md`.
