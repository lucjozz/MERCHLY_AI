# 04-Endurecimiento-para-Lanzamiento.md

---

title: Endurecimiento de Seguridad para el Lanzamiento
document: 013-04
version: 0.1.0
status: Aprobado por Daniel (admin_principal) — pendiente visto bueno del CTO
owner: CTO
last_updated: 2026-11-23
related:

* README.md
* 01-Modelo-de-Usuarios-y-Autenticacion.md
* 02-Roles-y-Permisos.md
* 03-Alcance-y-Plan-de-Migracion.md
* ../006-BaseDatos/02-Esquema-Fase1.md
* ../../memory/DECISIONS.md (DEC-032)

---

# Endurecimiento de Seguridad para el Lanzamiento

## Propósito

Los documentos 013-01 a 013-03 diseñaron la **base** de seguridad (usuarios, JWT, roles) para un sistema que corría solo en una PC. Este documento define lo necesario para **lanzar MERCHLY AI como servicio real**, con varios negocios (clientes) usando la misma instalación. Reemplaza varias decisiones de 013-01/03 que dejan de ser válidas (ver sección 1).

Se basa en una auditoría real hecha el 2026-11-22 (37 pruebas black-box contra el backend local, gitleaks sobre 276 commits, pip-audit, npm audit y nmap), cuyo resultado fue **12 OK / 25 fallas** y ninguna fuga de secretos en el historial.

---

# 1. Decisiones de 013-01/03 que cambian

| Antes (013-01/03) | Ahora (este documento) | Motivo |
|---|---|---|
| Sin refresh token, JWT de 8 h | Access token de 15 min + refresh token rotativo (cookie HttpOnly, guardado hasheado, detección de reutilización) | Un token robado sirve 15 min, no 8-24 h |
| GET de productos y decisiones públicos | **Todo** exige autenticación salvo `/health*` y `/auth/login` (y `/auth/google`) | La auditoría leyó datos sin login |
| Sin auto-registro | Auto-registro con **Google** (crea la organización y su admin) | Lanzamiento comercial |
| Una sola "bolsa" de datos | **Multi-tenancy**: cada negocio es una `organizacion` aislada por RLS | Un cliente no puede ver a otro |
| DELETE físico de productos | **Borrado lógico** (`eliminado_en`) | Convención de 006-BaseDatos; no dejar decisiones huérfanas |
| Decisiones re-editables sin regla | Máquina de estados con estados finales inmutables + bloqueo de fila | Doble aprobación/descarte pisaba la anterior |
| python-jose | PyJWT | python-jose tiene CVEs sin corrección |

---

# 2. Multi-tenancy (organizaciones)

## 2.1 Modelo

* Tabla nueva `organizaciones` (id, nombre, activo, timestamps estándar).
* **Un usuario pertenece a una sola organización** (`usuarios.organizacion_id`, NOT NULL, FK). El email sigue siendo único global.
* Los **roles son por organización**: el `admin_principal` de la organización A no tiene poder en la B.
* Columna `organizacion_id` (NOT NULL, FK, indexada) en: `productos_candidatos`, `decision_records`, `decision_context`, `decision_evidence`, `decision_outcomes`.
* Backfill: los datos existentes pasan a la organización inicial **"MERCHLY (organización inicial)"**, cuyo admin es Daniel.
* Al registrarse con Google un usuario nuevo, se crea su organización y él queda como `admin_principal` de ella.

## 2.2 Aislamiento en dos capas (defensa en profundidad)

1. **Aplicación:** cada servicio recibe `organizacion_id` del usuario autenticado y filtra explícitamente. El `organizacion_id` **nunca** viene del cliente.
2. **Base de datos (Row-Level Security):** `ENABLE` + `FORCE ROW LEVEL SECURITY` en las 5 tablas con datos de negocio, con la política:

   `organizacion_id = NULLIF(current_setting('app.organizacion_id', true), '')::uuid`

   (tanto `USING` como `WITH CHECK`). Si la app olvida filtrar, la base no devuelve ni acepta filas de otra organización. Sin organización fijada, no se ve **nada**.

* La organización se fija **por transacción** con `set_config('app.organizacion_id', <uuid>, true)` (equivalente a `SET LOCAL`), aplicado automáticamente al inicio de cada transacción de la sesión del request (evento `after_begin` de SQLAlchemy). Nunca `SET` de sesión: el pool de conexiones la filtraría a otro request.
* `usuarios` y `organizaciones` **no** tienen RLS (el login necesita buscar por email antes de saber la organización); la app filtra por organización y ningún endpoint lista usuarios salvo a un admin de su propia organización.

