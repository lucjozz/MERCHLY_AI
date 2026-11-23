# 05-Pendientes-para-Lanzar.md

---

title: Pendientes para Lanzar (seguridad y operación)
document: 013-05
version: 0.1.0
status: Vivo — se actualiza a medida que se cierran ítems
owner: CTO
last_updated: 2026-11-23
related:

* 04-Endurecimiento-para-Lanzamiento.md
* ../../memory/DECISIONS.md (DEC-032)

---

# Pendientes para Lanzar

## Propósito

Lista única de lo que falta para poner MERCHLY AI en producción. Separa lo que **solo puede hacer una persona** (cuentas, pagos, decisiones, credenciales) de lo que puede implementarse en código.

---

# 1. Estado de los 23 puntos de seguridad

| # | Punto | Estado |
|---|---|---|
| 1 | Secretos fuera de Git | ✅ gitleaks: historial limpio (276 commits). Secretos locales rotados y generados con `secrets.token_urlsafe`. Pre-commit y CI con gitleaks configurados. ⏳ Rotar la contraseña del admin y activar secret scanning en GitHub (manual). |
| 2 | Queries parametrizadas | ✅ Sin SQL crudo con datos de usuario; regla bandit S608 en CI; tests de inyección. |
| 3 | Cloudflare / WAF | ⏳ Requiere dominio y hosting (manual + config). El código ya soporta `CF-Connecting-IP` con `CONFIAR_PROXY`. |
| 4 | Backups y restauración | ⏳ Requiere almacenamiento externo (manual). Hay backup local pre-migración en `C:\Users\DANXX\Documents\MERCHLY_backups`. |
| 5 | Contraseñas | ✅ bcrypt 12, política 12+ caracteres y ≤ 72 bytes, tiempo constante, emails en minúsculas, re-hash, seed con getpass y `--rotar`. |
| 6 | Row-Level Security | ✅ Organizaciones + RLS con FORCE + rol sin privilegios; suite de aislamiento contra Postgres real. |
| 7 | Autenticación y cookies | ✅ Todo exige login; BFF con cookies HttpOnly, `__Host-` y Secure en producción; CSRF por Origin + SameSite; guard en `proxy.ts`; 401 → login, 403 → "sin permiso". |
| 8 | Rate limiting | ✅ Login por email+IP, email e IP (429 + Retry-After, fail-closed); cuotas por organización en agentes. ⏳ Complementar en Cloudflare. |
| 9 | Validación de inputs | ✅ Topes alineados con columnas, `Query(ge, le)`, body ≤ 1 MB, `extra="forbid"`. |
| 10 | Pool y concurrencia | ✅ Pool explícito, timeouts de Postgres y Redis, 2 workers, `FOR UPDATE` en decisiones (probado con envíos simultáneos). ⏳ Prueba de carga (k6) cuando haya hosting. |
| 11 | HTTPS y headers | ✅ Headers en backend y frontend, CSP con nonce, docs ocultos, sin header Server. ⏳ TLS y HSTS cuando haya dominio; calificación A en securityheaders.com. |
| 12 | Errores seguros | ✅ 500 genérico con request_id, 422 sin eco, mensajes claros por código en el frontend. |
| 13 | Monitoreo y alertas | ⏳ Healthcheck del backend listo; faltan las cuentas de UptimeRobot/Better Stack y Sentry (manual). |
| 14 | Archivos subidos | ➖ No hay subidas todavía. Política en 013-04; módulo de validación cuando aparezca la primera. |
| 15 | Solo datos necesarios | ✅ Listado resumido, sin hash ni campos internos; test de contrato de `/auth/me`. |
| 16 | Mass assignment | ✅ `extra="forbid"` en todas las entradas; tests. |
| 17 | CORS estricto | ✅ Orígenes por variable, sin `*`, métodos y headers explícitos; test de preflight. |
| 18 | Dependencias | ✅ pip-audit 0, npm audit 0, trivy 0 (HIGH/CRITICAL). CI y Dependabot configurados. ⏳ Que el CI corra en GitHub (al subir). |
| 19 | Credenciales de DB fuera del front | ✅ Regla escrita + chequeo de CI sobre el bundle. |
| 20 | Acceso a registros | ✅ Filtro por organización + RLS, rol mínimo por acción, decisiones append-only, borrado lógico. |
| 21 | Contenedores | ✅ Puertos solo en 127.0.0.1 (nmap desde el wifi: cerrados), contraseñas fuertes, Redis con contraseña, imagen sin root, multi-etapa, parcheada, read_only, cap_drop, límites. ⏳ Actualizar Docker Desktop. |
| 22 | IDOR y enumeración | ✅ 404 uniforme entre organizaciones (probado por HTTP), tiempos iguales en login. |
| 23 | Expiración y revocación | ✅ Access 15 min, refresh rotativo con detección de robo, logout con denylist, `token_version`, secreto fuerte obligatorio. |

