# 01-Convenciones-de-Prompts.md

---

title: Convenciones de Prompts
document: 010-01
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-07-27
next_review: 2027-01-27
related:

* ../007-Agentes/01-Contrato-Tecnico-Estandar.md
* ../000-Constitucion/09-Uso-de-IA.md
* ../002-CTO/03-Stack-Tecnologico.md

---

# Convenciones de Prompts

## Propósito

Fijar la estructura, el idioma, el versionado y la forma de probar cualquier prompt antes de ponerlo en producción, para que cada agente nuevo no reinvente sus propias reglas.

---

# 1. Estructura Obligatoria de un Prompt

Todo documento de prompt en este volumen tiene, como mínimo, estas secciones:

1. **Rol y contexto:** quién es el agente, qué hace la empresa, qué tono usa.
2. **Tarea:** instrucción concreta de qué debe producir, en función de las entradas del contrato técnico (`007-Agentes`).
3. **Restricciones:** qué el modelo no debe hacer (alineado con la sección 7, "Límites Explícitos", del contrato del agente correspondiente).
4. **Formato de salida:** el esquema exacto esperado — siempre que el proveedor lo soporte, se usa salida estructurada nativa (JSON Schema / `response_schema`), no se le pide al modelo que "devuelva JSON" en texto libre.
5. **Manejo de incertidumbre:** instrucción explícita de qué hacer cuando el modelo no tiene suficiente información (nunca inventar datos — coherente con la sección 8 del contrato del agente, "en vez de inventar productos").

---

# 2. Idioma

El prompt en sí (instrucciones al modelo) se escribe en español, coherente con DEC-004 (español como idioma oficial del proyecto). El contenido que el modelo genera dentro de los campos de salida (ej. `nombre_producto`) puede requerir términos del mercado objetivo (`mercado_objetivo` en el contrato) — el prompt debe instruir esto explícitamente cuando aplique, en vez de asumir que todo el contenido generado será en español.

---

# 3. Versionado

* Cada prompt tiene una versión semántica propia, independiente de la versión del contrato técnico del agente.
* Un cambio de versión **patch** (1.0.0 → 1.0.1): ajustes de redacción que no cambian el comportamiento esperado.
* Un cambio de versión **minor** (1.0.0 → 1.1.0): se agrega una instrucción nueva o un caso de manejo de incertidumbre, sin romper el formato de salida.
* Un cambio de versión **major** (1.0.0 → 2.0.0): cambia el formato de salida esperado o la tarea central. Requiere actualizar también el modelo/schema en `backend/app/schemas/` si corresponde, y registrar el cambio en `memory/DECISIONS.md`.

---

# 4. Salida Estructurada, No Texto Libre

Siempre que el proveedor de IA lo soporte (Gemini lo soporta vía `response_schema`), el prompt se acompaña de un esquema de salida estructurada que el proveedor valida antes de devolver la respuesta. Esto evita:

* Tener que parsear texto libre con expresiones regulares o heurísticas frágiles.
* Que el modelo devuelva campos con nombres o tipos distintos a los del contrato técnico.

El código del proveedor (`backend/app/services/proveedores/`) es responsable de traducir el schema del contrato (`InvestigacionInput`/`ProductoCandidatoOutput` u homólogos) al formato de `response_schema` que la API del proveedor específico requiera.

---

# 5. Prueba Antes de Producción

Ningún prompt nuevo o modificado se activa en el proveedor real sin antes:

1. Probarse manualmente contra al menos 3 entradas representativas (una típica, una al límite de lo permitido, una que debería devolver "sin resultados" en vez de inventar datos).
2. Confirmar que la salida es JSON válido conforme al schema, sin intervención manual de parseo.
3. Confirmar que el modelo respeta las restricciones (sección 3 de este documento) — en particular, que no inventa evidencia cuando no la tiene.

Esta prueba no reemplaza los tests automatizados del código (`backend/app/tests/`), que verifican la lógica de orquestación con proveedores mockeados; es una verificación adicional específica del comportamiento del modelo real, que no puede automatizarse completamente por su naturaleza no determinística.

---

# 6. Relación con el Contrato Técnico del Agente

Un prompt nunca contradice el contrato técnico de su agente (`007-Agentes`). Si el prompt necesita pedirle al modelo algo que el contrato no contempla (ej. un campo de salida nuevo), se actualiza primero el contrato técnico y su schema en código, y solo después el prompt — nunca al revés.

---

# Resumen Ejecutivo para IA

Todo prompt documentado en este volumen sigue una estructura fija (rol, tarea, restricciones, formato de salida, manejo de incertidumbre), se escribe en español, usa salida estructurada nativa cuando el proveedor lo permite, se versiona semánticamente de forma independiente al contrato técnico del agente, y se prueba manualmente contra casos representativos antes de activarse en producción. El prompt nunca contradice el contrato técnico del agente al que pertenece.