## 2.3 Roles de base de datos

| Rol | Uso | Privilegios |
|---|---|---|
| `merchly` (POSTGRES_USER) | Solo migraciones y administración | Dueño de las tablas, superusuario. **La app ya no se conecta con él.** Contraseña fuerte, no `merchly`. |
| `merchly_app` | La aplicación (backend) | `NOSUPERUSER NOBYPASSRLS`, no es dueño de nada. `SELECT, INSERT, UPDATE` en `productos_candidatos`, `usuarios`, `organizaciones`, `refresh_tokens`; **solo `SELECT, INSERT`** en `decision_*` (decisiones append-only); sin `DELETE` en ninguna tabla. |

Alembic se conecta con `DATABASE_URL_MIGRACIONES` (rol `merchly`); el backend con `DATABASE_URL` (rol `merchly_app`).

## 2.4 IDOR

Un recurso de otra organización responde **404** (igual que si no existiera), nunca 403, para no confirmar su existencia.

---

# 3. Autenticación y sesiones

* **PyJWT**, `algorithms=["HS256"]` fijo. Claims obligatorios: `sub` (UUID validado), `org`, `rol`, `iat`, `exp`, `jti`, `iss="merchly-ai"`, `aud="merchly-api"`, `typ="access"`. Leeway 10 s.
* El rol, el estado `activo` y la organización se **releen de la base en cada request** (se mantiene).
* `token_version` por usuario: cambiar la contraseña o forzar el cierre invalida todos sus tokens.
* `POST /auth/logout`: el `jti` del access token va a una denylist en Redis con TTL igual al tiempo que le queda; el refresh token se revoca.
* **Refresh tokens:** opacos (`secrets.token_urlsafe(48)`), guardados como SHA-256 en la tabla `refresh_tokens` (familia, expiración 14 días, revocado). Cada uso rota el token; reutilizar uno ya rotado revoca toda la familia (detección de robo).
* **Cookies vía BFF:** el navegador nunca ve los tokens. El login pasa por un Route Handler de Next que guarda access y refresh en cookies `HttpOnly; Secure (en producción); SameSite=Lax; Path=/`. Los componentes llaman a rutas de Next que reenvían al backend con el token. Protección CSRF: SameSite + verificación de `Origin` en las rutas que mutan.
* **Secreto JWT:** el backend **no arranca** si `JWT_SECRET_KEY` tiene menos de 32 caracteres o es el valor de ejemplo. Se genera con `secrets.token_urlsafe(64)`.
* Respuestas de `/auth/*` con `Cache-Control: no-store`.
* Sin header `Authorization` → **401** (antes 403).

## 3.1 Login con Google (auto-registro)

* El frontend obtiene un ID token de Google (Google Identity Services) y lo manda a `POST /auth/google`.
* El backend verifica firma (JWKS de Google), `aud = GOOGLE_CLIENT_ID`, `iss` de Google, `exp` y `email_verified = true`.
* Si el `sub` de Google ya está vinculado → login. Si el email existe sin vincular → se vincula. Si no existe → se crea organización + usuario `admin_principal`.
* Sin `GOOGLE_CLIENT_ID` configurado, el endpoint responde 503 (deshabilitado).
* `usuarios.password_hash` pasa a ser opcional (usuarios solo-Google); columna `google_sub` única.

## 3.2 Contraseñas

* Mínimo 12 caracteres al crear/cambiar; máximo 72 **bytes** (límite de bcrypt). En login, cualquier contraseña de más de 128 caracteres → 422 sin procesar (anti-DoS).
* Tiempo constante: si el email no existe se verifica contra un hash señuelo.
* Emails normalizados a minúsculas (con `CHECK (email = lower(email))`).
* El seed usa `getpass` y tiene modo `--rotar`.

---

# 4. Límites de uso (rate limiting)

* Login: 5 fallos por (email, IP) y 20 por IP en 15 minutos → **429** con `Retry-After`. Un login correcto limpia el contador de ese email+IP. **Fail-closed**: si Redis cae, el login responde 503.
* Agentes: cuota por organización (Investigador 30/hora, Marketing 60/hora) → 429. **Fail-open** si Redis cae (se loguea).
* Claves en Redis con hash SHA-256 de `email|ip`; `SET clave 0 EX ventana NX` + `INCR` (TTL atómico).
* La IP del cliente sale de la conexión; `X-Forwarded-For`/`CF-Connecting-IP` solo se aceptan cuando `CONFIAR_PROXY=true` (una vez que el origen esté cerrado detrás de Cloudflare).

