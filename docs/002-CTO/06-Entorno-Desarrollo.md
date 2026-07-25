# 06-Entorno-Desarrollo.md

---

title: Entorno de Desarrollo de Merchly AI
document: 002-06
version: 1.0.0
status: Draft
owner: CTO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* 03-Stack-Tecnico.md
* 04-Flujo-Git-CI.md

---

# Entorno de Desarrollo

## Propósito

Definir cómo se prepara un entorno de desarrollo válido para Merchly AI, de forma reproducible para cualquier colaborador o agente IA.

---

# 1. Requisitos Previos

* Git.
* Docker y Docker Compose.
* Python 3.12+ (para trabajo fuera de contenedor).
* Node.js LTS (para el frontend).
* Editor con soporte de linters del proyecto (ver `05-Estandares-Codigo.md`).

---

# 2. Estructura de Entornos

```text
local        → máquina del desarrollador, vía Docker Compose
staging      → réplica de producción para validación (a partir de Fase 2)
producción   → ambiente final (a partir de Fase 2/3)
```

En Fase 0 (actual) no existe aún staging ni producción; el trabajo es exclusivamente documental y de preparación.

---

# 3. Variables de Entorno

* Nunca se versiona un archivo `.env` con secretos reales (Norma 11, Seguridad por Diseño).
* Se mantiene un `.env.example` documentado por cada servicio, con valores ficticios.

---

# 4. Levantamiento Local (referencia objetivo)

Cuando exista código en `backend/` y `frontend/`, el flujo estándar será:

```bash
git clone <repo>
cd MERCHLY_AI
docker compose up -d
```

Este comando deberá levantar backend, frontend, PostgreSQL y Redis en un único paso. Su definición detallada (archivo `docker-compose.yml`) se documentará al iniciar `004-Backend`.

---

# 5. Codespaces / Entorno en la Nube

Se habilitará GitHub Codespaces como entorno alternativo, evitando fricción de configuración para nuevos colaboradores o para tareas ejecutadas por agentes IA con acceso al repositorio.

---

# 6. Checklist de Entorno Listo

☐ Docker Compose levanta todos los servicios sin errores.

☐ El backend responde en su endpoint de salud (`/health`).

☐ El frontend carga sin errores de consola.

☐ Las migraciones de base de datos corren limpias.

☐ Los linters y formateadores están configurados en el editor.

---

# Resumen Ejecutivo para IA

Entorno objetivo: Docker Compose como punto de entrada único (`docker compose up -d`), con Codespaces como alternativa en la nube. Ningún secreto real se versiona. Este documento se ampliará con instrucciones exactas al iniciar la implementación en `004-Backend`.
