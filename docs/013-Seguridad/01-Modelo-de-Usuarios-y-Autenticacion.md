# 01-Modelo-de-Usuarios-y-Autenticacion.md

---

title: Modelo de Usuarios y Autenticación
document: 013-01
version: 0.1.0
status: Draft — pendiente de aprobación
owner: CTO
last_updated: 2026-09-02
next_review: al aprobarse, o 2027-03-02
related:

* README.md
* 02-Roles-y-Permisos.md
* ../000-Constitucion/11-Seguridad.md
* ../001-Arquitectura/08-Arquitectura-de-Seguridad.md
* ../006-BaseDatos/01-Convenciones-de-Base-de-Datos.md

---

# Modelo de Usuarios y Autenticación

## Propósito

Definir cómo se identifica un usuario humano ante el backend de AICOS: la tabla que lo representa, cómo se protege su contraseña, y el token que prueba su identidad en cada request.

---

# 1. Tabla `usuarios`

Hereda las columnas estándar de `006-BaseDatos/01-Convenciones-de-Base-de-Datos.md` (`id`, `creado_en`, `actualizado_en`, `eliminado_en`).

| Columna | Tipo | Nulo | Default | Descripción |
|---|---|---|---|---|
| `id` | `UUID` | No | generado en app | Clave primaria, conforme a la convención del proyecto. |
| `email` | `VARCHAR(255)` | No | — | Identificador de login. Único (`UNIQUE`). |
| `password_hash` | `VARCHAR(255)` | No | — | Hash bcrypt de la contraseña. **Nunca se guarda ni se loguea la contraseña en texto plano.** |
| `nombre` | `VARCHAR(120)` | No | — | Nombre para mostrar. |
| `rol` | `VARCHAR(30)` | No | — | Uno de los 4 roles de `02-Roles-y-Permisos.md`. |
| `activo` | `BOOLEAN` | No | `true` | Un usuario inactivo no puede autenticarse, aunque su contraseña sea correcta. Reemplaza el borrado físico para revocar acceso sin perder el historial de decisiones que tomó (`decision_records.user_id` seguiría teniendo sentido). |
| `creado_en` / `actualizado_en` / `eliminado_en` | — | — | — | Estándar del proyecto. |

**Restricción (`CHECK`):** `rol IN ('admin_principal', 'responsable_tecnico', 'responsable_negocio', 'usuario_operativo')` (ver `02-Roles-y-Permisos.md`).

**Índice:** único sobre `email`.

**Cómo se crea el primer usuario:** no hay endpoint de auto-registro en esta versión (ver sección 5). El primer usuario (Lucas, rol `admin_principal`) se crea con un script de seed o directamente por migración de datos — a decidir en la sección de implementación, no aquí. Usuarios siguientes los crea un `admin_principal` (ver `02-Roles-y-Permisos.md`).

---

# 2. Hashing de Contraseñas

* Algoritmo: **bcrypt**, vía la librería `bcrypt` (no `passlib`: `passlib` tiene mantenimiento discontinuado desde 2020; `bcrypt` es la librería de referencia, activamente mantenida — criterio de `002-CTO/03-Stack-Tecnico.md` sobre evaluación de dependencias).
* Factor de costo: 12 (default razonable en 2026; se documenta explícito en vez de dejarlo implícito, para poder subirlo sin sorpresas si el hardware lo permite).
* Nunca se compara una contraseña en texto plano contra otra — siempre `bcrypt.checkpw`.

---

# 3. Token JWT

## 3.1 Algoritmo y secreto

* Algoritmo: **HS256** (simétrico). Suficiente mientras exista un solo backend emitiendo y validando tokens; si en el futuro hay múltiples servicios que solo necesitan *validar* (no emitir), se reevalúa RS256 (asimétrico) — no antes, por simplicidad (Principio de Simplicidad del proyecto).
* Secreto: `JWT_SECRET_KEY`, variable de entorno nueva en `backend/.env` (nunca en código ni en `.env.example` con un valor real — mismo criterio que ya se aplicó con `GEMINI_API_KEY`, ver DEC-023).

