# MERCHLY AI CURRENT STATE

Fecha:

2026-07-26


# Estado del Proyecto

Fase:

Infraestructura (Fase 1, en curso)


Versión:

0.8 Alpha


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

Se implementó en código el Agente Investigador de Producto (adelantado desde Fase 2 a Fase 1): validación, proveedor simulado, orquestación con reintentos, persistencia y endpoint HTTP. 12 tests nuevos, 18 en total, todos en verde. Ver DEC-020.


---

# Próxima acción

Reemplazar el proveedor simulado del Agente Investigador de Producto por una integración real (Gemini, conforme a docs/100-Organizacion/06-Agentes-IA.md), o avanzar con el siguiente agente/volumen según prioridad de negocio.


---

# Bloqueos

Ninguno.