---

# 5. Validación de entradas y salidas

* `extra="forbid"` en **todos** los schemas de entrada (un `rol`, `estado`, `user_id` u `organizacion_id` en el body → 422).
* `max_length` alineado con las columnas; listas con tope; `context_data` ≤ 16 KB serializado; paginación `pagina ≥ 1`, `1 ≤ tamano_pagina ≤ 100`.
* Body de más de 1 MB → 413.
* Los 422 **no** devuelven el valor enviado (`input`) ni el contexto interno.
* 500 genérico con `request_id`; el detalle solo va al log. Nunca se loguean tokens, contraseñas ni el header `Authorization`.
* Listados con schema resumido; `DecisionOutput` no expone datos de otros usuarios.

---

# 6. Decisiones de negocio

## 6.1 Máquina de estados de un producto

```
candidato ──approve──► en_catalogo   (final)
candidato ──discard──► descartado    (final)
candidato ──request_review──► en_revision
en_revision ──approve──► en_catalogo (final)
en_revision ──discard──► descartado  (final)
```

Cualquier otra transición → **409 Conflict** y no se registra la decisión. La fila del producto se bloquea con `SELECT ... FOR UPDATE` durante la decisión, de modo que dos envíos simultáneos no pueden decidir los dos.

## 6.2 Borrado

* Borrado **lógico** (`eliminado_en = now()`); todas las consultas filtran `eliminado_en IS NULL`.
* Pueden borrar: `admin_principal` y `responsable_negocio` (el dueño del negocio) **de la misma organización**.

## 6.3 Matriz actualizada

| Endpoint | admin_principal | responsable_tecnico | responsable_negocio | usuario_operativo |
|---|---|---|---|---|
| GET productos / decisiones | ✅ | ✅ | ✅ | ✅ |
| POST investigador, marketing, decisiones | ✅ | ✅ | ✅ | ❌ |
| POST analítica | ✅ | ✅ | ✅ | ✅ |
| DELETE producto | ✅ | ❌ | ✅ | ❌ |

Todo limitado a la organización del usuario.

---

# 7. Infraestructura local (Docker)

* Postgres y Redis **sin puertos publicados** hacia afuera: solo en `127.0.0.1` (para Alembic/scripts desde la PC). El backend en `127.0.0.1:8000`.
* Contraseñas fuertes en un `.env` raíz (fuera de git): `POSTGRES_PASSWORD`, `DB_APP_PASSWORD`, `REDIS_PASSWORD` (Redis con `requirepass`).
* Dockerfile multi-etapa, usuario no-root, sin compiladores en la imagen final, `uvicorn --no-server-header`, `.dockerignore`.
* `cap_drop: ALL`, `no-new-privileges`, `read_only` con `tmpfs`, límites de memoria/CPU/pids.

---

# 8. Headers y CORS

* `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` restrictiva, `Cross-Origin-Opener-Policy: same-origin`, `Strict-Transport-Security` (solo con HTTPS en producción).
* `/docs`, `/redoc` y `/openapi.json` ocultos salvo `EXPONER_DOCS=true`.
* CORS: orígenes desde `CORS_ORIGENES` (lista explícita, nunca `*`), métodos y headers explícitos, `expose_headers: Retry-After`.

---

# 9. Procedimiento ante fuga de un secreto

1. **Rotar primero** (generar uno nuevo con `secrets.token_urlsafe(64)` y reemplazarlo en el hosting/`.env`); borrarlo del repo no alcanza porque queda en el historial.
2. Revocar en el proveedor (Google AI Studio, OpenAI, GitHub).
3. Si fue `JWT_SECRET_KEY`: rotarlo invalida todas las sesiones (es lo deseado).
4. Revisar logs de uso del proveedor durante la ventana de exposición.
5. Registrar el incidente en `docs/015-Bitacora`.
6. Prevención: hook `pre-commit` con gitleaks + GitHub secret scanning y push protection.

---

# 10. Fuera de alcance de este documento

Cloudflare/WAF, HTTPS y dominio, backups externos, monitoreo con alertas, subida de archivos y pagos: dependen de elegir hosting y se documentan cuando existan (Fases 2 y 3).
