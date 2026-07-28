# MERCHLY AI CURRENT STATE

Fecha:

2026-07-26


# Estado del Proyecto

Fase:

Infraestructura (Fase 1, en curso)


Versión:

0.6 Alpha


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

Se conectó el backend realmente a PostgreSQL/pgvector y Redis (antes solo existían los contenedores en docker-compose.yml, sin uso real desde el código). Se agregó el endpoint /health/ready (readiness) separado de /health (liveness), con 3 tests nuevos y verificación manual. Ver DEC-018.


---

# Próxima acción

Implementar el Agente Investigador de Producto en código (backend/), sobre el contrato ya aprobado en docs/007-Agentes/03-Agente-Investigador-de-Producto.md, e iniciar docs/006-BaseDatos con el esquema mínimo para persistir sus resultados.


---

# Bloqueos

Ninguno.
