# 03-Alcance-y-Plan-de-Migracion.md

---

title: Alcance de Protección y Plan de Migración
document: 013-03
version: 0.1.0
status: Draft — pendiente de aprobación
owner: CTO
last_updated: 2026-09-02
next_review: al aprobarse, o 2027-03-02
related:

* README.md
* 01-Modelo-de-Usuarios-y-Autenticacion.md
* 02-Roles-y-Permisos.md
* ../004-Backend/02-Referencia-de-Endpoints.md
* ../memory/DECISIONS.md

---

# Alcance de Protección y Plan de Migración

## Propósito

Fijar exactamente qué endpoints pasan a requerir autenticación y cuáles quedan públicos, y cómo se migra `POST /decisiones` (que hoy acepta `user_id` como texto libre) sin dejar el sistema en un estado roto a mitad de camino.

---

# 1. Endpoints Protegidos (requieren JWT válido)

| Endpoint | Rol mínimo requerido |
|---|---|
| `POST /agentes/investigador-producto` | `responsable_negocio` (o superior — ver matriz en `02-...`) |
| `POST /agentes/analitica-basica` | `usuario_operativo` (o superior) |
| `POST /agentes/marketing` | `responsable_negocio` (o superior) |
| `POST /decisiones` | `responsable_negocio` (o superior) |

**Criterio de alcance:** se protegen los 4 endpoints que ejecutan una acción (llaman a un proveedor de IA, o registran una decisión con efecto real), tal como decidió el CTO — no solo los que persisten datos en la base. Es una definición deliberadamente más amplia que "solo lo que escribe en la base de datos", porque ejecutar un agente ya tiene costo (de proveedor de IA) o consecuencia (una decisión registrada) aunque no siempre persista.

---

# 2. Endpoints Públicos (sin cambios)

| Endpoint | Motivo |
|---|---|
| `GET /health` | Liveness check — lo consultan orquestadores (Docker, futuros balanceadores), no personas. Exigir JWT ahí rompe el healthcheck. |
| `GET /health/ready` | Mismo motivo. |
| `GET /decisiones/{id}` | Solo lectura, sin dato sensible más allá de lo que ya expone `POST /decisiones` a quien lo creó. Se puede reevaluar más adelante si `reason` o `context_data` empiezan a contener información sensible. |
| `GET /productos-candidatos` | Solo lectura. |
| `GET /productos-candidatos/{id}` | Solo lectura. |
| `POST /auth/login` | No puede requerir JWT — es el endpoint que lo emite. |

**Nota explícita:** dejar estos endpoints de lectura sin autenticación es una decisión de alcance para esta versión, no un descuido — quedó fuera cuando el CTO eligió "todos los que escriben" en vez de "todos, incluidos los de solo lectura". Se revisa si en el futuro hay datos de negocio sensibles en las lecturas (ej. reason de una decisión que mencione cifras internas).

---

# 3. Migración de `POST /decisiones`

## 3.1 Estado actual (antes de este volumen)

`DecisionInput.user_id` es un `string` de texto libre en el body del request (`backend/app/schemas/decisiones.py`). Cualquiera puede escribir cualquier nombre ahí.

## 3.2 Estado objetivo

`user_id` deja de venir en el body. Se obtiene del JWT (`claims.sub`, ver `01-...` sección 3.2) a través de una dependencia de FastAPI (`Depends(usuario_actual)`) que:

1. Valida el token (firma, expiración).
2. Busca el usuario en la base por `sub` y confirma que `activo = true`.
3. Confirma que su `rol` está en la lista de roles permitidos para ese endpoint (`02-...`, sección 2).
4. Inyecta el usuario autenticado en el handler del endpoint.

`registrar_decision` (el servicio) pasa a recibir el `user_id` como parámetro separado (ya viene del JWT, no del `DecisionInput`), en vez de leerlo de `entrada.user_id`.

## 3.3 Compatibilidad hacia atrás

**No se mantiene compatibilidad.** `DecisionInput.user_id` se elimina del schema en el mismo cambio que agrega la autenticación — no tiene sentido un período de transición donde `user_id` sea opcional y a veces venga del body y a veces del token, porque reintroduce exactamente el problema que este volumen resuelve (alguien podría declararse `user_id` distinto al que realmente autenticó). Esto es una ruptura de compatibilidad consciente: cualquier request a `POST /decisiones` hecho hoy (sin token) deja de funcionar el día que esto se implemente.

**Implicación práctica:** como hoy el único usuario del sistema es Lucas y lo usa manualmente (no hay integraciones externas llamando a este endpoint todavía, según `memory/CURRENT_STATE.md`), el costo de esta ruptura es bajo. Si en el futuro hay clientes automatizados llamando a estos endpoints, ese costo cambia — pero no es el caso hoy.

## 3.4 Orden de implementación (para cuando se apruebe este volumen)

1. Tabla `usuarios` + migración Alembic.
2. Script de seed para crear el usuario `admin_principal` inicial (Lucas).
3. `POST /auth/login` + `GET /auth/me`.
4. Dependencia `usuario_actual` (valida JWT + rol).
5. Aplicar la dependencia a los 4 endpoints de la sección 1, en el mismo cambio que se quita `user_id` de `DecisionInput`.
6. Actualizar `004-Backend/02-Referencia-de-Endpoints.md` (marcar qué requiere auth, agregar `/auth/*`).
7. Tests: login válido/inválido, endpoint protegido sin token (401), con token pero rol insuficiente (403), con token y rol correcto (200/201).

No se implementa nada de esto hasta que el CTO apruebe explícitamente este volumen completo (ver `README.md`, "Estado de Aprobación").

---

# Resumen Ejecutivo para IA

4 endpoints pasan a requerir JWT (`investigador-producto`, `analitica-basica`, `marketing`, `decisiones`); los de solo lectura y los health checks quedan públicos. `POST /decisiones` pierde `user_id` del body — pasa a tomarlo del token, sin período de transición ni compatibilidad hacia atrás, porque mantenerla reintroduciría el problema que se está resolviendo. La implementación sigue un orden fijo (tabla → seed → login → dependencia → aplicar a endpoints → docs → tests) y no arranca hasta aprobación explícita del CTO.