## 3.2 Claims

```json
{
  "sub": "uuid-del-usuario",
  "email": "lucas@merchly.ai",
  "rol": "admin_principal",
  "iat": 1756800000,
  "exp": 1756828800
}
```

* `sub`: el `id` del usuario (UUID). Es lo que reemplaza al `user_id` de texto libre en `POST /decisiones` (ver `03-Alcance-y-Plan-de-Migracion.md`).
* `rol`: se incluye en el token para no tener que consultar la base de datos en cada request solo para saber los permisos — se revalida contra la base en `GET /auth/me` y al hacer login, no en cada request protegido (trade-off consciente: si a alguien le cambian el rol a mitad de sesión, el token viejo sigue con el rol anterior hasta que expire o vuelva a loguearse).

## 3.3 Expiración

* **8 horas.** Sin refresh token en esta versión — al expirar, se vuelve a hacer login. Es una decisión deliberada de simplicidad: con un solo usuario real hoy, el costo de un refresh token (endpoint nuevo, tabla de tokens revocados o rotación) no se justifica todavía. Se revisa si en el futuro hay usuarios operativos que necesiten sesiones más largas sin volver a loguearse.

## 3.4 Dónde viaja el token

* Header `Authorization: Bearer <token>`, estándar. No se usan cookies en esta versión (no hay frontend con sesión de navegador todavía — Streamlit, según `002-CTO/03-Stack-Tecnico.md` — que dependa de cookies; cuando lo haya, se revisa si conviene).

---

# 4. Endpoints Nuevos

## 4.1 `POST /auth/login`

**Request:**

```json
{"email": "lucas@merchly.ai", "password": "..."}
```

**Respuesta 200:**

```json
{"access_token": "eyJ...", "token_type": "bearer", "expira_en": 28800}
```

**Respuesta 401:** email no existe, contraseña incorrecta, o usuario inactivo. **El mensaje de error es el mismo en los tres casos** ("credenciales inválidas") — no distinguir "el email no existe" de "la contraseña es incorrecta" es una norma estándar de seguridad para no filtrar qué emails están registrados.

## 4.2 `GET /auth/me`

**Requiere:** token válido.

**Respuesta 200:**

```json
{"id": "uuid", "email": "lucas@merchly.ai", "nombre": "Lucas", "rol": "admin_principal", "activo": true}
```

Sirve para que un cliente (frontend, o el propio Lucas probando con curl) confirme qué usuario y rol tiene el token actual, sin tener que decodificarlo a mano.

---

# 5. Fuera de Alcance de Esta Versión

No se implementan todavía, por no tener un caso de uso real hoy (mismo Principio de Simplicidad que ya aplicó `006-BaseDatos`):

* **Auto-registro** (`POST /auth/registro` abierto al público) — no aplica, AICOS no es un producto con usuarios externos todavía.
* **Refresh tokens** — ver sección 3.3.
* **Recuperación de contraseña por email** — no hay proveedor de email configurado en el proyecto todavía.
* **Autenticación multifactor (MFA)** — se revisa cuando haya más de un usuario administrador o datos más sensibles en juego.
* **OAuth/proveedores externos** (Google, etc.) — descartado explícitamente para esta versión (decisión del CTO, 2026-09-02); se revisa si en el futuro hay necesidad real de login social.

---

# Resumen Ejecutivo para IA

La autenticación de AICOS usa una tabla `usuarios` (email + contraseña con hash bcrypt + rol) y JWT firmado con HS256, sin refresh token, expirando a las 8 horas. `POST /auth/login` devuelve el token; `GET /auth/me` confirma la identidad actual. No hay auto-registro: los usuarios se crean manualmente o por un `admin_principal`.
