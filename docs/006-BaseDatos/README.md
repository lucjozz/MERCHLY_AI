# Volumen 006 - Base de Datos

> **Versión:** 0.1 Alpha
> **Estado:** Activo
> **Propietario:** CTO
> **Última actualización:** 2026-07-27

---

## Propósito

Este volumen define el **diseño técnico e implementable** de la base de datos de AICOS: convenciones de nombres, el esquema concreto de tablas, la estrategia de migraciones y la política de backups.

Ya existe `001-Arquitectura/04-Arquitectura-de-Datos.md`, que **no** duplica: ese documento responde **qué tipos de datos existen conceptualmente** (estratégicos, operativos, comerciales, técnicos, históricos) y cómo se relacionan con la memoria de los agentes IA. `006-BaseDatos` responde una pregunta distinta y más concreta: **¿qué tablas existen hoy, con qué columnas exactas, y cómo se crean y mantienen en PostgreSQL?**

Es el mismo tipo de relación que existe entre `001-Arquitectura/03-Arquitectura-de-Agentes.md` (conceptual) y `007-Agentes` (contrato técnico implementable).

---

## Objetivos

- Fijar convenciones de nombres y tipos de datos, para que el esquema crezca de forma consistente.
- Documentar el esquema real de tablas, empezando por lo mínimo necesario para el primer agente (Investigador de Producto) — no se diseñan tablas especulativas para funcionalidad que todavía no existe (Principio de Simplicidad, Norma 4).
- Definir cómo se versionan los cambios de esquema (migraciones), para que nunca se modifique una tabla en producción a mano.
- Definir una política mínima de backups y retención, coherente con `000-Constitucion/11-Seguridad.md`.

---

## Estructura

| Archivo | Descripción |
|---|---|
| 01-Convenciones-de-Base-de-Datos.md | Reglas de nombres, tipos, claves, timestamps y extensiones (pgvector) que aplican a toda tabla nueva. |
| 02-Esquema-Fase1.md | El esquema real y actual: hoy, una sola tabla (`productos_candidatos`), la que necesita el Agente Investigador de Producto. |
| 03-Estrategia-de-Migraciones.md | Cómo se versiona el esquema con Alembic; qué se permite y qué no. |
| 04-Politica-de-Backups-y-Retencion.md | Cada cuánto se respalda la base, dónde, y cuánto tiempo se conserva cada tipo de dato. |

---

## Relación con otros volúmenes

- `001-Arquitectura/04-Arquitectura-de-Datos.md`: diseño conceptual que este volumen aterriza en tablas reales.
- `002-CTO/03-Stack-Tecnologico.md`: fija PostgreSQL + pgvector como motor; este volumen no vuelve a discutir esa elección, la da por sentada.
- `007-Agentes/03-Agente-Investigador-de-Producto.md`: el contrato técnico del agente exige persistencia de resultados (sección 3, "Destino"); `02-Esquema-Fase1.md` es la implementación concreta de ese requisito.
- `backend/app/models/`: el código SQLAlchemy que implementa el esquema descrito aquí.
- `backend/alembic/`: las migraciones versionadas que crean y modifican estas tablas.

## Principio Rector

> **Ninguna tabla se crea "por si acaso". Cada tabla en `02-Esquema-Fase1.md` existe porque un agente o proceso concreto, ya especificado, la necesita hoy.**
