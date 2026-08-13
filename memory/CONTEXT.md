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

1.1 Alpha


Estado:

Fundación e Infraestructura cerradas. Dos agentes implementados y verificados: Investigador de Producto (con Gemini real) y Analítica Básica (agregación pura, sin proveedor de IA). Backend documentado (docs/004-Backend).


Fase:

FASE 1 - Infraestructura (cerrada); funcionalidad de agentes ya adelantada desde Fase 2-3


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

Convenciones de base de datos, esquema real de Fase 1 (tabla productos_candidatos), estrategia de migraciones (Alembic) y política de backups/retención.


## 007-Agentes

Estado:

Completado (volumen); 2 agentes con contrato, ambos implementados

Contrato técnico estándar, ciclo de vida de agentes, y dos agentes:
- Agente Investigador de Producto — implementado, con proveedor real (Gemini, verificado contra la API real) y fallback simulado.
- Agente de Analítica Básica — implementado, agregación de solo lectura sobre productos_candidatos, sin proveedor de IA (Nivel de permiso 0).

Nota histórica: un tercer contrato (Agente de Contenido) se redactó en una sesión y quedó descartado cuando otra sesión, en paralelo, avanzó con Analítica Básica en su lugar; el usuario confirmó continuar con Analítica Básica (ver DEC-026, DEC-027).


## 010-Prompts

Estado:

Completado

Convenciones de prompts, el prompt real del Agente Investigador de Producto (único agente que usa un proveedor de IA hasta ahora), y su registro.


## 004-Backend

Estado:

Completado

Arquitectura del backend, referencia de los 4 endpoints reales, patrón de 6 pasos para agregar un agente nuevo, y convenciones de manejo de errores/configuración.


---

# Entorno técnico

Estado:

Completado (Fase 0 y Fase 1)


Contenido:

- Backend FastAPI con /health, /health/ready, /agentes/investigador-producto, /agentes/analitica-basica
- docker-compose.yml: backend + PostgreSQL/pgvector + Redis
- Backend conectado realmente a PostgreSQL/pgvector y Redis
- Modelo SQLAlchemy productos_candidatos + primera migración de Alembic
- Agente Investigador de Producto: validación, proveedor Gemini real + simulado (fallback automático), reintentos, persistencia
- Agente de Analítica Básica: validación, agregación en Python sobre datos ya persistidos, sin escritura
- 38 tests automatizados, todos en verde


---

# Trabajo actual

Sin pendientes bloqueantes conocidos. Definir el tercer agente a especificar.


---

# Próximas acciones

1.

Elegir y especificar el tercer agente (SEO, atención al cliente, o marketing — ver docs/007-Agentes/04-Registro-de-Agentes.md), siguiendo docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md.


2.

Evaluar si conviene retomar el Agente de Contenido descartado, si sigue siendo prioritario para el negocio.


3.

Evaluar docs/005-Frontend: documentar antes de escribir la primera línea de código de frontend (a diferencia de 004-Backend, documentado después por necesidad).


---

# Decisiones recientes

Consultar:

memory/DECISIONS.md


---

# Última actualización

2026-08-05
