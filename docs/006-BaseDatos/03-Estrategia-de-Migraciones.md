# 03-Estrategia-de-Migraciones.md

---

title: Estrategia de Migraciones de Base de Datos
document: 006-03
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-07-27
next_review: 2027-01-27
related:

* 01-Convenciones-de-Base-de-Datos.md
* 02-Esquema-Fase1.md
* ../002-CTO/04-Flujo-Git-CICD.md

---

# Estrategia de Migraciones de Base de Datos

## Propósito

Definir cómo se crea, versiona y aplica cualquier cambio de esquema en PostgreSQL, para que la base de datos nunca se modifique a mano ni diverja entre el entorno local, staging y producción.

---

# 1. Herramienta

Se usa **Alembic**, integrado con SQLAlchemy (`backend/requirements.txt`), coherente con el stack ya definido en `002-CTO/03-Stack-Tecnologico.md`.

---

# 2. Regla Fundamental

**Ningún cambio de esquema se aplica directamente en una base de datos (ni siquiera local) sin pasar antes por una migración versionada en `backend/alembic/versions/`.**

Esto incluye: crear tablas, agregar columnas, cambiar tipos, agregar índices o restricciones, y habilitar extensiones (`CREATE EXTENSION`). Ejecutar SQL manual contra la base para "probar algo rápido" está permitido solo en una base local descartable, nunca en una que se vaya a conservar.

---

# 3. Flujo de Trabajo

1. Se actualiza el documento de esquema correspondiente en `006-BaseDatos` (ej. `02-Esquema-Fase1.md`) **antes** de tocar código, conforme al principio "documentación antes que código".
2. Se actualiza o crea el modelo SQLAlchemy en `backend/app/models/` para que coincida con el documento.
3. Se genera la migración automáticamente: `alembic revision --autogenerate -m "descripcion_en_español"`.
4. Se revisa manualmente el archivo generado — Alembic no siempre detecta correctamente cambios de tipo o restricciones `CHECK`; el autogenerado es un punto de partida, no el resultado final.
5. Se aplica localmente: `alembic upgrade head`, y se verifica contra el esquema documentado.
6. Se hace commit de la migración junto con el modelo y el documento de esquema, en el mismo cambio (conforme a Conventional Commits, DEC-010).

---

# 4. Entornos

* **Local:** cada desarrollador aplica migraciones manualmente con `alembic upgrade head` después de bajar cambios nuevos.
* **CI/CD (GitHub Actions):** corre `alembic upgrade head` contra una base de datos efímera como parte de las pruebas, para detectar migraciones rotas antes de fusionar (a implementar cuando exista el pipeline de CI descrito en `002-CTO/04-Flujo-Git-CICD.md`).
* **Staging/Producción:** las migraciones se aplican como paso explícito de despliegue, nunca automáticamente al arrancar la aplicación — un cambio de esquema fallido no debe impedir que el backend levante con el esquema anterior.

---

# 5. Reglas Adicionales

* Toda migración debe ser reversible (`downgrade()` implementado), salvo que el propio cambio sea irreversible por naturaleza (ej. borrado físico de una columna con datos) — en ese caso, se documenta explícitamente por qué en el docstring de la migración.
* No se editan migraciones ya aplicadas en un entorno compartido (staging o producción). Un error se corrige con una migración nueva, no reescribiendo la anterior.
* Las migraciones nunca contienen lógica de negocio (ej. no se usa una migración para "arreglar" datos según una regla de negocio específica); eso corresponde a un script separado, documentado aparte.

---

# 6. Estado Actual

Todavía no existe ninguna migración aplicada — `006-BaseDatos` recién define el primer esquema (`02-Esquema-Fase1.md`, tabla `productos_candidatos`). La primera migración de este proyecto corresponde a esa tabla.

---

# Resumen Ejecutivo para IA

Todo cambio de esquema en PostgreSQL pasa por: actualizar el documento de esquema → actualizar el modelo SQLAlchemy → generar una migración con Alembic → revisarla manualmente → aplicarla localmente → commitear todo junto. Nunca se modifica el esquema a mano, nunca se edita una migración ya aplicada en un entorno compartido, y las migraciones no contienen lógica de negocio.
