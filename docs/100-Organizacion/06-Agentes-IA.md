---
title: Agentes IA de Merchly AI
document: 100-06
version: 1.0.0
status: Approved
owner: CTO
last_updated: 2026-07-22
next_review: 2027-01-22
related:
  - 01-Organigrama.md
  - 03-Roles-Ejecutivos.md
  - 04-Departamentos.md
  - ../000-Constitucion/09-Uso-de-IA.md
  - ../000-Constitucion/13-Glosario.md
  - ../../prompts/MASTER_CONTEXT_PROMPT.md
---

# Agentes IA de Merchly AI

## Propósito

Este documento define el catálogo oficial de roles de inteligencia artificial dentro de la organización de Merchly AI, y establece la separación entre **rol** (responsabilidad permanente) y **proveedor** (modelo que lo implementa en un momento dado).

Mientras `09-Uso-de-IA.md` (Constitución) define la política y las reglas de uso de inteligencia artificial, este documento define **quién ocupa cada rol dentro de la organización**, en línea con el propósito de `100-Organizacion/`.

---

# Principio Fundamental

> Merchly AI no se organiza alrededor de modelos de IA. Se organiza alrededor de roles. Los modelos son intercambiables; los roles son permanentes.

Consecuencias de este principio:

- Ningún proceso, documento o automatización debe nombrar directamente a un proveedor de IA como parte de su lógica.
- Un mismo rol puede migrar de proveedor sin que el resto de la organización se vea afectada.
- Un mismo proveedor puede cubrir más de un rol si su capacidad lo permite.
- La sustitución de un proveedor por otro debe registrarse como una decisión, no como un rediseño.

Este principio es una extensión directa del Principio 12 de la Constitución (Independencia Tecnológica).

---

# Catálogo de Roles IA

## Arquitecto IA

Propósito: diseño de sistemas, arquitectura técnica e integración entre componentes.

Reporta a: CTO.

Proveedor actual: ChatGPT.

## CTO IA

Propósito: apoyo en decisiones tecnológicas, desarrollo e infraestructura.

Reporta a: CTO.

Proveedor actual: ChatGPT.

## CEO IA

Propósito: apoyo en estrategia, análisis de negocio y mercado.

Reporta a: CEO.

Proveedor actual: ChatGPT.

## Investigador IA

Propósito: investigación, validación técnica y de mercado.

Reporta a: CEO / CTO según el tema.

Proveedor actual: Gemini.

## Revisor IA

Propósito: documentación extensa, auditoría y revisión de coherencia documental.

Reporta a: CTO.

Proveedor actual: Claude.

## Analista IA

Propósito: investigación actualizada de mercado, tecnología y tendencias.

Reporta a: CMO / CEO.

Proveedor actual: Perplexity.

## Marketing IA

Propósito: apoyo en investigación, publicidad y crecimiento.

Reporta a: CMO.

Proveedor actual: ChatGPT.

## Backend IA

Propósito: apoyo en APIs, servicios y lógica de negocio.

Reporta a: CTO (Departamento Backend).

Proveedor actual: ChatGPT.

## Frontend IA

Propósito: apoyo en interfaces y experiencia de usuario.

Reporta a: CTO (Departamento Frontend).

Proveedor actual: ChatGPT.

---

# Tabla de Mapeo Rol → Proveedor

| Rol IA | Proveedor actual | Responsable humano |
|---|---|---|
| Arquitecto IA | ChatGPT | CTO |
| CTO IA | ChatGPT | CTO |
| CEO IA | ChatGPT | CEO |
| Investigador IA | Gemini | CEO / CTO |
| Revisor IA | Claude | CTO |
| Analista IA | Perplexity | CMO / CEO |
| Marketing IA | ChatGPT | CMO |
| Backend IA | ChatGPT | CTO |
| Frontend IA | ChatGPT | CTO |

Esta tabla representa el estado actual del proveedor asignado a cada rol. No es una regla fija: puede actualizarse sin que el catálogo de roles cambie.

---

# Reglas de Sustitución de Proveedor

Cambiar el proveedor de un rol requiere:

1. Justificar el motivo (rendimiento, costo, seguridad, disponibilidad — ver `09-Uso-de-IA.md`).
2. Verificar que el nuevo proveedor cumple el propósito del rol.
3. Actualizar la tabla de mapeo en este documento.
4. Registrar el cambio en `14-Historial.md`.

El cambio de proveedor **no** requiere modificar el catálogo de roles, la Organización, ni la documentación técnica que depende de ese rol.

---

# Relación entre Roles y Departamentos

Cada rol IA opera dentro del ámbito de un departamento definido en `04-Departamentos.md`.

Un rol IA no puede ejecutar tareas fuera del ámbito del departamento al que apoya sin autorización del responsable ejecutivo correspondiente.

---

# Límites de los Agentes IA

Aplica lo establecido en `07-Gobernanza.md` y `09-Uso-de-IA.md`.

Los roles IA definidos en este documento:

- No poseen autoridad de decisión estratégica.
- No sustituyen a los roles ejecutivos definidos en `03-Roles-Ejecutivos.md`.
- Deben identificar su rol antes de ejecutar cualquier tarea, conforme a `prompts/MASTER_CONTEXT_PROMPT.md`.

---

# Escalabilidad del Catálogo

Se podrá agregar un nuevo rol IA cuando:

- Exista una capacidad organizacional sin cobertura (ver `05-Capacidades-Organizacionales.md`).
- El rol tenga un propósito distinto a los ya existentes.
- Se identifique un responsable humano y un departamento al que reporte.

La creación de un nuevo rol deberá registrarse en `14-Historial.md`.

---

# Resumen Ejecutivo para IA

Antes de actuar, toda IA involucrada en el proyecto debe identificar:

1. Qué rol de este catálogo está ocupando.
2. A qué departamento y responsable ejecutivo apoya.
3. Qué proveedor la implementa actualmente (referencia, no identidad).

El rol define el comportamiento esperado. El proveedor es un detalle de implementación reemplazable.

---

# Fin del Documento
