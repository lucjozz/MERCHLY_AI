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

1.2 Alpha


Estado:

Fundación e Infraestructura cerradas. Tres agentes implementados: Investigador de Producto (con Gemini real), Analítica Básica (agregación pura, sin proveedor de IA) y Marketing (proveedor simulado, ChatGPT real pendiente). Backend documentado (docs/004-Backend).


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

Completado (volumen); 3 agentes con contrato, los 3 implementados

Contrato técnico estándar, ciclo de vida de agentes, y tres agentes:
- Agente Investigador de Producto — implementado, con proveedor real (Gemini, verificado contra la API real) y fallback simulado.
- Agente de Analítica Básica — implementado, agregación de solo lectura sobre productos_candidatos, sin proveedor de IA (Nivel de permiso 0).
- Agente de Marketing — implementado, proveedor simulado (ChatGPT real pendiente), genera campañas para productos en estado 'en_catalogo', no persiste nada.

Nota histórica: un contrato descartado (Agente de Contenido) se redactó en una sesión y quedó sustituido cuando otra sesión, en paralelo, avanzó con Analítica Básica en su lugar; el usuario confirmó continuar con Analítica Básica (ver DEC-026, DEC-027).


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

- Backend FastAPI con /health, /health/ready, /agentes/investigador-producto, /agentes/analitica-basica, /agentes/marketing
- docker-compose.yml: backend + PostgreSQL/pgvector + Redis
- Backend conectado realmente a PostgreSQL/pgvector y Redis
- Modelo SQLAlchemy productos_candidatos + primera migración de Alembic
- Agente Investigador de Producto: validación, proveedor Gemini real + simulado (fallback automático), reintentos, persistencia
- Agente de Analítica Básica: validación, agregación en Python sobre datos ya persistidos, sin escritura
- Agente de Marketing: validación de producto en estado 'en_catalogo', proveedor simulado, reintentos, distribución de presupuesto uniforme, sin persistencia
- 57 tests automatizados, todos en verde


---

# Trabajo actual

Sin pendientes bloqueantes conocidos. Elegir entre integrar ChatGPT real para el Agente de Marketing, o especificar un cuarto agente.


---

# Próximas acciones

1.

Integrar el proveedor real de ChatGPT para el Agente de Marketing (cerrando su único pendiente), o especificar un cuarto agente (SEO o atención al cliente — ver docs/007-Agentes/04-Registro-de-Agentes.md).


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

2026-08-11
