# MERCHLY AI

## AI Commerce Operating System

> **El sistema operativo para empresas de comercio electrónico autónomas impulsadas por inteligencia artificial.**

---

# 🚀 Visión

MERCHLY AI (AI Commerce Operating System) es una plataforma abierta, modular y diseñada desde una perspectiva AI-Native para construir, operar y escalar negocios de comercio electrónico con el mayor nivel posible de automatización.

El objetivo a largo plazo no es crear una única tienda online.

El objetivo es desarrollar una plataforma reutilizable capaz de crear, administrar y escalar múltiples negocios digitales con mínima intervención humana.

Los humanos deben enfocarse en:

* Estrategia.
* Creatividad.
* Supervisión.
* Toma de decisiones importantes.

La Inteligencia Artificial debe ejecutar:

* Operaciones.
* Análisis.
* Automatización.
* Optimización continua.

---

# 🎯 Misión

Construir una plataforma orientada a ingeniería donde agentes de inteligencia artificial colaboren para automatizar:

* Investigación de productos.
* Gestión de proveedores.
* Administración de tiendas.
* SEO.
* Marketing.
* Publicidad.
* Analítica.
* Atención al cliente.
* Reportes empresariales.
* Soporte para toma de decisiones.

Manteniendo siempre:

* Modularidad.
* Extensibilidad.
* Independencia de proveedores.
* Eficiencia de costos.
* Mejora continua.

---

# 🏛 Principios Fundamentales

Toda decisión dentro de MERCHLY AI sigue estos principios:

1. Automatizar antes que contratar.
2. Documentar antes de programar.
3. Diseñar antes de implementar.
4. Construir componentes reutilizables.
5. Preferir arquitectura modular.
6. Minimizar costos operativos.
7. Medir todo.
8. Optimizar continuamente.
9. La IA asiste; los humanos toman decisiones estratégicas.
10. Todo módulo debe poder reemplazarse independientemente.

---

# 🧠 Filosofía del Proyecto

MERCHLY AI se desarrolla como una empresa tecnológica desde el primer día.

El repositorio no representa únicamente código.

Representa:

* Código.
* Arquitectura.
* Procesos.
* Documentación.
* Conocimiento acumulado.
* Historia del proyecto.

La documentación tiene la misma importancia que el software.

---

# 🗺 Roadmap General

```
Fundación
        ↓
Arquitectura
        ↓
Infraestructura
        ↓
Núcleo de Plataforma
        ↓
Agentes IA
        ↓
Automatización
        ↓
Motor de Marketing
        ↓
Analítica
        ↓
Escalabilidad
        ↓
Empresa Autónoma
```

---

# 📂 Estructura del Repositorio

```text
MERCHLY_AI/

.github/

docs/

memory/

prompts/

backend/

frontend/

agents/

automation/

infrastructure/

scripts/

tests/

tools/
```

---

# 📚 Sistema de Documentación

MERCHLY AI utiliza una arquitectura documental organizada por volúmenes.

| Carpeta            | Descripción                             |
| ------------------ | --------------------------------------- |
| 000-Constitucion   | Constitución del proyecto               |
| 001-Arquitectura   | Arquitectura global del sistema         |
| 002-CTO            | Manual técnico y dirección tecnológica  |
| 003-CEO            | Estrategia empresarial                  |
| 004-Backend        | Documentación backend                   |
| 005-Frontend       | Documentación frontend                  |
| 006-BaseDatos      | Diseño y gestión de datos               |
| 007-Agentes        | Arquitectura de agentes IA              |
| 008-Automatizacion | Flujos automáticos                      |
| 009-Marketing      | Sistema de marketing                    |
| 010-Prompts        | Biblioteca de prompts                   |
| 011-SOP            | Procedimientos operativos               |
| 012-Testing        | Control de calidad                      |
| 013-Seguridad      | Seguridad del sistema                   |
| 014-Analytics      | Métricas y análisis                     |
| 015-Bitacora       | Historial de desarrollo                 |
| 016-Decisiones     | Registros de decisiones arquitectónicas |
| 017-Roadmap        | Planificación oficial                   |
| 018-Research       | Investigación y experimentos            |
| 019-Templates      | Plantillas reutilizables                |
| 020-Assets         | Recursos visuales y materiales          |

La serie 000-020 documenta el **conocimiento** del proyecto (arquitectura, procesos, especificaciones).

| Carpeta            | Descripción                             |
| ------------------ | --------------------------------------- |
| 100-Organizacion   | Estructura organizacional, roles ejecutivos, departamentos y agentes IA |

