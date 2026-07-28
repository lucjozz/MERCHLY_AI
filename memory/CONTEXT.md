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

docs/007-Agentes


---

# Estado actual

Versión:

0.6 Alpha


Estado:

Fundación cerrada; backend conectado a PostgreSQL/pgvector y Redis


Fase:

FASE 1 - Infraestructura (en curso)


---

# Documentación completada

## 000-Constitucion

Estado:

Completado


Contenido:

- Identidad
- Misión
- Visión
- Valores
- Principios (v2.0.0)
- Gobernanza (v2.0.0)
- Normas
- Uso de IA
- Estándares de Calidad
- Seguridad
- Escalabilidad
- Glosario
- Historial


---

## 001-Arquitectura

Estado:

Completado


Contenido:

- Arquitectura general
- Arquitectura sistema
- Arquitectura agentes
- Datos
- Tecnología
- Seguridad
- Automatización
- Escalabilidad


---

## 100-Organizacion

Estado:

Completado


Contenido:

- Organigrama
- Estructura Empresarial
- Roles Ejecutivos (CEO, CTO, CMO, COO, CFO)
- Departamentos
- Capacidades Organizacionales
- Agentes IA (catálogo de roles, independiente de proveedor)
- Matriz RACI


---

## 002-CTO

Estado:

Completado


Contenido:

- Rol técnico-operativo del CTO
- Metodología de desarrollo
- Stack técnico definitivo
- Flujo de Git y CI/CD
- Estándares de código
- Entorno de desarrollo


---

## 003-CEO

Estado:

Completado


Contenido:

- Rol operativo del CEO
- Modelo de negocio (Opción C — Híbrido, aprobado, ver DEC-014)
- Criterios de éxito de Fase 0
- Estrategia comercial preliminar
- Métricas y seguimiento


---

## 007-Agentes

Estado:

Completado


Contenido:

- Contrato técnico estándar de agentes IA (10 secciones)
- Ciclo de vida de agentes (8 etapas)
- Primer agente con contrato técnico completo: Agente Investigador de Producto
- Registro de agentes


---

# Entorno técnico

Estado:

Completado (criterios técnicos de cierre de Fase 0) + conexión real a dependencias (Fase 1)


Contenido:

- Backend FastAPI mínimo (backend/) con endpoint /health, probado con pytest y solicitud HTTP real (200 OK)
- docker-compose.yml en la raíz: backend + PostgreSQL/pgvector + Redis
- Backend conectado realmente a PostgreSQL/pgvector (SQLAlchemy async + psycopg 3) y Redis (redis.asyncio)
- Endpoint /health/ready (readiness) que verifica ambas conexiones


---

# Trabajo actual

Implementación del Agente Investigador de Producto en código, sobre el contrato ya aprobado en docs/007-Agentes.


Objetivo:

Tener el primer agente operando de punta a punta: entrada → investigación → salida persistida en base de datos.


---

# Próximas acciones

1.

Implementar el Agente Investigador de Producto en backend/, siguiendo su contrato técnico.


2.

Iniciar docs/006-BaseDatos con el esquema mínimo necesario para persistir sus resultados.


3.

Definir en docs/010-Prompts el prompt concreto que usará el agente (el contrato técnico ya existe; falta el prompt en sí).


---

# Decisiones recientes

Consultar:

memory/DECISIONS.md


---

# Última actualización

2026-07-27
