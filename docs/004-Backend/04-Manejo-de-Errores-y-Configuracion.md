# 03-Patron-para-Agregar-un-Agente-Nuevo.md

---

title: Patrón para Agregar un Agente Nuevo
document: 004-03
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-08-04
next_review: 2027-02-04
related:

* 01-Arquitectura-del-Backend.md
* ../007-Agentes/01-Contrato-Tecnico-Estandar.md
* ../006-BaseDatos/01-Convenciones-de-Base-de-Datos.md
* ../010-Prompts/01-Convenciones-de-Prompts.md

---

# Patrón para Agregar un Agente Nuevo

## Propósito

Extraer, del proceso real que llevó al Agente Investigador de Producto de contrato aprobado a endpoint funcionando, una guía paso a paso reutilizable — para que el segundo agente (y los siguientes) se construyan más rápido, siguiendo exactamente el mismo patrón, sin tener que releer todo el código del primero para inferirlo.

---

# Los 6 Pasos

## Paso 1 — Contrato técnico (`007-Agentes`)

Antes de cualquier código: escribir el contrato técnico completo del agente, siguiendo `007-Agentes/01-Contrato-Tecnico-Estandar.md` (las 10 secciones obligatorias). Registrar el agente en `007-Agentes/04-Registro-de-Agentes.md` con etapa "Contrato Aprobado".

**No avanzar al paso 2 sin esto.** Es la disciplina central del proyecto.

## Paso 2 — Esquema de datos, si hace falta (`006-BaseDatos`)

Si el agente necesita persistir algo nuevo (no siempre es el caso — un agente de análisis podría no persistir nada propio):

1. Documentar la tabla nueva en `006-BaseDatos/02-Esquema-Fase1.md` (o el documento de esquema vigente), siguiendo `01-Convenciones-de-Base-de-Datos.md`.
2. Crear el modelo SQLAlchemy en `backend/app/models/`, heredando de `ConMarcaDeTiempo` y `Base` (`app/models/base.py`) para las convenciones de UUID/timestamps/borrado lógico.
3. Generar la migración de Alembic (`alembic revision --autogenerate -m "..."`) y revisarla a mano.

## Paso 3 — Schemas Pydantic (`backend/app/schemas/`)

Crear un archivo nuevo en `app/schemas/` que replique exactamente las secciones 2 ("Entradas") y 3 ("Salidas") del contrato técnico. Usar `field_validator` de Pydantic para las reglas de validación del contrato (no dejarlas para el código del endpoint o del servicio) — ver `app/schemas/investigador_producto.py` como referencia: validación de formato, rechazo de valores prohibidos, truncado de límites.

## Paso 4 — Proveedor (`backend/app/services/proveedores/`)

Si el agente usa un modelo de IA:

1. Verificar si `ProveedorInvestigacion` (o una interfaz nueva, si el contrato de entrada/salida es distinto) ya sirve como base, o definir una interfaz abstracta nueva en `app/services/proveedores/base.py` (o un archivo equivalente).
2. Escribir primero una implementación simulada (`*_simulado.py`) que devuelva resultados sintéticos claramente marcados como tales — permite construir y testear el resto del sistema sin depender de una API externa ni de credenciales.
3. Documentar el prompt real en `010-Prompts` (`01-Convenciones-de-Prompts.md` + un documento nuevo para este agente), **antes** de escribir el proveedor real.
4. Escribir la implementación real (`*_gemini.py` u otra), usando salida estructurada nativa cuando el proveedor lo soporte — ver `app/services/proveedores/gemini.py` como referencia de cómo convertir errores de red/API en `ProveedorInvestigacionError` (o la excepción de dominio equivalente).

## Paso 5 — Servicio de orquestación (`backend/app/services/`)

Un archivo nuevo en `app/services/` con una clase que:

* Reciba el proveedor y la sesión de base de datos por constructor (inyección explícita, no crear sus propias dependencias adentro).
* Implemente la política de reintentos de la sección 8 del contrato del agente.
* Persista resultados si corresponde, agrupándolos bajo un identificador compartido si el contrato lo requiere (ver `investigacion_id` en el agente investigador como ejemplo del patrón).
* Nunca ejecute acciones que el contrato reserve a un humano (ver sección 7 del contrato, "Límites Explícitos") — esto se verifica con un test explícito, no se asume.

## Paso 6 — Endpoint (`backend/app/api/`)

Un router nuevo (o una ruta nueva en un router existente si el dominio es afín) que:

* Reciba el schema de entrada como parámetro del cuerpo (FastAPI valida automáticamente).
* Resuelva sus dependencias vía `Depends` (sesión de BD, selección de proveedor).
* Instancie el servicio del paso 5 y devuelva su resultado.
* Se registre en `app/main.py` con `app.include_router(...)`.

---

# Checklist de Tests (aplica a todos los pasos anteriores)

Siguiendo el patrón de `backend/app/tests/`:

* [ ] Tests del schema: entrada válida, cada regla de validación rechazada individualmente.
* [ ] Tests del proveedor simulado: cantidad de resultados, respeto de exclusiones/filtros.
* [ ] Tests del proveedor real: con un cliente mockeado (nunca llamar a la API real desde tests automatizados) — verificar parseo de respuesta y conversión de errores.
* [ ] Tests del servicio de orquestación: con proveedor y sesión de BD mockeados — verificar persistencia, agrupación, manejo de fallas y reintentos.
* [ ] Tests del endpoint: con `app.dependency_overrides`, sin infraestructura real — verificar código de respuesta y estructura del cuerpo.

Ningún paso se da por completo sin sus tests correspondientes en verde.

---

# Qué NO Repetir del Primer Agente

Cosas que costó más de lo necesario en el Agente Investigador de Producto, y que el siguiente agente puede evitar:

* **El proveedor real se escribió después de tener todo lo demás funcionando con el simulado.** Es el orden correcto — no escribir el proveedor real primero "porque es lo más importante"; el simulado permite avanzar en paralelo sin bloquearse por credenciales o cuota de API.
* **El prompt se documentó en `010-Prompts` antes del código del proveedor real**, no después. Mantener ese orden evita que el prompt "viva" solo en el código.
* **La verificación contra la API real del proveedor no se pudo hacer en el entorno de desarrollo asistido por IA** (sin acceso de red al proveedor externo) — asumir desde el principio que ese paso final lo corre una persona, en un entorno con acceso real, y dejarlo explícito como pendiente hasta confirmarse (ver `007-Agentes/04-Registro-de-Agentes.md`, sección "Pendientes Conocidos", como ejemplo de cómo se documentó ese hueco mientras existió).

---

# Resumen Ejecutivo para IA

Agregar un agente nuevo sigue 6 pasos en orden: contrato técnico (007-Agentes) → esquema de datos si hace falta (006-BaseDatos + modelo SQLAlchemy + migración) → schemas Pydantic replicando el contrato → proveedor (simulado primero, documentar el prompt en 010-Prompts, después el proveedor real) → servicio de orquestación con reintentos y persistencia → endpoint que conecta todo vía FastAPI Depends. Cada paso tiene sus propios tests, con proveedores y sesiones de base de datos siempre mockeados — nunca se depende de infraestructura real ni de APIs externas en los tests automatizados.
