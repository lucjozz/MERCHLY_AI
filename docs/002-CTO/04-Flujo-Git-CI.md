# 04-Flujo-Git-CI.md

---

title: Flujo de Git y CI/CD de Merchly AI
document: 002-04
version: 1.0.0
status: Draft
owner: CTO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* 03-Stack-Tecnico.md
* ../000-Constitucion/08-Normas-de-Ingenieria.md

---

# Flujo de Git y CI/CD

## Propósito

Definir cómo se gestionan ramas, commits, pull requests e integración continua, de forma que humanos y agentes IA sigan el mismo proceso.

---

# 1. Estrategia de Ramas

```text
main                    → siempre desplegable / documentación vigente
├── feature/<slug>       → nueva funcionalidad o documento
├── fix/<slug>            → corrección de errores
├── docs/<slug>            → cambios exclusivos de documentación
└── chore/<slug>            → mantenimiento, configuración, dependencias
```

* `main` es la única rama protegida en Fase 0.
* No se permite trabajo directo sobre `main` salvo para el propio CTO en cambios triviales de documentación (ej. corrección de un typo), y aun así se recomienda pull request.

---

# 2. Convención de Commits

Se adopta **Conventional Commits**:

```text
<tipo>(<alcance opcional>): <descripción breve en español>
```

Tipos permitidos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`.

Ejemplos:

* `docs(002-cto): agrega volumen de stack técnico`
* `feat(backend): agrega endpoint de autenticación`
* `fix(agents): corrige timeout en agente investigador`

---

# 3. Pull Requests

Todo cambio no trivial entra por pull request, incluyendo el trabajo generado por agentes IA.

Un pull request debe incluir:

* Descripción del objetivo (qué y por qué).
* Referencia al documento o issue relacionado, si existe.
* Checklist de `000-Constitucion/08-Normas-de-Ingenieria.md` §19 marcado.

Revisión mínima antes de fusionar: una aprobación humana, conforme a `01-Rol-Tecnico-Operativo.md`, sección 4.

---

# 4. Integración Continua (GitHub Actions)

En Fase 0, el pipeline mínimo de CI ejecuta, cuando exista código (a partir de `004-Backend` / `005-Frontend`):

```text
1. Lint
2. Tests unitarios
3. Build
```

Mientras el repositorio sea solo documental (Fase 0 actual), el pipeline se limita a:

```text
1. Validación de formato Markdown
2. Verificación de enlaces internos rotos
```

---

# 5. Versionado

Merchly AI usa versionado semántico (`MAJOR.MINOR.PATCH`) tanto para el software como, de forma adaptada, para los volúmenes de documentación (ver historiales de cada volumen, ej. `000-Constitucion/14-Historial.md`).

---

# 6. Etiquetas y Releases

Los releases formales del software comenzarán al cerrarse la Fase 1 (Infraestructura). Hasta entonces, el avance se registra únicamente en `memory/` y en los historiales documentales.

---

# Resumen Ejecutivo para IA

Ramas: `main` protegida + `feature/fix/docs/chore`. Commits en formato Conventional Commits, en español. Todo cambio no trivial vía pull request con al menos una aprobación humana. CI mínimo actual: validación de Markdown y enlaces; se ampliará a lint/tests/build cuando exista código.
