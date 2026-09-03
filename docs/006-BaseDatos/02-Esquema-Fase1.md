# 02-Esquema-Fase1.md

---

title: Esquema de Base de Datos — Fase 1
document: 006-02
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-09-02
next_review: 2027-03-02
related:

* 01-Convenciones-de-Base-de-Datos.md
* ../007-Agentes/03-Agente-Investigador-de-Producto.md
* ../003-CEO/03-Criterios-de-Exito-Fase0.md
* ../004-Backend/02-Referencia-de-Endpoints.md

---

# Esquema de Base de Datos — Fase 1

## Propósito

Documentar el esquema real y actual de PostgreSQL. Hoy existe **una sola tabla**, `productos_candidatos`, que es la que el Agente Investigador de Producto necesita para persistir sus resultados, conforme a la sección 3 ("Salidas") de su contrato técnico en `007-Agentes/03-Agente-Investigador-de-Producto.md`.

No se documentan tablas para funcionalidad futura (agentes de SEO, contenido, marketing, etc.) hasta que esos agentes tengan su propio contrato técnico aprobado, conforme al Principio Rector de este volumen.

---

# 1. Tabla `productos_candidatos`

Almacena cada producto recomendado por el Agente Investigador de Producto en una investigación, junto con la evidencia que sustenta la recomendación.

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | `uuid4()` | Clave primaria. |
| `nombre_producto` | `VARCHAR(255)` | No | — | Nombre del producto candidato. |
| `categoria` | `VARCHAR(120)` | No | — | Categoría consultada en la investigación. |
| `mercado_objetivo` | `VARCHAR(2)` | No | — | Código ISO 3166-1 alpha-2 del mercado. |
| `precio_estimado_proveedor` | `NUMERIC(12,2)` | Sí | `NULL` | Precio estimado de costo (USD). |
| `precio_sugerido_venta` | `NUMERIC(12,2)` | Sí | `NULL` | Precio sugerido de venta (USD). |
| `nivel_demanda_estimado` | `VARCHAR(10)` | No | — | Uno de: `alto`, `medio`, `bajo`. |
| `nivel_competencia_estimado` | `VARCHAR(10)` | No | — | Uno de: `alto`, `medio`, `bajo`. |
| `fuentes_evidencia` | `JSONB` | No | `'[]'` | Lista de URLs o referencias que sustentan la recomendación. |
| `riesgos_identificados` | `JSONB` | No | `'[]'` | Lista de riesgos detectados por el agente. |
| `estado` | `VARCHAR(20)` | No | `'candidato'` | Uno de: `candidato`, `en_catalogo`, `descartado`. Cambia solo por acción humana (ver sección 3). |
| `investigacion_id` | `UUID` | No | — | Agrupa todos los productos devueltos por una misma ejecución del agente. No es clave foránea a otra tabla todavía (no existe tabla `investigaciones` — ver sección 4). |
| `creado_en` | `TIMESTAMP WITH TIME ZONE` | No | `now()` | Conforme a `01-Convenciones-de-Base-de-Datos.md`. |
| `actualizado_en` | `TIMESTAMP WITH TIME ZONE` | No | `now()` | Ídem. |
| `eliminado_en` | `TIMESTAMP WITH TIME ZONE` | Sí | `NULL` | Borrado lógico. Ídem. |

## Índices

* `ix_productos_candidatos_categoria` sobre `categoria`.
* `ix_productos_candidatos_investigacion_id` sobre `investigacion_id`.
* `ix_productos_candidatos_estado` sobre `estado`.

## Restricciones (`CHECK`)

* `nivel_demanda_estimado IN ('alto', 'medio', 'bajo')`.
* `nivel_competencia_estimado IN ('alto', 'medio', 'bajo')`.
* `estado IN ('candidato', 'en_catalogo', 'descartado')`.

---

# 2. Correspondencia con el Contrato del Agente

Cada columna de `productos_candidatos` corresponde directamente a un campo de la sección 3 ("Salidas") del contrato técnico del Agente Investigador de Producto:

| Campo del contrato (JSON) | Columna |
|---|---|
| `productos[].nombre_producto` | `nombre_producto` |
| `productos[].categoria` | `categoria` |
| `productos[].precio_estimado_proveedor` | `precio_estimado_proveedor` |
| `productos[].precio_sugerido_venta` | `precio_sugerido_venta` |
| `productos[].nivel_demanda_estimado` | `nivel_demanda_estimado` |
| `productos[].nivel_competencia_estimado` | `nivel_competencia_estimado` |
| `productos[].fuentes_evidencia` | `fuentes_evidencia` |
| `productos[].riesgos_identificados` | `riesgos_identificados` |
| `metadata.mercado_objetivo` | `mercado_objetivo` (se copia a cada fila) |

El campo `metadata` completo del contrato (fecha, totales evaluados/devueltos) no se persiste como columnas propias en esta tabla; se puede reconstruir agrupando por `investigacion_id`, o se registra en el log de actividad del agente (`007-Agentes/03-...`, sección 10) mientras no exista la tabla `investigaciones`.

