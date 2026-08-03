# MERCHLY AI CURRENT STATE

Fecha:

2026-08-03


# Estado del Proyecto

Fase:

Infraestructura (Fase 1, en curso)


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

COMPLETADO


## 007-Agentes

Estado:

COMPLETADO (contrato técnico estándar, ciclo de vida, primer agente con contrato completo: Agente Investigador de Producto)


## Entorno Técnico Mínimo (Fase 0)

Estado:

COMPLETADO

Backend FastAPI mínimo en backend/ con endpoint /health (probado con pytest y con solicitud HTTP real, responde 200). docker-compose.yml en la raíz levanta backend + PostgreSQL/pgvector + Redis. Ver DEC-017.


## Conexión Real a PostgreSQL y Redis (Fase 1)

Estado:

COMPLETADO

Backend conectado a PostgreSQL/pgvector (SQLAlchemy 2.0 async + psycopg 3) y Redis (redis.asyncio). Nuevo endpoint /health/ready que verifica ambas conexiones y responde "ok" o "degraded" sin caerse si alguna falla. 3 tests con dependencias mockeadas, más verificación manual sin infraestructura real (responde 200 "degraded" correctamente). Ver DEC-018. Todavía no hay esquema de negocio (tablas); eso corresponde a docs/006-BaseDatos.


## 006-BaseDatos

Estado:

COMPLETADO

Convenciones de base de datos, esquema real de Fase 1 (tabla productos_candidatos), estrategia de migraciones (Alembic) y política de backups/retención. Implementado en código: modelo SQLAlchemy y primera migración, validados sin necesitar una base PostgreSQL real conectada (DDL compilado + "alembic upgrade head --sql" en modo offline). Ver DEC-019.


## Agente Investigador de Producto (implementación)

Estado:

COMPLETADO (con proveedor provisional simulado)

Schemas Pydantic, proveedor abstracto + implementación simulada, orquestación completa (validación, reintentos, persistencia, salida) y endpoint POST /agentes/investigador-producto. 18 tests en total en el proyecto, todos en verde. Pendiente: reemplazar el proveedor simulado por una integración real con Gemini antes de usarlo en decisiones de negocio reales. Ver DEC-020.


## 010-Prompts + Integración Real con Gemini

Estado:

COMPLETADO Y VERIFICADO

docs/010-Prompts completo (convenciones, prompt del Agente Investigador de Producto, registro). ProveedorInvestigacionGemini implementado con el SDK google-genai y salida estructurada nativa. El endpoint POST /agentes/investigador-producto elige automáticamente entre Gemini real (si GEMINI_API_KEY está configurada) y el proveedor simulado (si no). 23 tests en total, todos en verde, usando un cliente de Gemini mockeado. El usuario verificó además el proveedor contra la API real de Gemini: responde con datos reales y respeta el prompt (evidencia real, sin inventar productos). Ver DEC-021 y DEC-023.


## 003-CEO

Estado:

COMPLETADO (incluye decisión de modelo de negocio ya aprobada: Opción C — Híbrido, ver DEC-014)


Documentos:

✅ README (índice del volumen)

✅ Rol Operativo del CEO

✅ Modelo de Negocio Inicial (propuesta A/B/C, pendiente de elección)

✅ Criterios de Éxito de la Fase 0

✅ Estrategia Comercial Preliminar

✅ Métricas y Seguimiento


---

# En progreso

Ninguno.


---

# Pendientes críticos identificados (no bloquean pero deben resolverse antes de cerrar Fase 0)

Ninguno. Todos los criterios documentales y técnicos de cierre de Fase 0 (docs/003-CEO/03-Criterios-de-Exito-Fase0.md) están cumplidos.


---

# Próxima fase

Fase 1 — Infraestructura, según ROADMAP.md: ampliar el backend con conexión real a PostgreSQL/Redis, y comenzar la implementación del primer agente (Investigador de Producto) sobre el contrato ya aprobado en docs/007-Agentes.


---

# Última acción realizada

Se verificó ProveedorInvestigacionGemini contra la API real de Gemini (confirmado: responde con datos reales, respeta el prompt, no inventa evidencia). Se corrigió docker-compose.yml (env_file apuntaba a .env.example en vez de .env, dejando GEMINI_API_KEY sin efecto en el contenedor sin ningún error visible) y se sincronizaron docs/007-Agentes/04-Registro-de-Agentes.md, docs/010-Prompts/03-Registro-de-Prompts.md, docs/002-CTO/06-Entorno-Desarrollo.md y README.md. Ver DEC-023.


---

# Próxima acción

Elegir entre: (a) especificar el siguiente agente (SEO, contenido, atención al cliente, analítica básica o marketing — ver docs/007-Agentes/04-Registro-de-Agentes.md), o (b) documentar docs/004-Backend con lo ya construido antes de seguir agregando funcionalidad. Ver memory/NEXT_STEPS.md.


---

# Bloqueos

Ninguno.