---

# 2. Lo que tiene que hacer una PERSONA (no se puede automatizar)

## Urgente (antes de cualquier lanzamiento)

1. **Rotar la contraseña del admin.** La que se escribió en el chat quedó expuesta. Desde la raíz del repo, con los contenedores levantados:
   `docker compose exec backend python -m scripts.seed_admin --rotar`
2. **Visto bueno del CTO** a `04-Endurecimiento-para-Lanzamiento.md` y DEC-032. Confirmar quién es el `admin_principal` (el documento 013-02 nombra al CTO; Daniel indicó que es él).
3. **GitHub** (Settings del repo):
   - Activar *Secret scanning* y *Push protection*.
   - *Branch protection* en `main`: exigir el CI en verde y una revisión antes de mergear.
   - Activar las alertas de Dependabot.
4. **Hook local de secretos** (una vez por PC): `pip install pre-commit` y después `pre-commit install` en la raíz del repo.
5. **Topes de gasto de IA:** en Google AI Studio / Google Cloud (Gemini) y más adelante OpenAI, configurar un límite mensual de gasto y alertas. Si la clave de Gemini se pegó alguna vez en un chat, rotarla.

## Para salir a producción

6. **Hosting y dominio:** elegir proveedor (VPS o PaaS con Docker y Postgres administrado con backups/PITR), comprar el dominio.
7. **Cloudflare:** cuenta, DNS con proxy, SSL *Full (strict)*, reglas WAF gestionadas, rate limiting en `/api/auth/login` y `/api/backend/agentes/*`, *Bot Fight Mode*, y origen cerrado (Cloudflare Tunnel). Con el origen cerrado, poner `CONFIAR_PROXY=true`.
8. **Backups:** crear un bucket S3-compatible (Backblaze B2, Cloudflare R2 o el del hosting) y pasar las credenciales por el gestor de secretos del hosting (nunca por el chat).
9. **Monitoreo:** cuentas en UptimeRobot o Better Stack (contra `/health/ready`) y Sentry, más el canal de alertas (email o Telegram).
10. **Google Login:** en Google Cloud Console crear un *OAuth Client ID* de tipo "Aplicación web" con el origen autorizado del dominio (y `http://localhost:3000` para desarrollo). El **Client ID** no es secreto: se carga en `GOOGLE_CLIENT_ID`.
11. **Email transaccional** (Resend, Postmark, SES u otro) para invitaciones y recuperación de contraseña.
12. **Pagos:** averiguar qué pasarela opera en Bolivia con checkout alojado y webhooks firmados.
13. **Legal:** términos y condiciones y política de privacidad revisados por un abogado (Bolivia).
14. **Docker Desktop:** actualizar (la versión instalada es muy vieja). **Nunca** usar "Reset to factory defaults" (borra la base).
15. **Secretos de producción:** generarlos nuevos (no reutilizar los locales) y cargarlos solo en el gestor de secretos del hosting. Separar dev, staging y producción.

---

# 3. Lo que todavía se puede implementar en código

| Prioridad | Tarea | Depende de |
|---|---|---|
| ✅ | Gestión de usuarios: invitar por link, desactivar y cambiar rol (2026-11-24). Falta enviar la invitación por email | Email transaccional |
| Alta | Bitácora de auditoría append-only (login ok/fallido, logout, cambios de rol, borrados) | — |
| ✅ | Botón "Continuar con Google": implementado (2026-11-23), falta la prueba con una cuenta real | — |
| Alta | Pagos: la pantalla "Plan y pagos" existe (beta gratuita, precios a definir); falta integrar la pasarela con checkout alojado y webhooks firmados | Pasarela elegida, empresa registrada |
| Alta | Script de backup cifrado + restauración probada en entorno limpio (RPO/RTO) | Bucket externo |
| Media | Seguridad de LLM: timeouts y validación estricta de la salida de Gemini, mitigación de prompt injection en la categoría, no enviar datos de otras organizaciones | — |
| Media | Prueba de carga (k6) y ajuste del pool | Hosting |
| Media | Modelo de amenazas (STRIDE), checklist de release y plan de respuesta a incidentes | — |
| Media | Recuperación de contraseña por email | Email transaccional |
| Baja | Limpieza de 278 avisos de estilo de ruff (no son de seguridad) | — |
| Baja | Módulo de validación de archivos (magic bytes, tamaño, re-encode) | Primera funcionalidad con subidas |
