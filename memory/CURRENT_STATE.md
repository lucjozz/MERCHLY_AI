# MERCHLY AI CURRENT STATE

Fecha:

2026-09-02


# Estado del Proyecto

Fase:

Infraestructura (Fase 1, cerrada); funcionalidad de agentes ya adelantada desde Fase 2-3


Versión:

1.3 Alpha


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

COMPLETADO (incluye docs/002-CTO/06-Entorno-Desarrollo.md actualizado con los comandos reales de levantamiento local y migraciones, ver DEC-023)


## 003-CEO

Estado:

COMPLETADO

Documentos:

✅ README (índice del volumen)

✅ Rol Operativo del CEO

✅ Modelo de Negocio (Opción C — Híbrido, aprobada, ver DEC-014)

✅ Criterios de Éxito de la Fase 0

✅ Estrategia Comercial Preliminar

✅ Métricas y Seguimiento


## 006-BaseDatos

Estado:

COMPLETADO

Convenciones de base de datos, esquema real de Fase 1 (tabla productos_candidatos), estrategia de migraciones (Alembic) y política de backups/retención. Implementado en código: modelo SQLAlchemy y primera migración. Ver DEC-019.


## 007-Agentes

Estado:

COMPLETADO

Contrato técnico estándar (10 secciones), ciclo de vida de agentes (8 etapas), y el Agente Investigador de Producto — implementado en código, con proveedor real (Gemini, verificado contra la API real) y fallback simulado. Ver DEC-017 a DEC-021 y DEC-023.


## 004-Backend

Estado:

COMPLETADO

Arquitectura del backend (estructura de módulos, ciclo de vida de una request), referencia de los 4 endpoints reales, patrón de 6 pasos para agregar un agente nuevo (extraído del proceso real con el Investigador de Producto), y convenciones de manejo de errores y configuración. Documentado en retrospectiva sobre código ya existente. Ver DEC-025.


## 010-Prompts

Estado:

COMPLETADO Y VERIFICADO

Convenciones de prompts, el prompt real del Agente Investigador de Producto, y su registro. ProveedorInvestigacionGemini implementado con el SDK google-genai y salida estructurada nativa. Verificado contra la API real de Gemini: responde con datos reales y respeta el prompt (evidencia real, sin inventar productos). Ver DEC-021 y DEC-023.


## Entorno Técnico (Fase 0 y Fase 1)

Estado:

COMPLETADO

Backend FastAPI con /health (liveness) y /health/ready (readiness, verifica PostgreSQL y Redis). docker-compose.yml levanta backend + PostgreSQL/pgvector + Redis, con env_file apuntando correctamente a backend/.env (corregido en DEC-023 — antes apuntaba a .env.example, dejando cualquier secreto real, como GEMINI_API_KEY, sin efecto dentro del contenedor sin ningún error visible). Backend conectado realmente a PostgreSQL/pgvector (SQLAlchemy async + psycopg 3) y Redis (redis.asyncio). Modelo SQLAlchemy productos_candidatos + primera migración de Alembic. Las migraciones no corren automáticamente al levantar los contenedores (decisión deliberada); se aplican a mano con `docker compose exec backend alembic upgrade head`, según documentado en docs/002-CTO/06-Entorno-Desarrollo.md y README.md. Ver DEC-017, DEC-018, DEC-022, DEC-023.


## Agente Investigador de Producto (implementación)

Estado:

COMPLETADO Y VERIFICADO CONTRA LA API REAL

Schemas Pydantic, proveedor abstracto con dos implementaciones (ProveedorInvestigacionSimulado y ProveedorInvestigacionGemini, con selección automática según haya o no GEMINI_API_KEY configurada), orquestación completa (validación, reintentos, persistencia, salida) y endpoint POST /agentes/investigador-producto. 23 tests automatizados, todos en verde. El usuario verificó además el proveedor real contra la API de Gemini: responde con datos reales y respeta el prompt documentado (evidencia real, sin inventar productos). Sin pendientes conocidos. Ver DEC-020, DEC-021 y DEC-023.


---

# En progreso

Ninguno.


---

# Completado (adenda)

## Agente de Marketing

Estado:

COMPLETADO (proveedor simulado; sin integración real con ChatGPT todavía)

