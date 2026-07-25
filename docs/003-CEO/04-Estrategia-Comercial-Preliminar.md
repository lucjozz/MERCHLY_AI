# 04-Estrategia-Comercial-Preliminar.md

---

title: Estrategia Comercial Preliminar
document: 003-04
version: 1.0.0
status: Draft — pendiente de validación con datos reales
owner: CEO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* 02-Modelo-de-Negocio.md
* ../009-Marketing (pendiente de completar)

---

# Estrategia Comercial Preliminar

## Propósito

Dejar una hipótesis inicial de mercado por escrito, aunque todavía no exista producto, para que la Fase 1 (Infraestructura) y `004-Backend` se diseñen con un caso de uso concreto en mente y no en abstracto.

Este documento se revisará por completo una vez exista la primera tienda operando (ver `03-Criterios-de-Exito-Fase0.md`).

---

# 1. Segmento Inicial Recomendado

Se recomienda elegir **un solo nicho de producto** para la primera tienda piloto, en lugar de un catálogo generalista, por dos motivos:

* Reduce la superficie de trabajo del Agente Investigación y del Agente de Proveedores en su primera implementación real.
* Permite medir el modelo de negocio (`02-Modelo-de-Negocio.md`) con una variable menos (variedad de catálogo).

La elección concreta del nicho es una decisión de negocio pendiente del CEO; este documento no la prescribe.

---

# 2. Criterios para Elegir el Nicho Piloto

Al decidir, se recomienda evaluar:

* Disponibilidad de proveedores con API o integración automatizable (coherente con el objetivo de "gestión de proveedores" del README).
* Volumen de búsqueda estable, no estacional extremo, para simplificar la primera automatización de marketing.
* Márgenes que toleren el costo de automatización con IA en esta etapa (`02-Modelo-de-Negocio.md`, sección 3).

---

# 3. Validación Temprana

Antes de invertir en automatización completa, se recomienda validar manualmente:

1. Que existe demanda real (no solo teórica) para el nicho elegido.
2. Que al menos un proveedor puede integrarse sin fricción operativa excesiva.
3. Que el costo de adquisición de cliente estimado es compatible con el margen del producto.

Esta validación es manual y humana; los agentes IA se incorporan después de validar el nicho, no antes (evita automatizar un negocio que aún no se sabe si funciona).

---

# 4. Métricas de Validación Temprana

Ver `05-Metricas-y-Seguimiento.md` para las métricas específicas que se recomienda trackear desde el primer día del piloto.

---

# Resumen Ejecutivo para IA

La estrategia comercial recomienda un único nicho piloto (a decidir por el CEO), validado manualmente antes de automatizar, priorizando nichos con proveedores integrables, demanda estable y margen suficiente para sostener el costo de IA en esta fase.
