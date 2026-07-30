# Volumen 010 - Prompts

> **Versión:** 0.1 Alpha
> **Estado:** Activo
> **Propietario:** CTO
> **Última actualización:** 2026-07-27

---

## Propósito

Este volumen contiene los **prompts concretos** que instruyen a los modelos de IA detrás de cada agente. Es el último eslabón de la cadena que empieza en `001-Arquitectura/03-Arquitectura-de-Agentes.md` (diseño conceptual) y pasa por `007-Agentes` (contrato técnico: qué entra, qué sale, qué límites tiene). `010-Prompts` responde la pregunta que falta: **¿con qué instrucción exacta se le pide al modelo que haga su trabajo?**

Un contrato técnico completo (`007-Agentes`) no implica que el prompt ya exista — son artefactos distintos, con distinto ciclo de cambio. El contrato cambia poco (es una interfaz). El prompt puede iterarse muchas veces para mejorar resultados sin que el contrato se toque.

---

## Objetivos

- Fijar convenciones comunes de estructura, versionado y pruebas de prompts, para que cada agente nuevo no reinvente su propio formato.
- Documentar el prompt real de cada agente que ya tiene proveedor de IA integrado (no de los que siguen con proveedor simulado).
- Mantener un registro de qué prompt está en uso, en qué versión, y con qué agente/proveedor.

---

## Estructura

| Archivo | Descripción |
|---|---|
| 01-Convenciones-de-Prompts.md | Estructura obligatoria, idioma, versionado y forma de probar un prompt antes de ponerlo en producción. |
| 02-Prompt-Investigador-de-Producto.md | El prompt real usado por `ProveedorInvestigacionGemini` (ver `007-Agentes/03-...`). |
| 03-Registro-de-Prompts.md | Catálogo vivo de qué prompt está activo por agente. |

---

## Relación con otros volúmenes

- `007-Agentes`: el contrato técnico de cada agente fija su input/output; el prompt de este volumen es lo que traduce ese contrato en instrucciones para el modelo.
- `backend/app/services/proveedores/`: el proveedor real de cada agente (ej. `gemini.py`) carga el prompt documentado aquí — el texto del prompt no se hardcodea distinto en el código y en la documentación; el código lo importa desde un único lugar versionado.
- `002-CTO/03-Stack-Tecnologico.md`: fija qué proveedores de IA están disponibles (Anthropic Claude, Gemini, ChatGPT, Perplexity); este volumen no vuelve a discutir esa elección.

## Principio Rector

> **Ningún prompt vive únicamente en el código.** Todo prompt en producción tiene primero un documento en este volumen; el código lo referencia, no lo reemplaza.