Tercer agente del proyecto, implementado de punta a punta: contrato técnico (docs/007-Agentes/06-Agente-de-Marketing.md, rol "Marketing IA"), schemas Pydantic, proveedor simulado, servicio de orquestación (valida producto existente + estado 'en_catalogo' antes de invocar al proveedor, reintentos, distribución de presupuesto uniforme, no persiste nada), y endpoint POST /agentes/marketing. 19 tests nuevos (57 en total en el proyecto), todos en verde. Verificado con el servidor real (422 en validaciones, 500 esperado solo por falta de PostgreSQL real en este entorno). Ver DEC-028 y DEC-029.


## Sistema de Decisiones Humanas

Estado:

COMPLETADO Y CORREGIDO (ver DEC-030)

Se encontró en auditoría del 2026-09-02: código ya implementado en una sesión anterior (migración fechada 2026-08-26) sin contrato técnico, sin tests, y sin ningún DEC registrado — 4 tablas (decision_records, decision_context, decision_evidence, decision_outcomes) y 4 endpoints (POST /decisiones, GET /decisiones/{id}, GET /productos-candidatos, GET /productos-candidatos/{id}). Es el mecanismo real que resuelve el pendiente crítico de cambiar el estado de un producto candidato — vía POST /decisiones con action=approve/discard, no un PATCH directo.

Se detectó además un bug funcional real: el modelo DecisionRecord no tenía relaciones ORM hacia DecisionContext ni DecisionEvidence, así que context_data y evidencias se guardaban bien en la base pero la API siempre los devolvía vacíos, sin ningún error visible. Corregido (relationship() + selectinload + conversión manual a DecisionOutput). Se documentó en retrospectiva (docs/004-Backend/02-Referencia-de-Endpoints.md secciones 6-9, docs/006-BaseDatos/02-Esquema-Fase1.md sección 4) y se agregaron 20 tests nuevos (77 en total en el proyecto), todos en verde, incluyendo una prueba que reproduce el bug original.

Pendiente conocido: user_id es texto libre sin autenticación real (013-Seguridad sigue vacío). decision_outcomes existe como tabla pero sin endpoint que la use todavía.


## Agente de Analítica Básica

Estado:

COMPLETADO Y VERIFICADO

Segundo agente del proyecto, implementado de punta a punta: contrato técnico aprobado por el CTO (docs/007-Agentes/05-Agente-Analitica-Basica.md, rol "Analista IA"), schemas Pydantic, servicio de orquestación (agregación en Python sobre productos_candidatos, sin proveedor de IA — Nivel de permiso 0, solo lectura), y endpoint POST /agentes/analitica-basica. 15 tests nuevos (38 en total en el proyecto), todos en verde. Verificado con el servidor real: 422 en validaciones correctas, 500 esperado solo por falta de PostgreSQL real en este entorno (no un bug de código). Ver DEC-026 y DEC-027.


---

# Pendientes críticos identificados

Ninguno de Fase 0/1. El pendiente activo ahora es de higiene de proceso: mantener la disciplina "documentación antes que código" y "sin merge sin tests" en sesiones futuras — el sistema de Decisiones (ver DEC-030) es un ejemplo concreto de qué pasa cuando no se respeta (código en producción sin contrato, sin tests, con un bug silencioso).


---

# Próxima fase

Elegir entre: (a) integrar el proveedor real de ChatGPT para el Agente de Marketing, (b) especificar un cuarto agente (SEO o atención al cliente — ver docs/007-Agentes/04-Registro-de-Agentes.md), o (c) diseñar 013-Seguridad (autenticación real), ahora más urgente porque POST /decisiones expone `user_id` como texto libre sin validar.


---

# Última acción realizada

Auditoría general del repositorio (2026-09-02): se encontró y corrigió el sistema de Decisiones Humanas, implementado en una sesión anterior sin documentación, sin tests y sin DEC registrado. Se corrigió un bug real (relaciones ORM faltantes que ocultaban context_data/evidencias en la API), se agregaron 20 tests nuevos (77 en total) y se documentó en retrospectiva. Ver DEC-030.


---

# Próxima acción

Elegir entre integrar ChatGPT real para el Agente de Marketing, especificar el cuarto agente, o diseñar 013-Seguridad.


---

# Bloqueos

Ninguno.
