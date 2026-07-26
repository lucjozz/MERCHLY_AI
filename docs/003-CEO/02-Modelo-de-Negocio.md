# 02-Modelo-de-Negocio.md

---

title: Modelo de Negocio Inicial de AICOS
document: 003-02
version: 1.0.0
status: Aprobado — Opción C (Híbrido) seleccionada por el CEO
owner: CEO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* ../000-Constitucion/01-Mision.md
* ../000-Constitucion/02-Vision.md
* README.md (raíz del proyecto)

---

# Modelo de Negocio Inicial de AICOS

## Propósito

Proponer un modelo de negocio inicial, coherente con la visión descrita en `README.md` ("plataforma reutilizable capaz de crear, administrar y escalar múltiples negocios digitales con mínima intervención humana"). Este documento es una **propuesta para decisión del CEO**, no una decisión ya tomada — a diferencia de los volúmenes 000/001/100/002 que documentan decisiones ya aprobadas.

---

# 1. Naturaleza del Negocio

AICOS puede monetizarse de dos formas no excluyentes, y conviene decidir cuál es la prioritaria en Fase 0:

## Opción A — Producto Interno (Merchly opera sus propias tiendas)

Merchly AI usa AICOS para operar sus propias tiendas de e-commerce, y AICOS es infraestructura interna, no un producto que se vende.

**A favor:** valida la plataforma con datos reales antes de venderla a terceros; menor complejidad de soporte/atención a clientes externos.
**En contra:** el crecimiento depende de cuánto pueda escalar el propio negocio de tiendas, no de vender licencias.

## Opción B — Plataforma como Producto (AICOS se licencia a terceros)

AICOS se convierte en un SaaS que otros operadores de e-commerce usan para automatizar sus propias tiendas.

**A favor:** modelo de ingresos recurrentes (SaaS), escalabilidad de negocio independiente del número de tiendas propias.
**En contra:** requiere multi-tenancy, soporte, seguridad reforzada y documentación orientada a terceros mucho antes en el roadmap.

## Opción C — Híbrido (recomendación por defecto)

Fase 0-1: AICOS opera exclusivamente tiendas propias (Opción A), sirviendo como banco de pruebas.
Fase 2+: si el modelo demuestra tracción, se evalúa abrir AICOS como plataforma (Opción B), reutilizando lo ya construido.

**Motivo de la recomendación:** es coherente con la Norma 4 de `000-Constitucion/08-Normas-de-Ingenieria.md` (Principio de Simplicidad) — no construir multi-tenancy antes de tener una sola tienda funcionando.

---

# 2. Fuentes de Valor (independiente del modelo elegido)

* Reducción de costo operativo por automatización de tareas repetitivas (investigación de producto, SEO, atención al cliente de primer nivel).
* Velocidad de lanzamiento de nuevas tiendas/productos frente a operación manual.
* Toma de decisiones asistida por datos y agentes de análisis, no reemplazo total del criterio humano (coherente con DEC-003).

---

# 3. Costos Iniciales a Considerar (Fase 0-1)

* Infraestructura (Docker/hosting, PostgreSQL, Redis) — bajo costo en Fase 0 al no haber tráfico real.
* Uso de modelos de IA (ChatGPT, Claude, Gemini, Perplexity) — costo variable por volumen de uso, debe monitorearse desde el inicio.
* Herramientas de automatización (n8n) — puede autoalojarse para minimizar costo recurrente.

---

# 4. Decisión Adoptada

El CEO aprueba la **Opción C (Híbrido)** como modelo de negocio de AICOS:

* **Fase 0-1:** AICOS opera exclusivamente tiendas propias de Merchly, sirviendo como banco de pruebas con datos reales.
* **Fase 2+:** si el modelo demuestra tracción, se evalúa abrir AICOS como plataforma a terceros (Opción B), reutilizando lo ya construido.

Esta decisión queda registrada en `memory/DECISIONS.md` (DEC-014, que sustituye el estado "pendiente" de DEC-012). Consecuencia directa para `004-Backend`: el sistema **no** necesita diseñarse multi-tenant desde el día uno; esa necesidad se evalúa recién al entrar en Fase 2, si corresponde.

---

# Resumen Ejecutivo para IA

Se evaluaron tres opciones de modelo de negocio (tiendas propias / SaaS a terceros / híbrido). El CEO aprobó la **Opción C (Híbrido)**: Fase 0-1 con tiendas propias como banco de pruebas, evaluando apertura a terceros recién en Fase 2+. `004-Backend` no requiere diseño multi-tenant desde el inicio.