---

# 3. Regla de Negocio: Cambios de Estado

* Toda fila nace con `estado = 'candidato'`.
* El cambio a `estado = 'en_catalogo'` requiere aprobación humana explícita, conforme a la sección 7 del contrato del agente ("Límites Explícitos"). Ningún proceso automático puede hacer ese cambio.
* El cambio a `estado = 'descartado'` puede hacerlo un humano, o un proceso automático de limpieza si el producto lleva más de un umbral de tiempo sin decisión (umbral a definir cuando exista ese proceso; no implementado todavía).
* **Mecanismo real (ver sección 5):** la aprobación humana se ejecuta vía `POST /decisiones` (`004-Backend/02-Referencia-de-Endpoints.md`, sección 6), no con un `PATCH` directo sobre `productos_candidatos`. El cambio de `estado` es un efecto secundario de registrar la decisión, no una operación independiente — así cada cambio de estado queda siempre acompañado de su motivo, contexto y evidencia.

---

# 4. Tablas `decision_records`, `decision_context`, `decision_evidence`, `decision_outcomes`

**Estado:** implementadas en código (migración `202608260001_crear_tablas_decisiones.py`), documentadas en retrospectiva en DEC-030 — el código llegó antes que esta documentación, lo cual viola la disciplina habitual del proyecto y quedó registrado explícitamente como tal en esa decisión.

Registran las decisiones humanas sobre entidades del sistema (hoy, en la práctica, solo sobre `productos_candidatos`, vía `entity_type = 'product_candidate'`).

| Tabla | Propósito |
|---|---|
| `decision_records` | El registro central: qué se decidió (`action`: `approve` / `discard` / `request_review`), sobre qué entidad (`entity_type` + `entity_id`), quién y por qué (`user_id`, `reason`). |
| `decision_context` | La "foto" de los datos disponibles al momento de decidir (`context_data`, JSONB de formato libre) — se guarda aparte porque los datos del producto pueden cambiar después. Relación 1:1 con `decision_records`. |
| `decision_evidence` | Las fuentes que respaldaron la decisión (`source_type`, `source_url`, `source_title`, `evidence`). Relación 1:N con `decision_records` — una decisión puede tener varias evidencias. |
| `decision_outcomes` | El resultado real, medido después (`outcome_type`, `outcome_data`, `measured_at`). Pensada para que un futuro agente de automatización pueda aprender qué decisiones funcionaron. **Sin endpoint todavía** — la tabla existe mediante migración pero nada la escribe ni la lee hoy; queda fuera de esta versión del feature. |

Las cuatro heredan las columnas estándar (`id`, `creado_en`, `actualizado_en`, `eliminado_en`) de `01-Convenciones-de-Base-de-Datos.md`. `entity_id` en `decision_records` no es clave foránea real, a propósito: `entity_type` puede apuntar a distintas tablas en el futuro, no solo a `productos_candidatos`.

**Restricción (`CHECK`):** `decision_records.action IN ('approve', 'discard', 'request_review')`.

**Bug corregido en DEC-030:** el modelo SQLAlchemy (`backend/app/models/decisiones.py`) inicialmente no declaraba las relaciones ORM entre `DecisionRecord` y `DecisionContext`/`DecisionEvidence`. Los datos sí se guardaban bien en sus tablas, pero la API siempre devolvía `context_data: null` y `evidencias: []`, sin ningún error visible — la información quedaba persistida pero invisible. Corregido agregando las relaciones (`relationship()`) y cargándolas explícitamente (`selectinload`) al leer.

---

# 5. Fuera de Alcance de Este Esquema (por ahora)

No se crean todavía, por no tener un agente o proceso concreto que las necesite hoy (Principio Rector de este volumen):

* `investigaciones` (metadatos de cada ejecución del agente, independiente de sus productos).
* Cualquier tabla para SEO, contenido, publicidad o automatización — corresponden a agentes sin contrato técnico aprobado todavía.
* Uso real de `decision_outcomes` (existe la tabla, pero ningún endpoint la usa — ver sección 4).
* Columnas de embeddings (`vector`, pgvector) — se agregan cuando exista un caso de uso real de búsqueda semántica sobre productos (ej. deduplicación de candidatos similares), no antes.

---

# Resumen Ejecutivo para IA

El esquema real de la base de datos hoy tiene dos grupos de tablas: `productos_candidatos` (resultados del Agente Investigador de Producto) y el grupo de decisiones humanas (`decision_records`, `decision_context`, `decision_evidence`, `decision_outcomes` — esta última sin uso todavía), que registra por qué un humano aprobó o descartó un producto candidato y ejecuta ese cambio de `estado` como efecto secundario, vía `POST /decisiones`. Todas usan UUID como clave primaria, timestamps estándar y borrado lógico. `productos_candidatos.estado` solo puede pasar a `en_catalogo` mediante ese mecanismo de aprobación humana. No existen todavía tablas para otros agentes ni columnas de embeddings; se agregan solo cuando haya un caso de uso concreto que las necesite.
