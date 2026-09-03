# AICOS

Todas las entradas relevantes de este proyecto se documentan en este archivo, en orden cronológico descendente. El formato sigue el criterio de Conventional Commits (DEC-010), agrupando por tipo de cambio.

---

## [1.3.0-alpha] - 2026-09-02

### fix
- Se corrige un bug en el modelo `DecisionRecord` (`backend/app/models/decisiones.py`): faltaban las relaciones ORM hacia `DecisionContext` y `DecisionEvidence`. Efecto: `context_data` y `evidencias` se guardaban bien en la base de datos, pero la API siempre los devolvía vacíos (`null` / `[]`), sin ningún error visible.

### feat
- Se documenta y corrige en retrospectiva el sistema de Decisiones Humanas, implementado en una sesión anterior sin contrato, sin tests y sin DEC registrado: `POST /decisiones`, `GET /decisiones/{id}`, `GET /productos-candidatos`, `GET /productos-candidatos/{id}`. `POST /decisiones` con `action=approve/discard` es el mecanismo real que mueve un producto candidato entre `candidato`, `en_catalogo` y `descartado`.

### docs
- Se actualiza `docs/004-Backend/02-Referencia-de-Endpoints.md` (secciones 6-9) y `docs/006-BaseDatos/02-Esquema-Fase1.md` (sección 4) con los 4 endpoints y las 4 tablas nuevas, incluyendo la limitación explícita de que `user_id` es texto libre sin autenticación real.

### test
- Se agregan 20 tests nuevos (77 en total): relaciones del modelo y conversión a `DecisionOutput` (incluye reproducción directa del bug corregido), orquestación de `registrar_decision` con sesión mockeada, y los 4 endpoints HTTP nuevos.

### nota
- Auditoría general del repositorio (ver DEC-030): se detectó código en producción sin seguir la disciplina "documentación antes que código" ni la práctica de testear todo código nuevo. Corregido en este mismo ciclo.

## [1.2.0-alpha] - 2026-08-11

### feat
- Se implementa el Agente de Marketing (`backend/app/services/agente_marketing.py`): tercer agente del proyecto, recibe hasta 10 productos ya aprobados en catálogo (`estado = 'en_catalogo'`) y genera ángulos de campaña, copy por canal, público objetivo sugerido y una distribución de presupuesto orientativa (reparto uniforme, determinístico). No persiste nada ni ejecuta gasto real.
- Se agrega `ProveedorMarketingSimulado`, siguiendo el mismo patrón ya validado con el Investigador de Producto (simulado primero, proveedor real ChatGPT queda pendiente).
- Se agrega el endpoint `POST /agentes/marketing`.

### docs
- Se aprueba el contrato técnico del Agente de Marketing (`docs/007-Agentes/06-Agente-de-Marketing.md`), rol "Marketing IA" ya existente en el catálogo organizacional.
- Se actualiza `docs/004-Backend/02-Referencia-de-Endpoints.md` con el endpoint nuevo.

### test
- Se agregan 19 tests nuevos (57 en total): validación de schema, proveedor simulado, orquestación (validación de estado del producto, distribución de presupuesto, manejo de fallas del proveedor, no-persistencia) y el endpoint HTTP.

## [1.1.0-alpha] - 2026-08-05

### feat
- Se implementa el Agente de Analítica Básica (`backend/app/services/agente_analitica_basica.py`): segundo agente del proyecto, de solo lectura (Nivel de permiso 0), sin proveedor de IA — agrega en Python los datos ya existentes en `productos_candidatos` (resumen por categoría/estado/nivel, tasa de conversión, actividad del Investigador de Producto).
- Se agrega el endpoint `POST /agentes/analitica-basica`.

### docs
- Se aprueba (CTO) el contrato técnico del Agente de Analítica Básica (`docs/007-Agentes/05-Agente-Analitica-Basica.md`), pasando de "Contrato en Diseño" a "Contrato Aprobado" e "Implementado".
- Se actualiza `docs/004-Backend/02-Referencia-de-Endpoints.md` con el endpoint nuevo.

