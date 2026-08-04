# 04-Manejo-de-Errores-y-Configuracion.md

---

title: Manejo de Errores y Configuración
document: 004-04
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-08-04
next_review: 2027-02-04
related:

* 01-Arquitectura-del-Backend.md
* ../000-Constitucion/11-Seguridad.md

---

# Manejo de Errores y Configuración

## Propósito

Documentar las convenciones ya en uso para manejo de errores y configuración, para que el código nuevo las siga sin tener que inferirlas leyendo el código existente.

---

# 1. Configuración (`app/core/config.py`)

Toda configuración pasa por una única clase `Settings` (Pydantic `BaseSettings`), con:

* Valores por defecto sensatos para desarrollo local (ej. `database_url` ya apunta al contenedor `db` de `docker-compose.yml`).
* Campos opcionales (`| None = None`) para configuración sensible que no debe tener un default real (ej. `gemini_api_key`).
* Una función `get_settings()` cacheada con `@lru_cache`, para no releer variables de entorno en cada request.

**Regla:** ningún módulo lee `os.environ` directamente. Toda configuración nueva se agrega como campo de `Settings`, con su valor real viviendo en `backend/.env` (nunca en `.env.example`, que solo tiene placeholders o valores de desarrollo sin riesgo).

En tests, cuando hace falta forzar un valor de configuración distinto, se usa `monkeypatch.setenv(...)` seguido de `get_settings.cache_clear()` — ver `backend/app/tests/test_proveedor_gemini.py` como referencia.

---

# 2. Excepciones de Dominio

Cada capa de proveedor/servicio define su propia excepción de dominio (ej. `ProveedorInvestigacionError` en `app/services/proveedores/base.py`), en vez de dejar propagar excepciones de librerías externas (`google.genai`, `sqlalchemy`, etc.) hacia capas superiores.

**Regla:** un proveedor nunca deja escapar una excepción de su SDK subyacente sin envolverla. Ver `app/services/proveedores/gemini.py`: cualquier excepción de `google.genai` se captura y se relanza como `ProveedorInvestigacionError`, para que el código que orquesta reintentos (`AgenteInvestigadorProducto`) no necesite conocer las excepciones específicas de cada proveedor.

---

# 3. Reintentos

La política de reintentos vive en el servicio de orquestación (`app/services/agente_investigador_producto.py`), no en el proveedor. El proveedor solo debe fallar de forma clara (levantando su excepción de dominio); cuántas veces reintentar y con qué espera es una decisión de negocio que corresponde al contrato técnico del agente (`007-Agentes`, sección 8 de cada contrato), no una decisión técnica del proveedor.

---

# 4. Errores HTTP

* **422:** siempre generado automáticamente por FastAPI/Pydantic a partir de los validadores de los schemas (`app/schemas/`). El código de los endpoints no lanza `HTTPException(422, ...)` a mano para validaciones que Pydantic ya puede expresar.
* **500:** se deja que ocurra de forma natural ante errores no manejados (ej. base de datos inalcanzable) — no se capturan genéricamente para devolver un mensaje "amigable" que oculte el problema real durante desarrollo. Antes de producción real (Fase 2+), esto debe revisarse para no filtrar detalles internos en la respuesta.
* **Nunca 200 con un error disfrazado en el cuerpo**, excepto en el caso deliberado de `/health/ready`, donde `"status": "degraded"` es información operativa esperada, no un error del endpoint en sí (ver `002-Referencia-de-Endpoints.md`, sección 2).

---

# 5. Logging

Se usa el módulo estándar `logging` de Python (`logger = logging.getLogger(__name__)` por archivo), no `print()`. Los reintentos fallidos y los errores de proveedor se loguean con `logger.warning`/`logger.error` antes de decidir cómo responder — ver `app/services/agente_investigador_producto.py` como referencia. Todavía no hay configuración centralizada de logging (formato, destino, niveles por entorno) — es un pendiente para cuando exista un entorno de staging/producción real.

---

# 6. Tests: Nunca Contra Infraestructura Real

Ningún test automatizado en `backend/app/tests/` requiere PostgreSQL, Redis, o la API de Gemini corriendo. Se logra con:

* `app.dependency_overrides` de FastAPI, para reemplazar `get_db_session`/`get_redis_client` por mocks en tests de endpoints.
* `unittest.mock.AsyncMock`/`MagicMock` inyectados directamente en los servicios/proveedores, cuando se testea la lógica sin pasar por HTTP.
* Para el proveedor Gemini específicamente: se inyecta un cliente `genai.Client` falso por constructor (`ProveedorInvestigacionGemini(cliente=..., modelo=...)`), en vez de mockear el módulo `google.genai` globalmente.

**Regla:** si un test nuevo necesitara una base de datos o API real para pasar, es una señal de que la lógica bajo prueba no está suficientemente separada de la infraestructura — hay que revisar el diseño antes de agregar el test, no agregar un test lento o frágil.

---

# Resumen Ejecutivo para IA

Configuración: toda vía la clase `Settings` cacheada, ningún acceso directo a `os.environ`, secretos reales solo en `backend/.env`. Errores: cada proveedor envuelve las excepciones de su SDK en una excepción de dominio propia; los reintentos son responsabilidad del servicio de orquestación, no del proveedor; los 422 los genera Pydantic automáticamente. Logging: módulo estándar, nunca `print()`. Tests: nunca requieren infraestructura real — dependencias mockeadas vía `Depends`/`dependency_overrides` o inyección directa por constructor.
