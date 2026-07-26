# 01-Contrato-Tecnico-Estandar.md

---

title: Contrato Técnico Estándar de Agentes IA
document: 007-01
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-07-26
next_review: 2027-01-26
related:

* ../001-Arquitectura/03-Arquitectura-de-Agentes.md
* ../100-Organizacion/06-Agentes-IA.md
* ../002-CTO/02-Metodologia-Desarrollo.md
* ../000-Constitucion/09-Uso-de-IA.md

---

# Contrato Técnico Estándar de Agentes IA

## Propósito

Definir el esquema obligatorio que debe cumplir la especificación de **cualquier** agente IA de Merchly AI antes de que se autorice su implementación en código. Este documento es la plantilla; cada agente concreto (ej. `03-Agente-Investigador-de-Producto.md`) es una instancia de esta plantilla.

Ningún agente pasa a `004-Backend` sin que las 10 secciones de este contrato estén completas.

---

# 1. Por qué un contrato técnico y no solo diseño conceptual

`001-Arquitectura/03-Arquitectura-de-Agentes.md` define la anatomía conceptual de un agente (identidad, cerebro, memoria, herramientas, acciones). Ese nivel es necesario pero insuficiente para escribir código: no especifica tipos de datos, formatos de error, ni límites verificables.

El contrato técnico traduce ese diseño conceptual a algo que un desarrollador (humano o agente IA bajo supervisión) puede implementar y testear directamente.

---

# 2. Esquema Obligatorio del Contrato

Todo agente debe documentarse con estas 10 secciones, en este orden:

## 2.1 Identidad

* Nombre del agente.
* Rol organizacional asociado (referencia a `100-Organizacion/06-Agentes-IA.md`).
* Versión del contrato (semver).
* Propósito en una sola frase.
* Responsable humano (persona o rol ejecutivo).

## 2.2 Entradas (Input Schema)

* Lista de campos de entrada, con nombre, tipo de dato y obligatoriedad.
* Origen de cada entrada (usuario, otro agente, sistema externo, base de datos).
* Validaciones mínimas antes de procesar (qué rechaza el agente antes de ejecutar nada).

## 2.3 Salidas (Output Schema)

* Lista de campos de salida, con nombre, tipo de dato y significado.
* Destino de la salida (respuesta directa, otro agente, base de datos, cola de tareas).
* Formato exacto (ej. JSON con esquema definido) — no texto libre sin estructura cuando la salida alimenta otro sistema.

## 2.4 Herramientas Permitidas

* Lista cerrada de herramientas, APIs o sistemas que el agente puede invocar.
* Cualquier herramienta no listada aquí está prohibida por defecto (allowlist, no denylist).

## 2.5 Memoria

* Qué tipo(s) de memoria usa, conforme a la clasificación de `001-Arquitectura/03-Arquitectura-de-Agentes.md` (temporal, operativa, histórica).
* Dónde persiste cada tipo (ej. `memory/`, base de datos, ninguna — memoria vacía si el agente es sin estado).

## 2.6 Permisos

* Nivel de permiso conforme a la escala de `001-Arquitectura/03-Arquitectura-de-Agentes.md` (0 a 4: solo lectura, análisis, ejecución autorizada, automatización supervisada, autonomía limitada).
* Justificación de por qué ese nivel y no uno mayor.

## 2.7 Límites Explícitos

* Qué el agente **no puede hacer** bajo ninguna circunstancia.
* Qué acciones requieren aprobación humana explícita antes de ejecutarse.
* Coherente con DEC-008: ningún agente ocupa el rol de Aprobador (A) en la Matriz RACI.

## 2.8 Manejo de Errores

* Qué ocurre si una herramienta falla.
* Política de reintentos (cuántos, con qué backoff).
* Condición de escalamiento a un humano cuando el agente no puede completar la tarea.

## 2.9 Métricas de Evaluación

* Precisión, velocidad, coste y seguridad, conforme a los criterios de `001-Arquitectura/03-Arquitectura-de-Agentes.md`.
* Umbral mínimo aceptable para cada métrica, si se conoce; si no, se declara "a definir tras primeras ejecuciones".

## 2.10 Registro de Actividad

* Qué se registra por cada ejecución (fecha, entrada, salida, resultado, duración, coste).
* Dónde se registra (mientras no exista base de datos operativa, en `memory/` o en logs de la aplicación).

---

# 3. Regla de Completitud

Un contrato se considera **completo** solo si las 10 secciones tienen contenido específico del agente, no una copia genérica de esta plantilla. Una sección marcada "a definir" en más de un punto bloquea la implementación de ese agente.

Este criterio de completitud es el que satisface el requisito técnico de cierre de Fase 0 (`003-CEO/03-Criterios-de-Exito-Fase0.md`, sección 2): *"Existe al menos un agente IA definido con contrato técnico completo (entradas, salidas, límites)"*.

---

# 4. Versionado del Contrato

* Cambios menores (aclaraciones, ejemplos adicionales) → incrementan versión patch (1.0.0 → 1.0.1).
* Cambios que agregan o quitan campos de entrada/salida → incrementan versión minor (1.0.0 → 1.1.0).
* Cambios que alteran el propósito, los permisos o los límites del agente → incrementan versión major (1.0.0 → 2.0.0) y requieren registro en `memory/DECISIONS.md`.

---

# 5. Relación con el Ciclo de Desarrollo

La redacción de este contrato corresponde a la fase 1 (Especificación) y parte de la fase 2 (Diseño) del ciclo definido en `002-CTO/02-Metodologia-Desarrollo.md`. Ningún agente entra a fase 3 (Implementación) sin contrato aprobado.

---

# Resumen Ejecutivo para IA

Todo agente IA de Merchly AI debe tener un contrato técnico con 10 secciones obligatorias: identidad, entradas, salidas, herramientas permitidas, memoria, permisos, límites explícitos, manejo de errores, métricas de evaluación y registro de actividad. Ninguna sección puede quedar genérica o sin definir antes de autorizar la implementación en código. Este contrato es el puente entre el diseño conceptual de `001-Arquitectura` y el código real en `004-Backend`.
