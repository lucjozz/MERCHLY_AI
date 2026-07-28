# MERCHLY AI NEXT STEPS


## Prioridad actual

Fase 1 — Infraestructura: dejar el backend conectado de verdad a PostgreSQL/pgvector y Redis, e implementar el primer agente en código.


---

# Próximas tareas


## 1

Conectar el backend a PostgreSQL/pgvector y Redis:

- El contenedor de base de datos y Redis ya existen en docker-compose.yml, pero backend/app/main.py todavía no ejecuta ninguna consulta ni usa esas conexiones.
- Agregar cliente de base de datos (SQLAlchemy o equivalente) y cliente de Redis en backend/app/core.


---

## 2

Implementar el Agente Investigador de Producto:

- Seguir estrictamente el contrato técnico ya aprobado en docs/007-Agentes/03-Agente-Investigador-de-Producto.md (entradas, salidas, herramientas permitidas, límites).
- Registrar el avance de etapa (Implementado, En Prueba) en docs/007-Agentes/04-Registro-de-Agentes.md, conforme al ciclo de vida definido en docs/007-Agentes/02-Ciclo-de-Vida-de-Agentes.md.


---

## 3

Iniciar docs/006-BaseDatos:

- Esquema mínimo necesario para persistir resultados del Agente Investigador de Producto (tabla de productos candidatos).
- Coherente con el stack ya definido (PostgreSQL + pgvector) en docs/002-CTO/03-Stack-Tecnico.md.


---

# Objetivo siguiente etapa

Con la Fase 0 (Fundación) cerrada —incluyendo Constitución, Arquitectura, Organización, CTO, CEO, Agentes y el entorno técnico mínimo— el proyecto pasa de "documentación y diseño" a "implementación real" en Fase 1. El primer entregable funcional debe ser el Agente Investigador de Producto operando de punta a punta: entrada → investigación → salida persistida en base de datos.
