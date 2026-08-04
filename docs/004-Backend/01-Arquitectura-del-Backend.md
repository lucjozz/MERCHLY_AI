# Volumen 004 - Backend

> **Versión:** 0.1 Alpha
> **Estado:** Activo
> **Propietario:** CTO
> **Última actualización:** 2026-08-04

---

## Propósito

Este volumen documenta el backend **tal como existe hoy en código** (`backend/`): su estructura de módulos, el ciclo de vida de una request, el catálogo real de endpoints, y el patrón reutilizable para agregar un agente nuevo.

A diferencia de `002-CTO`, que fija decisiones de stack y estándares aplicables a todo el proyecto, y de `007-Agentes`, que define contratos técnicos por agente, `004-Backend` responde una pregunta más concreta: **¿cómo está organizado el código que ya corre, y cómo se le agrega algo nuevo sin romper el patrón?**

Este volumen se escribió **después** del código (a diferencia de la disciplina habitual del proyecto), porque el backend avanzó más rápido de lo previsto al construir el primer agente de punta a punta. Se documenta ahora para no acumular más deuda antes de escalar a un segundo agente — ver `memory/DECISIONS.md`, DEC-025.

---

## Objetivos

- Dejar registrada la arquitectura real del backend, no la planeada.
- Servir de referencia rápida de los endpoints que existen hoy.
- Fijar el patrón paso a paso para agregar un agente nuevo, extraído de cómo se construyó el Agente Investigador de Producto — para que el segundo agente sea más rápido de construir que el primero.
- Documentar las convenciones de manejo de errores y configuración ya en uso, para que el código nuevo las siga sin tener que releer el código viejo para inferirlas.

---

## Estructura

| Archivo | Descripción |
|---|---|
| 01-Arquitectura-del-Backend.md | Estructura de módulos (`api`, `core`, `models`, `schemas`, `services`), y el recorrido completo de una request. |
| 02-Referencia-de-Endpoints.md | Catálogo real de endpoints HTTP: método, ruta, entrada, salida. |
| 03-Patron-para-Agregar-un-Agente-Nuevo.md | Los 6 pasos concretos, con archivos y nombres reales, para llevar un agente desde su contrato técnico hasta un endpoint funcionando. |
| 04-Manejo-de-Errores-y-Configuracion.md | Cómo se manejan errores hoy, y cómo se gestiona configuración/secretos vía `Settings`. |

---

## Relación con otros volúmenes

- `002-CTO/03-Stack-Tecnologico.md`: fija qué tecnologías se usan (FastAPI, SQLAlchemy, Alembic, etc.); este volumen no repite esa lista, la da por sentada y documenta cómo se usan en la práctica.
- `002-CTO/05-Estandares-Codigo.md`: fija la estructura de carpetas (`api/`, `core/`, `models/`, `services/`, `tests/`) como estándar; este volumen confirma que el código real la sigue y explica qué va en cada una.
- `006-BaseDatos`: el esquema de datos que los modelos en `backend/app/models/` implementan.
- `007-Agentes`: el contrato técnico que cada agente implementa; `03-Patron-para-Agregar-un-Agente-Nuevo.md` de este volumen es la guía operativa para pasar de un contrato aprobado a código funcionando.
- `010-Prompts`: los prompts que los proveedores de IA reales (ej. `ProveedorInvestigacionGemini`) usan.

## Principio Rector

> **Este documento describe el código, no al revés.** Si el código cambia de forma incompatible con lo escrito acá, se actualiza este volumen en el mismo cambio — no se deja para "después".