### test
- Se agregan 15 tests nuevos (38 en total): validación de schema, orquestación (agrupación, tasa de conversión, actividad del investigador, no-escritura, reintentos) y el endpoint HTTP.

### nota
- Un contrato previo para un "Agente de Contenido", redactado en una sesión distinta, quedó descartado cuando otra sesión avanzó en paralelo con Analítica Básica. El usuario confirmó continuar con Analítica Básica. Ver DEC-026 y DEC-027.

## [1.0.0-alpha] - 2026-08-04

### docs
- Se completa `docs/004-Backend`: arquitectura del backend (estructura de módulos, ciclo de vida de una request), referencia real de los 3 endpoints existentes, patrón de 6 pasos para agregar un agente nuevo (extraído del proceso real seguido con el Agente Investigador de Producto), y convenciones de manejo de errores y configuración. Documentado en retrospectiva sobre código ya existente (ver DEC-025).

## [0.9.1-alpha] - 2026-08-03

### fix
- Se corrige `docker-compose.yml`: el servicio `backend` cargaba `env_file: ./backend/.env.example` en vez de `./backend/.env`, por lo que cualquier valor puesto en `backend/.env` (incluida `GEMINI_API_KEY`) nunca llegaba al contenedor — el backend arrancaba siempre con `ProveedorInvestigacionSimulado` sin ningún error visible (ver DEC-023).
- Se corrigen contradicciones internas en `memory/CURRENT_STATE.md` y el mismo error de fase desactualizada en `README.md`, introducidas al integrar la verificación de Gemini sobre una copia desactualizada de esos archivos (ver DEC-024).

### verified
- Se verifica `ProveedorInvestigacionGemini` contra la API real de Gemini: responde con datos reales (no el proveedor simulado) y respeta el prompt documentado (evidencia real, sin inventar productos). Cierra el pendiente de DEC-021.

### docs
- Se actualizan `docs/007-Agentes/04-Registro-de-Agentes.md` y `docs/010-Prompts/03-Registro-de-Prompts.md` quitando la nota de "pendiente verificación final". Se actualiza `docs/002-CTO/06-Entorno-Desarrollo.md` con los comandos reales de levantamiento local (incluyendo `alembic upgrade head` manual) y `README.md` con una nueva sección "Cómo Empezar".

## [0.9.0-alpha] - 2026-07-30

### docs
- Se completa `docs/010-Prompts`: convenciones de prompts, el prompt real del Agente Investigador de Producto, y su registro.

### feat
- Se implementa `ProveedorInvestigacionGemini` (`backend/app/services/proveedores/gemini.py`): integración real con Gemini vía el SDK `google-genai`, con salida estructurada nativa (`response_schema`) en vez de parseo de texto libre.
- El endpoint `POST /agentes/investigador-producto` elige automáticamente entre el proveedor real (si `GEMINI_API_KEY` está configurada) y el proveedor simulado (si no).

### test
- Se agregan 5 tests nuevos (23 en total) con un cliente de Gemini mockeado, sin llamar a la API real de Google.

### pendiente
- Verificación final del proveedor Gemini contra la API real, no realizable desde este entorno de ejecución (sin acceso de red a Google). Debe correrse con una `GEMINI_API_KEY` válida en la máquina del usuario o en CI/CD.

## [0.8.0-alpha] - 2026-07-27

### feat
- Se implementa en código el Agente Investigador de Producto (`backend/app/services/agente_investigador_producto.py`), adelantado desde Fase 2 a Fase 1: validación de entrada (schemas Pydantic replicando el contrato técnico), proveedor abstracto con implementación provisional simulada, reintentos según el contrato (sección 8), persistencia en `productos_candidatos` y endpoint `POST /agentes/investigador-producto`.

### test
- Se agregan 12 tests nuevos (18 en total en el proyecto): validaciones de entrada, comportamiento del proveedor simulado, orquestación del agente (persistencia, agrupación por `investigacion_id`, manejo de fallas) y el endpoint HTTP.

### docs
- Se actualiza `docs/007-Agentes/03-Agente-Investigador-de-Producto.md` y `04-Registro-de-Agentes.md` reflejando la etapa "Implementado" y el pendiente de reemplazar el proveedor simulado por una integración real con Gemini.

