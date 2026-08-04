# 02-Referencia-de-Endpoints.md

---

title: Referencia de Endpoints
document: 004-02
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-08-04
next_review: 2027-02-04
related:

* 01-Arquitectura-del-Backend.md
* ../007-Agentes/03-Agente-Investigador-de-Producto.md

---

# Referencia de Endpoints

## Propósito

Catálogo real de los endpoints HTTP que expone el backend hoy. Se actualiza en el mismo cambio que agrega o modifica un endpoint — no es una API pública versionada todavía (eso corresponde a una decisión futura, cuando exista Fase 7 o consumidores externos reales).

---

# 1. `GET /health`

**Propósito:** liveness — confirma que el proceso está corriendo, sin depender de nada externo.

**Respuesta 200:**

```json
{
  "status": "ok",
  "service": "MERCHLY AI Backend",
  "version": "0.1.0",
  "environment": "local",
  "timestamp": "2026-08-04T12:00:00+00:00"
}
```

No requiere autenticación. No consulta PostgreSQL ni Redis — para eso existe `/health/ready`.

---

# 2. `GET /health/ready`

**Propósito:** readiness — confirma que las dependencias reales (PostgreSQL, Redis) están alcanzables.

**Respuesta 200 (todo bien):**

```json
{
  "status": "ok",
  "database": "ok",
  "redis": "ok",
  "timestamp": "2026-08-04T12:00:00+00:00"
}
```

**Respuesta 200 (alguna dependencia falla — no es un 5xx):**

```json
{
  "status": "degraded",
  "database": "error",
  "redis": "ok",
  "timestamp": "2026-08-04T12:00:00+00:00"
}
```

Este endpoint siempre responde `200`, incluso si `status` es `"degraded"` — el código HTTP indica que el propio endpoint funcionó; el campo `status` indica el resultado del chequeo. Un orquestador (Kubernetes, Docker healthcheck) debe mirar el campo `status`, no solo el código HTTP.

---

# 3. `POST /agentes/investigador-producto`

**Propósito:** ejecuta una investigación de producto con el Agente Investigador de Producto (`007-Agentes/03-...`).

**Request:**

```json
{
  "categoria": "audífonos bluetooth",
  "mercado_objetivo": "MX",
  "presupuesto_max_producto": 50,
  "excluir_marcas": ["MarcaX"],
  "cantidad_resultados": 5
}
```

Solo `categoria` y `mercado_objetivo` son obligatorios. Ver `007-Agentes/03-...`, sección 2, para las reglas de validación completas (código ISO del mercado, categorías prohibidas, truncado de `cantidad_resultados` a 50).

**Respuesta 200:**

```json
{
  "productos": [
    {
      "nombre_producto": "...",
      "categoria": "audífonos bluetooth",
      "precio_estimado_proveedor": 12.5,
      "precio_sugerido_venta": 29.99,
      "nivel_demanda_estimado": "alto",
      "nivel_competencia_estimado": "medio",
      "fuentes_evidencia": ["https://..."],
      "riesgos_identificados": []
    }
  ],
  "metadata": {
    "categoria_consultada": "audífonos bluetooth",
    "mercado_objetivo": "MX",
    "fecha_investigacion": "2026-08-04T12:00:00+00:00",
    "total_productos_evaluados": 5,
    "total_productos_devueltos": 5,
    "confianza": "normal",
    "investigacion_id": "uuid-generado"
  }
}
```

**Respuesta 422:** la entrada no pasó las validaciones del contrato (ej. categoría prohibida, código de mercado inválido). El cuerpo del error sigue el formato estándar de validación de FastAPI/Pydantic.

**Efecto secundario:** si hay productos en la respuesta, quedan persistidos en `productos_candidatos` con `estado = 'candidato'` (`006-BaseDatos/02-Esquema-Fase1.md`). Ningún producto pasa a `en_catalogo` desde este endpoint — eso requiere una acción humana separada, todavía no implementada como endpoint.

**Proveedor usado:** automático — `ProveedorInvestigacionGemini` si `GEMINI_API_KEY` está configurada, si no `ProveedorInvestigacionSimulado` (`004-Backend/03-...`, o directamente `app/api/agentes.py`, función `_obtener_proveedor`).

**Requiere:** que la migración de `productos_candidatos` ya esté aplicada (`docker compose exec backend alembic upgrade head`) — de lo contrario, la persistencia falla con un error de base de datos.

---

# 4. Endpoints Pendientes (no implementados)

Estos endpoints son necesarios para el flujo completo del negocio, pero todavía no existen:

* **Cambiar `estado` de un producto candidato** (de `candidato` a `en_catalogo` o `descartado`) — requiere autenticación/autorización humana, que todavía no está diseñada (`013-Seguridad` sigue vacío).
* **Listar/consultar productos candidatos** ya persistidos — hoy solo se pueden ver insertando directamente en la base o vía `POST /agentes/investigador-producto` (que siempre crea nuevos, nunca lista existentes).

---

# Resumen Ejecutivo para IA

El backend expone hoy 3 endpoints: `GET /health` (liveness), `GET /health/ready` (readiness, verifica PostgreSQL y Redis, siempre 200 con campo `status`), y `POST /agentes/investigador-producto` (ejecuta el agente, persiste resultados como `candidato`, nunca los aprueba automáticamente). No existe todavía ningún endpoint para listar productos candidatos o cambiar su estado — son los próximos candidatos naturales a implementar.
