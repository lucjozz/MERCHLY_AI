# MERCHLY AI CURRENT CONTEXT

## Proyecto

MERCHLY AI

AI Commerce Operating System (AICOS)
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

0.5 Alpha


Estado:

Fundación cerrada


Fase:

FASE 1 - Infraestructura (recién iniciada)


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

Completado (criterios técnicos de cierre de Fase 0)


Contenido:

- Backend FastAPI mínimo (backend/) con endpoint /health, probado con pytest y solicitud HTTP real (200 OK)
- docker-compose.yml en la raíz: backend + PostgreSQL/pgvector + Redis


---

# Trabajo actual

Inicio de Fase 1 — Infraestructura.


Objetivo:

Conectar el backend realmente a PostgreSQL/pgvector y Redis, y comenzar la implementación del Agente Investigador de Producto sobre el contrato ya aprobado en docs/007-Agentes.


---

# Próximas acciones

1.

Conectar el backend a PostgreSQL/pgvector y Redis (más allá de que los contenedores existan en docker-compose.yml).


2.

Implementar el Agente Investigador de Producto en código, siguiendo su contrato técnico (docs/007-Agentes/03-Agente-Investigador-de-Producto.md).


3.

Iniciar docs/006-BaseDatos con el esquema mínimo necesario para el agente investigador.


---

# Decisiones recientes

Consultar:

memory/DECISIONS.md


---

# Última actualización

2026-07-26
