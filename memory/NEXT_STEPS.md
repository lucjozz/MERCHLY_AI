# MERCHLY AI NEXT STEPS


## Prioridad actual

Implementar el Agente Investigador de Producto en código, sobre el contrato técnico ya aprobado en docs/007-Agentes.


---

# Próximas tareas


## 1

Implementar el Agente Investigador de Producto:

- Seguir estrictamente el contrato técnico ya aprobado en docs/007-Agentes/03-Agente-Investigador-de-Producto.md (entradas, salidas, herramientas permitidas, límites).
- El backend ya está conectado a PostgreSQL/pgvector y Redis (ver DEC-018); falta el esquema de datos y la lógica del agente en sí.
- Registrar el avance de etapa (Implementado, En Prueba) en docs/007-Agentes/04-Registro-de-Agentes.md, conforme al ciclo de vida definido en docs/007-Agentes/02-Ciclo-de-Vida-de-Agentes.md.


---

## 2

Iniciar docs/006-BaseDatos:

- Esquema mínimo necesario para persistir resultados del Agente Investigador de Producto (tabla de productos candidatos).
- Coherente con el stack ya definido (PostgreSQL + pgvector) en docs/002-CTO/03-Stack-Tecnico.md.


---

## 3

Iniciar docs/010-Prompts:

- El contrato técnico del agente ya define entradas/salidas/límites; falta el prompt concreto que lo instruye.


---

# Objetivo siguiente etapa

Con la Fase 0 (Fundación) cerrada y el backend ya conectado a PostgreSQL/pgvector y Redis (primer hito de Fase 1), el siguiente entregable funcional es el Agente Investigador de Producto operando de punta a punta: entrada → investigación → salida persistida en base de datos.
