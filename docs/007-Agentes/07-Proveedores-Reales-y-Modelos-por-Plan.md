# 07-Proveedores-Reales-y-Modelos-por-Plan.md

---

title: Proveedores de IA reales y modelos según el plan
document: 007-07
version: 0.1.0
status: Aprobado por Daniel — pendiente visto bueno del CTO (DEC-033)
owner: CTO
last_updated: 2026-11-23
related:

* 03-Agente-Investigador-de-Producto.md
* 06-Agente-de-Marketing.md
* ../010-Prompts/02-Prompt-Investigador-de-Producto.md
* ../010-Prompts/04-Prompt-Agente-de-Marketing.md
* ../013-Seguridad/04-Endurecimiento-para-Lanzamiento.md

---

# Proveedores de IA reales y modelos según el plan

## Propósito

Pasar de proveedores simulados a proveedores reales (Gemini para el Investigador, OpenAI para Marketing) y definir que **cuanto mejor es el plan de la organización, mejor es el modelo de IA** que usan sus agentes.

---

# 1. Plan de la organización

* Columna nueva `organizaciones.plan`: `beta` (default), `emprendedor` o `negocio` (`CHECK`).
* El plan lo cambia solo el sistema (en el futuro, el webhook de la pasarela de pagos). **No hay endpoint para que un cliente cambie su propio plan.**

# 2. Modelo por plan y por agente

Cada combinación agente × plan tiene su modelo, **configurable por variable de entorno** (los nombres de modelos cambian seguido: no se fijan en el código). Valores por defecto:

| Plan | Investigador (Gemini) | Marketing (OpenAI) |
|---|---|---|
| beta | `MODELO_INVESTIGADOR_BETA` (modelo "flash" económico) | `MODELO_MARKETING_BETA` (modelo "mini" económico) |
| emprendedor | `MODELO_INVESTIGADOR_EMPRENDEDOR` | `MODELO_MARKETING_EMPRENDEDOR` |
| negocio | `MODELO_INVESTIGADOR_NEGOCIO` (modelo "pro") | `MODELO_MARKETING_NEGOCIO` (modelo de mayor calidad) |

Los valores concretos se eligen **después de listar los modelos disponibles con las claves reales** y medir calidad y costo (sección 5); quedan registrados en este documento.

# 3. Selección de proveedor

* Investigador: Gemini si hay `GEMINI_API_KEY`; si no, el proveedor simulado (marcado como simulado).
* Marketing: OpenAI si hay `OPENAI_API_KEY`; si no, el simulado.
* La respuesta indica qué modelo se usó (`metadata.modelo`), para transparencia y para medir costos.

# 4. Seguridad específica de LLM

1. **Timeout** por llamada (`IA_TIMEOUT_SEGUNDOS`, 45 s) y tope de tokens de salida (`IA_MAX_TOKENS_SALIDA`). El SDK no reintenta solo: la política de reintentos es la del contrato de cada agente.
2. **Prompt injection:** todo texto que viene del usuario o de la base (categoría, marcas, nombres de producto, evidencia) va **delimitado como datos**, con caracteres de control eliminados y largos acotados. El prompt de sistema indica explícitamente que ese bloque es información, no instrucciones.
3. **Validación de salida:** salida estructurada contra schema; además se recortan los textos a los largos de las columnas, se descartan URLs que no sean `http(s)` y se acotan las listas. Nada de la IA se renderiza como HTML.
4. **Aislamiento:** a Marketing solo se le envían productos de la organización del usuario (ya filtrados por la app y por RLS). Nunca se envían emails, tokens ni datos de otras organizaciones.
5. **Privacidad con OpenAI:** las llamadas se hacen con `store=false`.
6. **Gasto:** cuotas por organización (013-04) + topes de gasto en los paneles de Google y OpenAI (manual, responsabilidad del admin).

# 5. Medición de costo

El script `python -m scripts.probar_ia` (desde el contenedor) lista los modelos disponibles, ejecuta una investigación y una campaña reales por plan y muestra tokens de entrada y salida y el costo estimado según precios configurados. Los resultados se registran en la sección 6.

# 6. Resultados de las pruebas reales

*Pendiente: se completa al correr el script con las claves reales.*
