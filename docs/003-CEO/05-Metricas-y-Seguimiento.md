# 05-Metricas-y-Seguimiento.md

---

title: Métricas y Seguimiento del Proyecto
document: 003-05
version: 1.0.0
status: Draft
owner: CEO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* 03-Criterios-de-Exito-Fase0.md
* ../014-Analytics (pendiente de completar)

---

# Métricas y Seguimiento del Proyecto

## Propósito

Definir qué se mide desde la Fase 0, aunque no exista producto en producción, para que `014-Analytics` (cuando se documente en detalle) herede una base ya en uso y no empiece de cero.

---

# 1. Métricas de Progreso Documental (ya trackeables hoy)

* Volúmenes de `docs/` completados vs. totales (20 volúmenes 000-020 + 100-Organizacion).
* Fecha de última actualización de `memory/CURRENT_STATE.md` (no debería quedar desactualizada por más de una fase de trabajo).

---

# 2. Métricas Técnicas (desde que exista código)

* Cobertura de pruebas del backend.
* Tiempo de respuesta del entorno local (`docker compose up -d` hasta servicio disponible).
* Costo mensual de uso de modelos de IA por proveedor (ChatGPT, Claude, Gemini, Perplexity), para controlar el supuesto de costo de `02-Modelo-de-Negocio.md`.

---

# 3. Métricas de Validación de Negocio (desde el piloto)

Conforme a `04-Estrategia-Comercial-Preliminar.md`:

* Demanda observada (búsquedas, consultas, señales de interés) para el nicho piloto.
* Viabilidad de al menos un proveedor integrado sin fricción.
* Margen estimado real vs. margen supuesto en la elección del nicho.

---

# 4. Frecuencia de Revisión

* Métricas documentales: al cierre de cada volumen.
* Métricas técnicas y de negocio: se definirá una cadencia formal (semanal/mensual) al iniciar el piloto, no antes, para no medir sin tener aún qué medir.

---

# Resumen Ejecutivo para IA

En Fase 0 se miden solo avance documental y, cuando exista código, costo de IA y disponibilidad técnica. Las métricas de negocio (demanda, margen) se activan recién con el piloto comercial, no antes.
