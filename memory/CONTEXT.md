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

docs/004-Backend


---

# Estado actual

Versión:

1.0 Alpha


Estado:

Fundación e Infraestructura cerradas; primer agente implementado con integración real a Gemini, verificada contra la API real (DEC-023); backend documentado en retrospectiva (docs/004-Backend, DEC-025)


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


## 004-Backend

Estado:

Completado

Arquitectura del backend, referencia de endpoints, patrón de 6 pasos para agregar un agente nuevo, y convenciones de manejo de errores/configuración. Documentado en retrospectiva sobre código ya existente.


---

# Entorno técnico

Estado:

Completado (Fase 0 y Fase 1)


Contenido:

- Backend FastAPI con /health (liveness) y /health/ready (readiness, verifica PostgreSQL y Redis)
- docker-compose.yml: backend + PostgreSQL/pgvector + Redis
- Backend conectado realmente a PostgreSQL/pgvector (SQLAlchemy async + psycopg 3) y Redis (redis.asyncio)
- Modelo SQLAlchemy productos_candidatos + primera migración de Alembic (aplicada realmente contra el Postgres de docker-compose, no solo en modo offline)
- Agente Investigador de Producto implementado: validación, proveedor Gemini real + proveedor simulado (fallback automático), reintentos, persistencia, endpoint POST /agentes/investigador-producto
- 23 tests automatizados, todos en verde


---

# Trabajo actual

Sin pendientes bloqueantes conocidos. docs/004-Backend completado, documentando el backend existente y el patrón para agregar el próximo agente (ver DEC-025).


---

# Próximas acciones

1.

Definir el siguiente agente a especificar (SEO, contenido, atención al cliente, analítica o marketing — ver docs/007-Agentes/04-Registro-de-Agentes.md), siguiendo el patrón de 6 pasos en docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md.


2.

Evaluar si conviene documentar también docs/005-Frontend antes de que exista código de frontend, o esperar a que el frontend empiece a construirse (a diferencia de 004-Backend, que se documentó después del código por necesidad, no por elección).


---

# Decisiones recientes

Consultar:

memory/DECISIONS.md


---

# Última actualización

2026-08-04
