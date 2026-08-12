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
| Agente Investigador de Producto | Investigador IA | `03-Agente-Investigador-de-Producto.md` | 1.0.0 | Implementado (proveedor real Gemini + fallback simulado) |
| Agente de Analítica Básica | Analista IA | `05-Agente-Analitica-Basica.md` | 1.0.0 | Implementado (sin proveedor de IA — agregación pura sobre `productos_candidatos`) |

---

# Pendientes Conocidos

## Agente Investigador de Producto

* La integración real con Gemini (`ProveedorInvestigacionGemini`) fue verificada contra la API real (2026-08-03), además de los tests con cliente mockeado. Ya no hay pendiente de verificación.
* Mientras no haya `GEMINI_API_KEY` configurada en el entorno, el endpoint sigue usando `ProveedorInvestigacionSimulado` automáticamente (ver `backend/app/api/agentes.py`, `_obtener_proveedor`) — esto es comportamiento esperado, no una limitación pendiente.
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
* Marketing y publicidad.

(Analítica básica ya cuenta con contrato en diseño — ver tabla de registro arriba.)

Ninguno de estos agentes se implementa en `004-Backend` sin pasar primero por este mismo proceso de contrato.

---

# Resumen Ejecutivo para IA

Este documento es el índice de agentes con contrato técnico. Hay dos agentes registrados: el Agente Investigador de Producto, en etapa "Implementado" (proveedor real Gemini verificado + fallback simulado), y el Agente de Analítica Básica, en etapa "Implementado" (agregación pura en Python sobre `productos_candidatos`, sin proveedor de IA — es un agente de solo lectura, Nivel de permiso 0). Todo nuevo agente debe agregarse aquí al momento de redactar su contrato, y su etapa debe mantenerse sincronizada con el ciclo de vida definido en `02-Ciclo-de-Vida-de-Agentes.md`.
