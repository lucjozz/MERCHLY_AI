# 01-Convenciones-de-Base-de-Datos.md

---

title: Convenciones de Base de Datos
document: 006-01
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-07-27
next_review: 2027-01-27
related:

* ../001-Arquitectura/04-Arquitectura-de-Datos.md
* ../002-CTO/03-Stack-Tecnologico.md
* ../002-CTO/05-Estandares-Codigo.md
* ../000-Constitucion/08-Normas-de-Ingenieria.md

---

# Convenciones de Base de Datos

## Propósito

Fijar las reglas de diseño que debe cumplir toda tabla nueva en PostgreSQL, para que el esquema crezca de forma predecible a medida que se agregan agentes y funcionalidades (Fases 2 en adelante), sin que cada tabla nueva reinvente sus propias convenciones.

---

# 1. Nombres

* **Tablas:** `snake_case`, en plural, en español (coherente con DEC-004: español como idioma oficial del proyecto). Ejemplo: `productos_candidatos`, no `ProductCandidates` ni `producto_candidato`.
* **Columnas:** `snake_case`, en español. Ejemplo: `precio_estimado_proveedor`, no `estimatedSupplierPrice`.
* **Claves foráneas:** `<tabla_singular>_id`. Ejemplo: `producto_candidato_id`.
* **Índices:** `ix_<tabla>_<columna(s)>`. Ejemplo: `ix_productos_candidatos_categoria`.
* **Migraciones (Alembic):** nombre de archivo autogenerado por Alembic (hash + slug descriptivo en español), nunca renombrado a mano.

## Excepción admitida

Los campos que replican literalmente un identificador externo (ej. un ID de proveedor de una API de terceros) pueden conservar el nombre original de esa fuente si renombrarlo agrega confusión. Esta excepción debe justificarse en un comentario en el modelo SQLAlchemy correspondiente.

---

# 2. Claves Primarias

* Toda tabla usa `UUID` como clave primaria (`id`), generado en la aplicación (no autoincremental), vía `uuid4()`.
* Motivo: evita colisiones si en el futuro (Fase 7, apertura a terceros bajo Opción C del modelo de negocio) hace falta fusionar datos de distintos orígenes, y no revela volumen de registros como sí lo hace un ID secuencial.

---

# 3. Timestamps Obligatorios

Toda tabla incluye, como mínimo:

* `creado_en` (`TIMESTAMP WITH TIME ZONE`, no nulo, default `now()`).
* `actualizado_en` (`TIMESTAMP WITH TIME ZONE`, no nulo, se actualiza automáticamente en cada `UPDATE`).

Ninguna tabla implementa borrado físico por defecto: se usa `eliminado_en` (`TIMESTAMP WITH TIME ZONE`, nulo por defecto) para borrado lógico, salvo que un documento de esquema justifique explícitamente lo contrario (ej. datos que por ley o por costo de almacenamiento deben eliminarse físicamente).

---

# 4. Tipos de Datos

* Dinero: `NUMERIC(12, 2)`, nunca `FLOAT` (evita errores de redondeo en cálculos financieros).
* Texto corto (nombres, categorías): `VARCHAR` con longitud explícita cuando se conoce un límite razonable; `TEXT` cuando no.
* Texto largo o estructurado sin necesidad de consultarlo por campo interno: `JSONB`, no `TEXT` con JSON serializado a mano.
* Vectores de embeddings: tipo `vector` de la extensión `pgvector`, con la dimensión fija según el modelo de embeddings usado (se documenta en el esquema específico que lo use).

---

# 5. Extensión pgvector

* La extensión `pgvector` se habilita una sola vez por base de datos (`CREATE EXTENSION IF NOT EXISTS vector;`), en la primera migración que la necesite — no en todas.
* Toda columna de tipo `vector` documenta en el esquema (`02-Esquema-Fase1.md` o el que corresponda) qué modelo de embeddings la generó y su dimensión, porque cambiar de modelo casi siempre implica una migración de datos, no solo de esquema.

---

# 6. Multi-tenancy

Conforme a DEC-014 (Opción C — Híbrido), el esquema **no** incluye una columna `tenant_id` ni particionamiento por cliente mientras el sistema opere solo tiendas propias (Fases 0-6). Si en Fase 7 se aprueba abrir AICOS a terceros, esa columna se agrega entonces, vía migración, no se diseña preventivamente hoy.

---

# 7. Relación con el Modelo SQLAlchemy

Cada tabla documentada en este volumen tiene una clase equivalente en `backend/app/models/`, con el mismo nombre de tabla (`__tablename__`) y las mismas columnas descritas aquí. El documento de esquema (`02-Esquema-Fase1.md`) es la fuente de verdad conceptual; el modelo en código es su implementación. Si difieren, se corrige el código para que coincida con el documento — el esquema no se decide primero en código y se documenta después (coherente con el principio "documentación antes que código" de `002-CTO/02-Metodologia-Desarrollo.md`).

---

# Resumen Ejecutivo para IA

Toda tabla nueva en PostgreSQL usa: nombres en `snake_case` y en español, clave primaria `UUID`, timestamps `creado_en`/`actualizado_en`/`eliminado_en` (borrado lógico por defecto), `NUMERIC` para dinero, `JSONB` para datos semi-estructurados y `vector` (pgvector) para embeddings. No se agrega `tenant_id` hasta que exista una decisión explícita de abrir la plataforma a terceros (Fase 7). El documento de esquema es la fuente de verdad; el código SQLAlchemy la implementa, nunca al revés.
