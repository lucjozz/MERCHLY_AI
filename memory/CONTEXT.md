# MERCHLY AI CURRENT CONTEXT

## Proyecto

MERCHLY AI

AI Commerce Operating System (AICOS)

MERCHLY AI es la empresa. AICOS es el producto/plataforma que dicha empresa desarrolla.


## Documento principal

Toda IA o colaborador debe leer primero:

MERCHLY_AI_ROOT.md


Después:

docs/000-Constitucion

docs/001-Arquitectura

docs/100-Organizacion

docs/002-CTO

docs/003-CEO

docs/006-BaseDatos

docs/007-Agentes

docs/010-Prompts


---

# Estado actual

Versión:

0.9 Alpha


Estado:

Fundación e Infraestructura cerradas; primer agente implementado con integración real a Gemini (pendiente de verificación final contra la API real)


Fase:

FASE 1 - Infraestructura (cerrada); trabajo actual corresponde a funcionalidad adelantada de Fase 2-3


---

# Documentación completada

## 000-Constitucion

Estado:

Completado


## 001-Arquitectura

Estado:

Completado


## 100-Organizacion

Estado:

Completado


## 002-CTO

Estado:

Completado


## 003-CEO

Estado:

Completado (incluye decisión de modelo de negocio: Opción C — Híbrido, DEC-014)


## 006-BaseDatos

Estado:

Completado

Convenciones de base de datos, esquema real de Fase 1 (tabla productos_candidatos), estrategia de migraciones (Alembic) y política de backups/retención. Implementado en código: modelo SQLAlchemy y primera migración.


## 007-Agentes

Estado:

Completado

Contrato técnico estándar (10 secciones), ciclo de vida de agentes (8 etapas), y el Agente Investigador de Producto — implementado en código, con proveedor real (Gemini) y fallback simulado.


## 010-Prompts

Estado:

Completado

Convenciones de prompts, el prompt real del Agente Investigador de Producto, y su registro.


---

# Entorno técnico

Estado:

Completado (Fase 0 y Fase 1)


Contenido:

- Backend FastAPI con /health (liveness) y /health/ready (readiness, verifica PostgreSQL y Redis)
- docker-compose.yml: backend + PostgreSQL/pgvector + Redis
- Backend conectado realmente a PostgreSQL/pgvector (SQLAlchemy async + psycopg 3) y Redis (redis.asyncio)
- Modelo SQLAlchemy productos_candidatos + primera migración de Alembic (validada en modo offline)
- Agente Investigador de Producto implementado: validación, proveedor Gemini real + proveedor simulado (fallback automático), reintentos, persistencia, endpoint POST /agentes/investigador-producto
- 23 tests automatizados, todos en verde


---

# Trabajo actual

Verificación final del proveedor Gemini contra la API real de Google (con GEMINI_API_KEY válida). No se puede completar desde este entorno de ejecución (sin acceso de red a Google) — corresponde al usuario, en su máquina o en CI/CD.


---

# Próximas acciones

1.

El usuario verifica ProveedorInvestigacionGemini contra la API real de Gemini.


2.

Definir el siguiente agente a especificar (SEO, contenido, atención al cliente, analítica o marketing — ver docs/007-Agentes/04-Registro-de-Agentes.md, "Próximos Agentes a Especificar").


3.

Evaluar si conviene avanzar con docs/004-Backend y docs/005-Frontend (Fase 2 formal) o seguir profundizando agentes sobre la base ya construida.


---

# Decisiones recientes

Consultar:

memory/DECISIONS.md


---

# Última actualización

2026-07-30
