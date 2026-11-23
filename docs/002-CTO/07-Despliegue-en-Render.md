# 07-Despliegue-en-Render.md

---

title: Despliegue de MERCHLY AI en Render + Cloudflare
document: 002-07
version: 0.1.0
status: Borrador listo para usar — pendiente visto bueno del CTO (DEC-036)
owner: CTO
last_updated: 2026-11-24
related:

* ../../render.yaml
* ../013-Seguridad/04-Endurecimiento-para-Lanzamiento.md
* ../006-BaseDatos/04-Politica-de-Backups-y-Retencion.md

---

# Despliegue en Render + Cloudflare (paso a paso)

## Arquitectura

* **merchly-web** (Next.js, el BFF): el único servicio público.
* **merchly-backend** (FastAPI): **servicio privado**, sin URL pública. Solo lo alcanza el frontend por la red interna de Render.
* **merchly-db**: Postgres administrado (Render hace backups diarios; en planes pagos, recuperación a un punto en el tiempo).
* **merchly-redis**: Key Value, solo red interna.
* **Cloudflare** adelante: DNS, HTTPS, firewall (WAF) y límite de intentos.

## Lo que hace la persona (cuentas y decisiones)

1. Crear la cuenta en **render.com** e iniciar sesión con GitHub (con permiso sobre el repo `lucjozz/MERCHLY_AI`).
2. En Render: **New → Blueprint**, elegir el repo y la rama `main`. Render lee `render.yaml` y propone los 4 recursos. Elegir los planes (para clientes reales: planes pagos, no los gratuitos que se duermen).
3. Cargar en el panel las variables marcadas `sync: false`:
   * `CORS_ORIGENES` y `APP_URL`: `https://tudominio.com`.
   * `GOOGLE_CLIENT_ID` y `NEXT_PUBLIC_GOOGLE_CLIENT_ID`: el Client ID de Google. Agregar `https://tudominio.com` en "Orígenes autorizados" de Google Cloud.
   * `GEMINI_API_KEY`, `OPENAI_API_KEY`, `RESEND_API_KEY`, `EMAIL_REMITENTE` (ej.: `MERCHLY AI <no-responder@tudominio.com>`).
   * `NEXT_PUBLIC_SOPORTE_WHATSAPP`: `59163628429`.
4. Después del primer despliegue (cuando la migración ya creó el rol `merchly_app`): copiar la `connectionString` de la base, cambiar el usuario `merchly` por `merchly_app` y la contraseña por el valor de `DB_APP_PASSWORD`, y guardarla en `DATABASE_URL` del backend. Volver a desplegar.
5. **Dominio:** comprarlo en Cloudflare. En Render (merchly-web → Settings → Custom Domains) agregar el dominio y copiar el registro DNS que indica en Cloudflare, con el **proxy activado** (nube naranja).
6. **Cloudflare:**
   * SSL/TLS en **Full (strict)** y "Always Use HTTPS".
   * WAF: activar las reglas administradas.
   * Rate limiting: `/api/auth/*` (por ejemplo 20 solicitudes por minuto por IP) y `/api/backend/agentes/*`.
   * Bot Fight Mode activado.
7. **Crear el primer admin** desde la Shell del backend en Render: `python -m scripts.seed_admin`.
8. **Monitoreo:** en UptimeRobot (o Better Stack), un monitor HTTPS a `https://tudominio.com/login` cada 5 minutos con alerta por email. En Sentry, crear el proyecto y pasar el DSN para conectarlo.

## Verificaciones antes de abrir la beta

* [ ] `https://tudominio.com` abre el login con candado y sin errores en la consola.
* [ ] El backend **no** tiene URL pública (merchly-backend es privado).
* [ ] Login con email y con Google funcionando.
* [ ] "¿Olvidaste tu contraseña?" llega por email.
* [ ] Una búsqueda y una campaña con IA real funcionan, y el tope de gasto está configurado en Google y OpenAI.
* [ ] securityheaders.com y Mozilla Observatory dan nota A o A+.
* [ ] Simulacro de restauración de un backup de Render en una base nueva (anotar cuánto tardó).
* [ ] La alerta de UptimeRobot llega al apagar el servicio a propósito.

## Riesgos a verificar en el primer despliegue

* **Crear el rol `merchly_app`:** la migración necesita que el usuario de la base pueda crear roles (`CREATEROLE`). Si Render no lo permite, la alternativa es crear el rol desde el panel o la consola de la base y volver a correr la migración. Mientras tanto, **no** se abre la beta usando el usuario dueño (se perdería la protección de RLS).
* **Extensión pgvector:** verificar con `CREATE EXTENSION IF NOT EXISTS vector;`.
* **Puerto del backend:** el contenedor escucha en el 8000; confirmar que Render lo detecta en el servicio privado.

## Backups

* En producción: los backups automáticos de Render y, además, `ops/backups/backup.py` adaptado a la base de Render, para tener una copia cifrada **fuera** de Render (bucket R2 o Backblaze), como pide la política 006-04.
* En la PC local: `backend\venv\Scripts\python.exe ops\backups\backup.py` (cifrado) y `ops\backups\probar_restauracion.py` (simulacro en un Postgres limpio). El primer simulacro (2026-11-24) restauró 11 tablas idénticas, con RLS activo, en 41 s.
