# 04-Politica-de-Backups-y-Retencion.md

---

title: Política de Backups y Retención de Datos
document: 006-04
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-07-27
next_review: 2027-01-27
related:

* 02-Esquema-Fase1.md
* ../000-Constitucion/11-Seguridad.md
* ../000-Constitucion/12-Escalabilidad.md

---

# Política de Backups y Retención de Datos

## Propósito

Definir cada cuánto se respalda la base de datos, dónde se conserva y por cuánto tiempo, de forma proporcional al estado actual del proyecto (Fase 1, sin datos de producción todavía) y escalable a medida que AICOS opera tiendas reales.

---

# 1. Estado Actual (Fase 1 — entorno local)

Mientras la única base de datos existente es la de desarrollo local (contenedor `db` en `docker-compose.yml`, volumen `merchly_pgdata`):

* No se requiere backup automatizado — los datos son descartables y reproducibles (no hay datos de clientes ni de negocio reales).
* El volumen Docker persiste entre reinicios del contenedor, pero no está pensado como respaldo — `docker compose down -v` lo elimina intencionalmente.

Esta sección se reemplaza en cuanto exista un entorno de staging o producción real (Fase 2 en adelante).

---

# 2. Política a Partir de Producción (Fase 2+)

Se define ahora para no tener que improvisarla bajo presión el día que haya datos reales:

## 2.1 Frecuencia

* Backup completo diario.
* Backup incremental (WAL) continuo, si el proveedor de hosting elegido lo soporta (a definir en `002-CTO/03-Stack-Tecnologico.md` cuando se elija hosting de producción).

## 2.2 Retención

| Tipo de dato | Retención mínima |
|---|---|
| Backups diarios completos | 30 días |
| Backups semanales | 12 semanas |
| Backups mensuales | 12 meses |

## 2.3 Ubicación

* Los backups se almacenan en un proveedor distinto o, como mínimo, en una región distinta a la de la base de datos activa, para no perder ambos ante un mismo incidente.
* Nunca se almacenan backups en el mismo repositorio de código (coherente con `000-Constitucion/11-Seguridad.md`, Norma 11: nunca versionar datos sensibles).

## 2.4 Verificación

* Se ejecuta una restauración de prueba (a un entorno aislado, no productivo) al menos una vez por trimestre, para confirmar que los backups son realmente restaurables y no solo existen.

---

# 3. Retención de Datos por Categoría (Borrado Lógico)

Conforme a `01-Convenciones-de-Base-de-Datos.md`, toda tabla usa borrado lógico (`eliminado_en`) por defecto. Reglas de retención antes del borrado físico definitivo:

* **`productos_candidatos` con `estado = 'descartado'`:** se conservan mínimo 90 días antes de considerar borrado físico, para permitir auditoría de por qué se descartó un producto.
* **Datos históricos de decisiones y aprendizajes** (conforme a `001-Arquitectura/04-Arquitectura-de-Datos.md`, categoría "Datos Históricos"): no se borran físicamente salvo requerimiento legal explícito — son la base del aprendizaje continuo del sistema.

---

# 4. Relación con Seguridad

Esta política complementa, no reemplaza, lo ya definido en `000-Constitucion/11-Seguridad.md`. Cualquier backup que contenga datos personales de clientes (cuando existan) debe cumplir además las normas de protección de datos aplicables al mercado donde opere esa tienda — esto se detalla en `013-Seguridad` cuando ese volumen se desarrolle.

---

# Resumen Ejecutivo para IA

Mientras el proyecto está en Fase 1 (solo entorno local, sin datos reales), no hace falta backup automatizado. A partir de que exista producción (Fase 2+), se aplica: backup diario completo + WAL continuo, retención de 30 días/12 semanas/12 meses, almacenamiento en ubicación distinta a la base activa, y prueba de restauración trimestral. Todas las tablas usan borrado lógico por defecto antes de cualquier borrado físico.
