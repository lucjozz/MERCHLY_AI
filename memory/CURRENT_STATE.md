# MERCHLY AI CURRENT STATE

Fecha:

2026-08-03


# Estado del Proyecto

Fase:

Infraestructura (Fase 1, cerrada); funcionalidad de agentes ya adelantada desde Fase 2-3


Versión:

0.9 Alpha


---

# Completado

## 000-Constitucion

Estado:

COMPLETADO


## 001-Arquitectura

Estado:

COMPLETADO


## 100-Organizacion

Estado:

COMPLETADO


## 002-CTO

Estado:

COMPLETADO (incluye docs/002-CTO/06-Entorno-Desarrollo.md actualizado con los comandos reales de levantamiento local y migraciones, ver DEC-023)


## 003-CEO

Estado:

COMPLETADO

Documentos:

✅ README (índice del volumen)

✅ Rol Operativo del CEO

✅ Modelo de Negocio (Opción C — Híbrido, aprobada, ver DEC-014)

✅ Criterios de Éxito de la Fase 0

✅ Estrategia Comercial Preliminar

✅ Métricas y Seguimiento


## 006-BaseDatos

Estado:

COMPLETADO

Convenciones de base de datos, esquema real de Fase 1 (tabla productos_candidatos), estrategia de migraciones (Alembic) y política de backups/retención. Implementado en código: modelo SQLAlchemy y primera migración. Ver DEC-019.


## 007-Agentes

Estado:

COMPLETADO

Contrato técnico estándar (10 secciones), ciclo de vida de agentes (8 etapas), y el Agente Investigador de Producto — implementado en código, con proveedor real (Gemini, verificado contra la API real) y fallback simulado. Ver DEC-017 a DEC-021 y DEC-023.


## 010-Prompts

Estado:

COMPLETADO Y VERIFICADO

Convenciones de prompts, el prompt real del Agente Investigador de Producto, y su registro. ProveedorInvestigacionGemini implementado con el SDK google-genai y salida estructurada nativa. Verificado contra la API real de Gemini: responde con datos reales y respeta el prompt (evidencia real, sin inventar productos). Ver DEC-021 y DEC-023.


## Entorno Técnico (Fase 0 y Fase 1)

Estado:

COMPLETADO

Backend FastAPI con /health (liveness) y /health/ready (readiness, verifica PostgreSQL y Redis). docker-compose.yml levanta backend + PostgreSQL/pgvector + Redis, con env_file apuntando correctamente a backend/.env (corregido en DEC-023 — antes apuntaba a .env.example, dejando cualquier secreto real, como GEMINI_API_KEY, sin efecto dentro del contenedor sin ningún error visible). Backend conectado realmente a PostgreSQL/pgvector (SQLAlchemy async + psycopg 3) y Redis (redis.asyncio). Modelo SQLAlchemy productos_candidatos + primera migración de Alembic. Las migraciones no corren automáticamente al levantar los contenedores (decisión deliberada); se aplican a mano con `docker compose exec backend alembic upgrade head`, según documentado en docs/002-CTO/06-Entorno-Desarrollo.md y README.md. Ver DEC-017, DEC-018, DEC-022, DEC-023.


## Agente Investigador de Producto (implementación)

Estado:

COMPLETADO Y VERIFICADO CONTRA LA API REAL

Schemas Pydantic, proveedor abstracto con dos implementaciones (ProveedorInvestigacionSimulado y ProveedorInvestigacionGemini, con selección automática según haya o no GEMINI_API_KEY configurada), orquestación completa (validación, reintentos, persistencia, salida) y endpoint POST /agentes/investigador-producto. 23 tests automatizados, todos en verde. El usuario verificó además el proveedor real contra la API de Gemini: responde con datos reales y respeta el prompt documentado (evidencia real, sin inventar productos). Sin pendientes conocidos. Ver DEC-020, DEC-021 y DEC-023.


---

# En progreso

Ninguno.


---

# Pendientes críticos identificados

Ninguno. Todos los criterios documentales y técnicos de cierre de Fase 0 y Fase 1 están cumplidos, y la integración con Gemini está verificada contra la API real.


---

# Próxima fase

Elegir el siguiente foco de trabajo (ver memory/NEXT_STEPS.md): especificar el siguiente agente (SEO, contenido, atención al cliente, analítica o marketing — ver docs/007-Agentes/04-Registro-de-Agentes.md), o documentar docs/004-Backend y docs/005-Frontend con lo ya construido antes de seguir agregando funcionalidad.


---

# Última acción realizada

Se verificó ProveedorInvestigacionGemini contra la API real de Gemini (confirmado: responde con datos reales, respeta el prompt, no inventa evidencia). Se corrigió docker-compose.yml (env_file apuntaba a .env.example en vez de .env, dejando GEMINI_API_KEY sin efecto en el contenedor sin ningún error visible) y se sincronizaron docs/007-Agentes/04-Registro-de-Agentes.md, docs/010-Prompts/03-Registro-de-Prompts.md, docs/002-CTO/06-Entorno-Desarrollo.md y README.md. Ver DEC-023. Se corrigieron además contradicciones internas que había quedado en este mismo archivo (fase marcada "en curso" en vez de "cerrada", sección 003-CEO con el modelo de negocio desactualizado, y la sección del agente todavía marcada con proveedor "provisional" pese a estar ya verificado) y se sincronizó la fecha de memory/CONTEXT.md.


---

# Próxima acción

Elegir entre: (a) especificar el siguiente agente (SEO, contenido, atención al cliente, analítica básica o marketing — ver docs/007-Agentes/04-Registro-de-Agentes.md), o (b) documentar docs/004-Backend y docs/005-Frontend con lo ya construido antes de seguir agregando funcionalidad. Ver memory/NEXT_STEPS.md.


---

# Bloqueos

Ninguno.
