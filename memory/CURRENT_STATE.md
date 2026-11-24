# MERCHLY AI CURRENT STATE

Fecha:

2026-11-23


# Estado del Proyecto

Fase:

Infraestructura (Fase 1, cerrada); funcionalidad de agentes ya adelantada desde Fase 2-3


Versión:

1.4 Alpha (endurecimiento de seguridad para lanzamiento)


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

Resuelto (DEC-031/032): user_id sale del token y las decisiones siguen una máquina de estados con estados finales inmutables. decision_outcomes existe como tabla pero sin endpoint que la use todavía.


## 013-Seguridad

Estado:

BASE (DEC-031) + ENDURECIMIENTO PARA LANZAMIENTO (DEC-032) IMPLEMENTADOS — pendiente visto bueno del CTO del documento 013-04

* Multi-tenancy: tabla `organizaciones`, `organizacion_id` en todo, Row-Level Security con FORCE, rol de app `merchly_app` sin privilegios de dueño, decisiones append-only.
* Sesiones: PyJWT (access 15 min con jti/iss/aud), refresh tokens rotativos con detección de reutilización, logout con revocación, cerrar todas las sesiones, login con Google implementado de punta a punta (Client ID configurado; falta la prueba con una cuenta real).
* Frontend: BFF de Next (cookies HttpOnly, el navegador nunca ve el token), `proxy.ts` con guard de rutas, refresh automático y CSP con nonce; 401 → login, 403 → "sin permiso".
* Todo exige login salvo health y login. Rate limiting en Redis (login fail-closed, agentes con cuota por organización). Validación estricta (extra="forbid", topes), errores sin filtrar datos, headers de seguridad, CORS por variable.
* Docker: puertos solo en 127.0.0.1, contraseñas fuertes, Redis con contraseña, imagen sin root y parcheada, límites de recursos.
* Dependencias: FastAPI 0.165 / Starlette 1.10 / PyJWT; Next 16.4.6. pip-audit, npm audit y trivy en 0.
* Tests: 216 en verde, incluidos de integración contra Postgres real (RLS, IDOR, privilegios, concurrencia, refresh). Pentest black-box: 68/69 (la única "falla" es un falso positivo del script).
* CI (GitHub Actions), Dependabot y pre-commit con gitleaks: configurados, todavía no corrieron en GitHub.

Frontend: pantalla "Plan y pagos" (beta gratuita, cobros no activos todavía).

## Proveedores reales y funciones de producto (DEC-033, DEC-034)

* Gemini y OpenAI reales listos, con modelo de IA según el plan (beta, emprendedor, negocio); se activan al cargar `GEMINI_API_KEY` y `OPENAI_API_KEY`. `scripts.probar_ia` mide costo real. Sin claves, siguen los simulados.
* Historial de campañas (guardar, editar, compartir), canales reales (copiar, WhatsApp, email, descargar), perfil del negocio con onboarding, precios en bolivianos con calculadora de margen y búsqueda de proveedores, equipo con invitaciones y roles, uso del plan visible, página de Ayuda y botón de WhatsApp de soporte (falta el número).
* 269 tests de backend; E2E por el BFF 32/32.

Pendientes para lanzar: ver docs/013-Seguridad/05-Pendientes-para-Lanzar.md.


## Agente de Analítica Básica

Estado:

COMPLETADO Y VERIFICADO

Segundo agente del proyecto, implementado de punta a punta: contrato técnico aprobado por el CTO (docs/007-Agentes/05-Agente-Analitica-Basica.md, rol "Analista IA"), schemas Pydantic, servicio de orquestación (agregación en Python sobre productos_candidatos, sin proveedor de IA — Nivel de permiso 0, solo lectura), y endpoint POST /agentes/analitica-basica. 15 tests nuevos (38 en total en el proyecto), todos en verde. Verificado con el servidor real: 422 en validaciones correctas, 500 esperado solo por falta de PostgreSQL real en este entorno (no un bug de código). Ver DEC-026 y DEC-027.


---

# Pendientes críticos identificados

Ver docs/013-Seguridad/05-Pendientes-para-Lanzar.md. Los principales: visto bueno del CTO a 013-04, rotar la contraseña del admin, elegir hosting y dominio (Fase 2: HTTPS, Cloudflare, backups, monitoreo) y crear el Client ID de Google.

---

# Próxima fase

Fase 1 de seguridad pendiente de producto: gestión de usuarios (invitar, desactivar, cambiar rol), bitácora de auditoría y botón "Continuar con Google". Después, Fase 2 (hosting).

---

# Última acción realizada

2026-11-23: auditoría de seguridad (37 pruebas, 25 fallas) y endurecimiento completo para lanzamiento (DEC-032): multi-tenancy con RLS, BFF con cookies HttpOnly, refresh tokens, rate limiting, Docker endurecido, dependencias sin vulnerabilidades, CI. Rediseño visual del frontend (mismos colores, lenguaje simple). Bug corregido: la pantalla de detalle de producto había sido pisada en 15e42ad.

---

# Próxima acción

El CTO revisa docs/013-Seguridad/04 y DEC-032. Daniel rota su contraseña con `docker compose exec backend python -m scripts.seed_admin --rotar` y sube los commits.

---

# Bloqueos

Ninguno.

## Funciones diferenciales para Bolivia (DEC-038)

* Costo real puesto en Bolivia en la calculadora de margen: FOB, flete, seguro presunto, CIF, gravamen arancelario, IVA de importación, gastos locales y comisión de cobro.
* Pantalla Catálogo WhatsApp (`/catalogo`): solo productos aprobados; copiar o abrir en WhatsApp.
* Calendario de temporadas bolivianas: `GET /temporadas`, tarjeta en el panel con ideas que precargan la búsqueda, y contexto para el Investigador.
* Tests del frontend con `node --test` (`npm test`), también en el CI.
* Agente vendedor por WhatsApp: idea evaluada en `docs/004-Backend/05`, sección 4; queda para después de la beta.
* Pendiente: visto bueno del CTO.

## Inventario y catálogo público (DEC-039, fase A1)

* Tablas `inventario_productos` e `inventario_fotos`, con RLS forzado (migración 202611250001).
* Dos vistas sobre los mismos productos:
  * **Inventario privado** del dueño: costo, gastos, proveedor, notas, stock y margen.
  * **Catálogo público** que usa la IA: solo los productos publicados y sin datos privados, garantizado por un test.
* Fotos re-codificadas a WebP sin EXIF; se sirven solo con sesión.
* Importación de Excel/CSV con vista previa obligatoria; PDF, Word y fotos quedan para A2.
* Pantalla `/inventario`, con las pestañas privado y público.
* Siguiente: A2, importar cualquier formato con IA.

## Agente de Atención al Cliente (DEC-039, fases A4 y A5)

* Tablas nuevas: `atencion_config`, `qr_pagos`, `zonas_envio`, `conversaciones`, `mensajes` (append-only), `pedidos` y `notificaciones`. Todas con RLS forzado; migración 202611260001.
* Orquestador más 5 sub-agentes:
  * Catálogo/Stock;
  * Envíos por zona;
  * Venta (reserva y QR, informar pago);
  * Conversación;
  * Derivar a una persona.
* Proveedores: IA real (OpenAI con herramientas) o simulado.
* El pago lo confirma solo una persona, y el stock se descuenta recién ahí.
* Guardia de montos: los números nunca salen del modelo.
* Simulador de chat dentro de la app.
* Siguiente: sub-agentes de Catálogo (A2 y A3); Visión (A6); Fase B con WhatsApp.