La serie 100+ documenta la **organización** del proyecto (quién es responsable de cada capacidad). Responde una pregunta distinta a la serie 000-020 y por eso usa una numeración separada.

---

# 🧠 Sistema de Memoria del Proyecto

MERCHLY AI mantiene tres capas principales de información:

## Documentación oficial

Ubicación:

```
docs/
```

Contiene:

* Arquitectura.
* Procesos.
* Estándares.
* Especificaciones.

---

## Memoria operativa

Ubicación:

```
memory/
```

Contiene:

* Estado actual del proyecto.
* Próximos pasos.
* Decisiones recientes.
* Contexto operativo.

---

## Instrucciones para Inteligencia Artificial

Ubicación:

```
prompts/
```

Contiene:

* Roles IA.
* Instrucciones operativas.
* Contextos especializados.

---

# 🤖 Ecosistema de Inteligencia Artificial

Cada modelo de IA tiene una función especializada.

| IA         | Responsabilidad principal                                |
| ---------- | -------------------------------------------------------- |
| ChatGPT    | Arquitectura, ingeniería, planificación e implementación |
| Claude     | Documentación extensa, análisis y revisión               |
| Gemini     | Investigación y validación técnica                       |
| Perplexity | Investigación actualizada de mercado y tecnología        |

En futuras versiones se incorporarán nuevos proveedores de IA.

---

# 🛠 Stack Tecnológico Inicial

## Backend

* Python
* FastAPI

## Frontend

* Next.js
* React
* TypeScript

## Base de Datos

* PostgreSQL
* pgvector
* Redis

## Infraestructura

* Docker
* GitHub Actions
* Ubuntu

## Automatización

* n8n

---

# 🏁 Cómo Empezar

## Requisitos

* Git.
* Docker y Docker Compose.

## Levantamiento local

```bash
git clone <repo>
cd MERCHLY_AI
docker compose up -d
```

Esto levanta `backend` (FastAPI, puerto 8000), `db` (PostgreSQL + pgvector) y `redis`. El backend responde inmediatamente en `GET /health`.

Las migraciones de base de datos **no corren automáticamente** al levantar los contenedores (decisión deliberada, ver `docs/006-BaseDatos/03-Estrategia-de-Migraciones.md`). Después de levantar los servicios, aplicalas a mano:

```bash
docker compose exec backend alembic upgrade head
```

Sin este paso, `POST /agentes/investigador-producto` va a fallar al intentar persistir resultados, aunque `/health` responda bien.

Por defecto, sin `GEMINI_API_KEY` configurada, el agente usa `ProveedorInvestigacionSimulado` (resultados sintéticos, marcados como tales). Para variables de entorno reales, copiá `backend/.env.example` a `backend/.env` — nunca se versiona un `.env` con secretos reales (ver `docs/000-Constitucion/11-Seguridad.md`).

Instrucciones más detalladas del entorno de desarrollo: `docs/002-CTO/06-Entorno-Desarrollo.md`.

---

# 📊 Estado Actual

## Versión

```
1.0 Alpha
```

## Fase actual

```
Infraestructura (Fase 1, cerrada); funcionalidad de agentes ya adelantada desde Fase 2-3
```

## Estado de desarrollo

```
Backend funcionando: FastAPI + PostgreSQL/pgvector + Redis vía Docker
Compose, primer agente (Investigador de Producto) implementado y
verificado con proveedor real (Gemini). Backend documentado en
docs/004-Backend, incluyendo el patrón para agregar el próximo agente.
```

Ver `memory/CURRENT_STATE.md` para el detalle completo por área.

---

# 📚 Documentación Primero

Ningún código será considerado completo si no incluye:

* Documentación técnica.
* Pruebas.
* Criterios de aceptación.
* Notas arquitectónicas.
* Registro de cambios.

---

# 🤝 Flujo de Desarrollo

MERCHLY AI sigue un proceso de ingeniería estructurado:

```
Idea
    ↓
Especificación
    ↓
Arquitectura
    ↓
Diseño Técnico
    ↓
Implementación
    ↓
Pruebas
    ↓
Documentación
    ↓
Revisión
    ↓
Integración
```

---

# 📄 Licencia

La licencia será definida antes del primer lanzamiento público.

---

# 🌍 Visión a Largo Plazo

MERCHLY AI busca convertirse en un sistema operativo empresarial extensible capaz de coordinar negocios digitales autónomos mediante agentes especializados de inteligencia artificial.

Este repositorio representa la base tecnológica y documental de esa visión.

---

# Estado del Documento

Documento:

README.md

Versión:

1.1.0

Idioma:

Español

Última actualización:

2026-08-03
