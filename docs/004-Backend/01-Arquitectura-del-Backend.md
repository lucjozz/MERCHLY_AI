# 01-Arquitectura-del-Backend.md

---

title: Arquitectura del Backend
document: 004-01
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-08-04
next_review: 2027-02-04
related:

* ../002-CTO/03-Stack-Tecnologico.md
* ../002-CTO/05-Estandares-Codigo.md
* 02-Referencia-de-Endpoints.md

---

# Arquitectura del Backend

## Propósito

Documentar cómo está organizado el código en `backend/` hoy, y cómo fluye una request a través de sus capas.

---

# 1. Estructura de Módulos

```text
backend/
├── alembic/              # Migraciones de base de datos (docs/006-BaseDatos)
│   ├── env.py
│   └── versions/
├── app/
│   ├── main.py            # Punto de entrada: crea la app FastAPI, registra routers
│   ├── api/                # Endpoints HTTP (routers de FastAPI)
│   │   ├── health.py       # /health, /health/ready
│   │   └── agentes.py      # /agentes/investigador-producto
│   ├── core/                # Infraestructura transversal
│   │   ├── config.py        # Settings (variables de entorno)
│   │   ├── database.py      # Motor SQLAlchemy async + sesión por request
│   │   └── redis.py         # Cliente Redis async
│   ├── models/               # Modelos SQLAlchemy (esquema real de la BD)
│   │   ├── base.py           # Base declarativa + mixin de timestamps/UUID
│   │   └── producto_candidato.py
│   ├── schemas/               # Modelos Pydantic (contratos de entrada/salida de la API)
│   │   └── investigador_producto.py
│   ├── services/                # Lógica de negocio, independiente de HTTP
│   │   ├── agente_investigador_producto.py   # Orquestación del agente
│   │   └── proveedores/                       # Proveedores de IA intercambiables
│   │       ├── base.py         # Interfaz abstracta (ProveedorInvestigacion)
│   │       ├── simulado.py     # Implementación de prueba, sin IA real
│   │       └── gemini.py       # Implementación real, vía Gemini
│   └── tests/                  # Tests automatizados (pytest)
├── requirements.txt
├── pyproject.toml               # Config de black/isort/ruff/mypy/pytest
├── alembic.ini
├── Dockerfile
└── .env.example
```

Esta estructura sigue al pie de la letra la definida en `002-CTO/05-Estandares-Codigo.md`.

---

# 2. Responsabilidad de Cada Capa

* **`api/`** — traduce HTTP a llamadas de dominio y de vuelta. No contiene lógica de negocio; valida vía Pydantic (`schemas/`) y delega a `services/`.
* **`core/`** — infraestructura que no pertenece a ningún dominio en particular: configuración, conexión a base de datos, conexión a Redis. Cualquier módulo puede importar de acá; `core/` no importa de `services/` ni de `api/`.
* **`models/`** — la verdad del esquema de base de datos, en código. Corresponde exactamente a `006-BaseDatos/02-Esquema-Fase1.md`.
* **`schemas/`** — contratos de entrada/salida de la API, en Pydantic. Corresponden exactamente a las secciones 2 y 3 del contrato técnico del agente en `007-Agentes`. **No se reutilizan como modelos de base de datos** — `schemas/` y `models/` son deliberadamente dos cosas distintas, aunque hoy tengan campos parecidos, porque lo que la API expone y lo que se persiste no siempre deben evolucionar juntos.
* **`services/`** — la lógica real: validación de negocio más allá de lo que Pydantic puede expresar, orquestación (reintentos, persistencia), y los proveedores de IA. Es la capa que se testea más exhaustivamente, porque no depende de HTTP ni de infraestructura para poder testearse (ver `04-Manejo-de-Errores-y-Configuracion.md`, sección sobre tests).

---

# 3. Ciclo de Vida de una Request

Usando `POST /agentes/investigador-producto` como ejemplo concreto:

1. FastAPI recibe el request y valida el cuerpo contra `InvestigacionInput` (`app/schemas/investigador_producto.py`). Si falla, devuelve `422` automáticamente, sin que el código del endpoint se ejecute.
2. El endpoint (`app/api/agentes.py`) resuelve sus dependencias vía `Depends`: una sesión de base de datos (`get_db_session`, `app/core/database.py`) y elige el proveedor de IA (`_obtener_proveedor`, según haya o no `GEMINI_API_KEY`).
3. Se instancia `AgenteInvestigadorProducto` (`app/services/agente_investigador_producto.py`) con esa sesión y ese proveedor, y se llama a `.ejecutar(entrada)`.
4. El servicio invoca al proveedor con política de reintentos, persiste los resultados en `productos_candidatos` vía la sesión de SQLAlchemy, y arma la salida.
5. FastAPI serializa la salida contra `InvestigacionOutput` y la devuelve.

Ninguna capa "salta" a otra: `api/` nunca toca SQLAlchemy directamente, `services/` nunca importa nada de `fastapi`.

---

# 4. Inyección de Dependencias

El proyecto usa el sistema de `Depends` de FastAPI para todo lo que necesita compartirse entre endpoints o mockearse en tests: sesión de base de datos, cliente de Redis. Esto es lo que permite que `backend/app/tests/test_agentes_api.py` y `test_readiness.py` reemplacen esas dependencias por mocks sin tocar el código de producción — ver `app.dependency_overrides` en esos archivos.

---

# 5. Estado de lo Documentado vs. lo Implementado

Hoy solo existe un dominio de negocio implementado: la investigación de producto. La estructura de carpetas (`api/`, `services/proveedores/`, etc.) ya está pensada para que un segundo agente no necesite reorganizar nada — solo agregar archivos nuevos siguiendo el mismo patrón (ver `03-Patron-para-Agregar-un-Agente-Nuevo.md`).

---

# Resumen Ejecutivo para IA

El backend sigue una arquitectura en capas: `api/` (HTTP) → `services/` (lógica de negocio y proveedores de IA) → `models/`+`core/` (persistencia e infraestructura), con `schemas/` como contratos de entrada/salida de la API, deliberadamente separados de `models/`. Toda dependencia compartida (sesión de BD, cliente Redis, proveedor de IA) se resuelve vía `Depends` de FastAPI, lo que permite mockearla en tests sin infraestructura real. La estructura ya está preparada para agregar un segundo agente sin reorganizar nada.