## [0.7.0-alpha] - 2026-07-27

### docs
- Se completa `docs/006-BaseDatos`: convenciones de base de datos, esquema real de Fase 1 (`productos_candidatos`), estrategia de migraciones con Alembic y política de backups/retención.

### feat
- Se agrega el modelo SQLAlchemy `ProductoCandidato` (`backend/app/models/`), con clase base compartida (`Base`, `ConMarcaDeTiempo`) que implementa las convenciones de UUID, timestamps y borrado lógico.
- Se configura Alembic (`backend/alembic/`) y se agrega la primera migración (`productos_candidatos`), validada en modo offline sin requerir una base PostgreSQL real conectada.

## [0.6.0-alpha] - 2026-07-27

### feat
- El backend se conecta realmente a PostgreSQL/pgvector (SQLAlchemy 2.0 async + psycopg 3) y a Redis (redis.asyncio).
- Se agrega el endpoint `/health/ready` (readiness), separado de `/health` (liveness): verifica ambas conexiones y responde "ok" o "degraded" sin caerse si alguna dependencia falla.

### test
- Se agregan 3 tests para `/health/ready` con dependencias mockeadas, sin requerir PostgreSQL/Redis reales.

## [0.5.0-alpha] - 2026-07-26

### feat
- Se agrega el backend mínimo (`backend/`) en FastAPI, con endpoint `/health` probado (pytest + solicitud HTTP real, 200 OK).
- Se agrega `docker-compose.yml` en la raíz, levantando backend, PostgreSQL con extensión `pgvector` y Redis en un solo paso.

### docs
- Se completa `docs/007-Agentes`: contrato técnico estándar de agentes IA, ciclo de vida de agentes, y el primer agente con contrato técnico completo (Agente Investigador de Producto).
- Se declara el cierre formal de la Fase 0 (Fundación): todos los criterios documentales y técnicos de `docs/003-CEO/03-Criterios-de-Exito-Fase0.md` quedan cumplidos.

### chore
- Auditoría general del repositorio: se corrige el orden y se completan entradas faltantes en `memory/DECISIONS.md` (DEC-014, DEC-017), se sincronizan `memory/CURRENT_STATE.md`, `memory/CONTEXT.md`, `memory/NEXT_STEPS.md` y `prompts/MASTER_CONTEXT_PROMPT.md` con el estado real del proyecto, y se elimina un archivo suelto (`backend/test`).

## [0.4.0-alpha] - 2026-07-26

### docs
- Se completa `ROADMAP.md` con las 9 fases del proyecto (Fundación a Empresa Autónoma), volúmenes asociados, criterios de cierre e hitos estimados.
- Se aprueba el modelo de negocio de AICOS: Opción C (Híbrido) — tiendas propias en Fase 0-1, evaluación de apertura a terceros en Fase 2+ (DEC-014).
- Se completa `docs/003-CEO` (rol operativo del CEO, modelo de negocio, criterios de éxito de Fase 0, estrategia comercial preliminar, métricas y seguimiento).
- Se completa `docs/002-CTO` (rol técnico-operativo, metodología de desarrollo, stack tecnológico, flujo Git/CI, estándares de código, entorno de desarrollo).

## [0.3.0-alpha] - 2026-07-22

### docs
- Se completa `docs/100-Organizacion` (organigrama, estructura empresarial, roles ejecutivos, departamentos, capacidades organizacionales, agentes IA, matriz RACI).

## [0.2.0-alpha] - 2026-07-21

### docs
- Se completa `docs/001-Arquitectura` (arquitectura general, del sistema, de agentes, de datos, tecnológica, flujos de información, modelo de comunicación, seguridad, automatización, escalabilidad, decisiones arquitectónicas).

## [0.1.0-alpha] - 2026-07-20

### docs
- Se completa `docs/000-Constitucion` (misión, visión, valores, principios, objetivos, roles, gobernanza, normas de ingeniería, uso de IA, estándares de calidad, seguridad, escalabilidad, glosario, historial).
- Arranque del proyecto: repositorio estructurado, decisión de idioma oficial (español) y de GitHub como fuente principal (DEC-001, DEC-002).
