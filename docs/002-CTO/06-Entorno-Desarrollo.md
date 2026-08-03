# 06-Entorno-Desarrollo.md

---

title: Entorno de Desarrollo de Merchly AI
document: 002-06
version: 1.1.0
status: Draft
owner: CTO
last_updated: 2026-08-03
next_review: 2027-01-25
related:

* 03-Stack-Tecnico.md
* 04-Flujo-Git-CI.md
* 006-BaseDatos/03-Estrategia-de-Migraciones.md

---

# Entorno de Desarrollo

## Propósito

Definir cómo se prepara un entorno de desarrollo válido para Merchly AI, de forma reproducible para cualquier colaborador o agente IA.

---

# 1. Requisitos Previos

* Git.
* Docker y Docker Compose.
* Python 3.12+ (para trabajo fuera de contenedor).
* Node.js LTS (para el frontend, todavía no implementado).
* Editor con soporte de linters del proyecto (ver `05-Estandares-Codigo.md`).

---

# 2. Estructura de Entornos

```text
local        → máquina del desarrollador, vía Docker Compose
staging      → réplica de producción para validación (a partir de Fase 2)
producción   → ambiente final (a partir de Fase 2/3)
```

En Fase 1 (actual) solo existe el entorno local; no hay aún staging ni producción.

---

# 3. Variables de Entorno

* Nunca se versiona un archivo `.env` con secretos reales (Norma 11, Seguridad por Diseño). `backend/.env` está en `.gitignore`.
* `backend/.env.example` es la plantilla versionada, con valores ficticios o vacíos (ej. `GEMINI_API_KEY` vacío). Para overrides locales reales, copiá ese archivo a `backend/.env` y completá ahí los valores reales — nunca en `.env.example`.
* **Incidencia conocida:** `docker-compose.yml` define actualmente `env_file: ./backend/.env.example` para el servicio `backend`, en vez de `./backend/.env`. Mientras esto no se corrija, cualquier valor que pongas en `backend/.env` (por ejemplo `GEMINI_API_KEY`) **no llega al contenedor**: el backend va a seguir arrancando con `ProveedorInvestigacionSimulado` sin ningún error visible. Corregir esto es un prerequisito para poder probar `ProveedorInvestigacionGemini` localmente vía Docker Compose.

---

# 4. Levantamiento Local

```bash
git clone <repo>
cd MERCHLY_AI
docker compose up -d
```

Esto levanta tres servicios: `backend` (FastAPI, puerto 8000), `db` (PostgreSQL + pgvector, puerto 5432) y `redis` (puerto 6379). El servicio `frontend` todavía no existe en `docker-compose.yml`.

`docker compose up -d` **no aplica migraciones de base de datos**. Esto es intencional, no un paso pendiente de automatizar: conforme a `006-BaseDatos/03-Estrategia-de-Migraciones.md` (sección 4), las migraciones nunca se aplican automáticamente al arrancar la aplicación — un cambio de esquema fallido no debe impedir que el backend levante con el esquema anterior. Por eso, después de levantar los contenedores (y cada vez que bajes una migración nueva), hay que aplicarlas a mano:

```bash
docker compose exec backend alembic upgrade head
```

Sin este paso, `db` existe pero la tabla `productos_candidatos` no — `/health` va a responder igual (no depende del esquema), pero cualquier llamada a `POST /agentes/investigador-producto` va a fallar al intentar persistir resultados.

Para desarrollo fuera de contenedor (ej. correr tests con `pytest` directamente):

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head   # requiere DATABASE_URL apuntando a un Postgres accesible
```

---

# 5. Codespaces / Entorno en la Nube

Se habilitará GitHub Codespaces como entorno alternativo, evitando fricción de configuración para nuevos colaboradores o para tareas ejecutadas por agentes IA con acceso al repositorio. Pendiente de implementar.

---

# 6. Checklist de Entorno Listo

☐ `docker compose up -d` levanta `backend`, `db` y `redis` sin errores.

☐ `backend/.env` existe y sus valores efectivamente llegan al contenedor (ver incidencia de la sección 3).

☐ El backend responde en su endpoint de salud (`GET /health`).

☐ `docker compose exec backend alembic upgrade head` corre limpio y `GET /health/ready` reporta `database: "ok"` y `redis: "ok"`.

☐ `POST /agentes/investigador-producto` devuelve 200 con productos (simulados o reales, según haya `GEMINI_API_KEY` configurada).

☐ El frontend carga sin errores de consola. *(No aplica todavía — no existe frontend en el repo.)*

☐ Los linters y formateadores están configurados en el editor.

---

# Resumen Ejecutivo para IA

Entorno objetivo: Docker Compose como punto de entrada único (`docker compose up -d`), con Codespaces como alternativa en la nube (pendiente). Ningún secreto real se versiona: los valores reales van en `backend/.env`, nunca en `.env.example` — aunque hoy `docker-compose.yml` todavía no lee ese archivo (incidencia conocida, sección 3). Las migraciones nunca corren automáticamente al levantar el backend, por diseño (`006-BaseDatos/03-Estrategia-de-Migraciones.md`); siempre hay que aplicarlas a mano con `docker compose exec backend alembic upgrade head` antes de usar cualquier endpoint que toque la base de datos. Este documento se ampliará cuando exista `frontend/`.
