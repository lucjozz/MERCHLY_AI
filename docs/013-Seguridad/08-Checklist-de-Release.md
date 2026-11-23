# 08-Checklist-de-Release.md

---

title: Checklist antes de cada versión (release)
document: 013-08
version: 0.1.0
status: Borrador — pendiente visto bueno del CTO (DEC-037)
owner: CTO
last_updated: 2026-11-24
related:

* 04-Endurecimiento-para-Lanzamiento.md
* 07-Plan-de-Respuesta-a-Incidentes.md
* ../002-CTO/07-Despliegue-en-Render.md

---

# Checklist antes de cada versión

Copiar esta lista en el PR o en la nota de la versión y tildar cada punto. Si alguno no se cumple, la versión no sale.

## Código

- [ ] CI de GitHub en verde: backend (tests + aislamiento real entre negocios + bandit + pip-audit), frontend (tipos + lint + build + npm audit + bundle sin secretos), gitleaks y trivy.
- [ ] Cada endpoint nuevo exige sesión y rol (el test `test_rutas_publicas_son_solo_las_esperadas` lo controla), filtra por organización y tiene test de "otro negocio → 404".
- [ ] Toda tabla nueva con datos de negocio tiene `organizacion_id`, RLS con `FORCE` y `GRANT` mínimos a `merchly_app`.
- [ ] Ningún schema de entrada acepta campos extra (`EntradaEstricta`) y todo texto tiene largo máximo.
- [ ] Lo que viene de la IA se valida y se muestra como texto (nunca HTML).
- [ ] Acciones sensibles nuevas registran evento en la bitácora de auditoría.
- [ ] Commits en español, por tema, sin secretos (pre-commit con gitleaks activo).

## Base de datos

- [ ] La migración se probó en local (`alembic upgrade head`) y tiene `downgrade`.
- [ ] **Backup fresco antes de desplegar** si la migración toca datos existentes.
- [ ] Las migraciones no corren solas al levantar (se ejecutan en el pre-deploy de Render).

## Configuración

- [ ] Variables nuevas documentadas en `.env.example` (sin valores reales) y cargadas en Render.
- [ ] Ningún secreto en variables `NEXT_PUBLIC_*`.
- [ ] `EXPONER_DOCS` apagado en producción.

## Después de desplegar (prueba de humo, 5 minutos)

- [ ] Login con email y con Google.
- [ ] Buscar un producto, aprobarlo y generar su campaña.
- [ ] Una página de cada sección carga sin errores.
- [ ] La bitácora registra el login.
- [ ] Sin errores nuevos en Sentry ni alertas en UptimeRobot.

## Si algo sale mal

- [ ] Volver a la versión anterior desde Render (Rollback) y seguir el plan de incidentes (013-07).
