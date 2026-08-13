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

# 4. `POST /agentes/analitica-basica`

**Propósito:** genera un reporte agregado de solo lectura sobre `productos_candidatos` (`007-Agentes/05-Agente-Analitica-Basica.md`).

**Request:**

```json
{
  "fecha_desde": "2026-07-06",
  "fecha_hasta": "2026-08-05",
  "categoria": "audífonos bluetooth",
  "mercado_objetivo": "MX",
  "agrupar_por": "categoria"
}
```

Todos los campos son opcionales — sin body (`{}`), usa los defaults del contrato (últimos 30 días, agrupado por categoría, sin filtros de categoría/mercado).

**Respuesta 200:**

```json
{
  "periodo": {"fecha_desde": "2026-07-06", "fecha_hasta": "2026-08-05"},
  "resumen_catalogo": {
    "total_productos_candidatos": 12,
    "agrupado_por": "categoria",
    "grupos": [{"clave": "audífonos bluetooth", "cantidad": 8, "porcentaje_del_total": 66.67}]
  },
  "tasa_conversion_catalogo": {
    "candidato": 9, "en_catalogo": 2, "descartado": 1,
    "tasa_candidato_a_en_catalogo": 0.1667
  },
  "actividad_agente_investigador": {
    "total_investigaciones": 3,
    "promedio_productos_por_investigacion": 4.0,
    "categorias_mas_investigadas": ["audífonos bluetooth"]
  },
  "metadata": {"fecha_generacion_reporte": "...", "filtros_aplicados": {"...": "..."}}
}
```

Un catálogo sin resultados en el rango pedido devuelve `200` con totales en cero — nunca es un error (contrato, sección 8).

**Respuesta 422:** `fecha_desde` posterior a `fecha_hasta`, rango mayor a 365 días, `mercado_objetivo` inválido, o `agrupar_por` fuera del enum permitido.

**Efecto secundario:** ninguno — es de solo lectura (Nivel de permiso 0). Nunca escribe en `productos_candidatos` ni en ninguna otra tabla.

**Nota de implementación:** la agregación se hace en Python sobre las filas ya filtradas por SQL, no con `GROUP BY`. Es la opción más simple mientras el catálogo es pequeño; revisar si el volumen crece (ver `backend/app/services/agente_analitica_basica.py`).

---

# 5. `POST /agentes/marketing`

**Propósito:** genera una propuesta de campaña publicitaria para productos ya aprobados en catálogo (`007-Agentes/06-Agente-de-Marketing.md`).

**Request:**

```json
{
  "productos_candidato_ids": ["uuid"],
  "canales_objetivo": ["email", "redes_sociales"],
  "idioma_destino": "es",
  "tono": "entusiasta",
  "presupuesto_mensual_referencia": 500
}
```

Solo `productos_candidato_ids`, `canales_objetivo` e `idioma_destino` son obligatorios. Cada producto debe existir y estar en `estado = 'en_catalogo'` — de lo contrario, `422`.

**Respuesta 200:**

```json
{
  "productos_candidato_ids": ["uuid"],
  "angulos_de_campana": ["..."],
  "copy_por_canal": {"email": [{"titulo": "...", "cuerpo": "..."}]},
  "publico_objetivo_sugerido": "...",
  "distribucion_presupuesto_sugerida": {"email": 0.5, "redes_sociales": 0.5},
  "advertencias": [],
  "metadata": {"idioma_destino": "es", "tono": "entusiasta", "fecha_generacion": "...", "campana_id": "uuid"}
}
```

**Respuesta 422:** algún producto no existe, no está en `estado = 'en_catalogo'`, o la entrada no cumple las validaciones del contrato (canales vacíos/duplicados, idioma inválido, más de 10 productos).

**Efecto secundario:** ninguno — no persiste nada (contrato, sección 3). Nunca publica anuncios ni ejecuta gasto real; `distribucion_presupuesto_sugerida` es siempre orientativa.

**Proveedor usado:** hoy siempre `ProveedorMarketingSimulado` — la integración real con ChatGPT todavía no existe (ver `007-Agentes/04-Registro-de-Agentes.md`, "Pendientes Conocidos").

---

# 6. Endpoints Pendientes (no implementados)

Estos endpoints son necesarios para el flujo completo del negocio, pero todavía no existen:

* **Cambiar `estado` de un producto candidato** (de `candidato` a `en_catalogo` o `descartado`) — requiere autenticación/autorización humana, que todavía no está diseñada (`013-Seguridad` sigue vacío).
* **Listar/consultar productos candidatos** ya persistidos — hoy solo se pueden ver insertando directamente en la base o vía `POST /agentes/investigador-producto` (que siempre crea nuevos, nunca lista existentes).

---

# Resumen Ejecutivo para IA

El backend expone hoy 5 endpoints: `GET /health` (liveness), `GET /health/ready` (readiness), `POST /agentes/investigador-producto` (proveedor real Gemini + fallback simulado, persiste resultados), `POST /agentes/analitica-basica` (solo lectura, sin proveedor de IA) y `POST /agentes/marketing` (proveedor simulado, no persiste nada). No existe todavía ningún endpoint para listar productos candidatos individualmente o cambiar su estado — son los próximos candidatos naturales a implementar.
