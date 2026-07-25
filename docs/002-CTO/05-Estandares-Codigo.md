# 05-Estandares-Codigo.md

---

title: Estándares de Código de Merchly AI
document: 002-05
version: 1.0.0
status: Draft
owner: CTO
last_updated: 2026-07-25
next_review: 2027-01-25
related:

* 03-Stack-Tecnico.md
* ../000-Constitucion/08-Normas-de-Ingenieria.md
* ../000-Constitucion/10-Estandares-de-Calidad.md

---

# Estándares de Código

## Propósito

Aterrizar la Norma 6 (Organización del Código) y la Norma 4 (Simplicidad) de `000-Constitucion/08-Normas-de-Ingenieria.md` en convenciones verificables por lenguaje.

---

# 1. Python (Backend)

* Formato: `black`, sin configuración personalizada.
* Orden de imports: `isort`.
* Linter: `ruff`.
* Tipado: obligatorio (`mypy` en modo estricto para módulos nuevos).
* Nombres: `snake_case` para funciones y variables, `PascalCase` para clases.
* Docstrings: obligatorios en toda función pública, formato Google Style.

---

# 2. TypeScript / React (Frontend)

* Formato: `prettier`.
* Linter: `eslint` con reglas de `next/core-web-vitals`.
* Tipado: `strict: true` en `tsconfig.json`; prohibido `any` salvo justificación en comentario.
* Nombres: `camelCase` para funciones/variables, `PascalCase` para componentes.
* Componentes: funcionales con hooks; se evita lógica de negocio dentro de componentes de presentación.

---

# 3. SQL / Base de Datos

* Nombres de tablas en `snake_case`, en plural (`orders`, `agents`).
* Toda tabla debe tener `created_at` y `updated_at`.
* Migraciones versionadas y nunca editadas retroactivamente una vez aplicadas en un ambiente compartido.

---

# 4. Estructura de Carpetas (referencia general)

```text
backend/
  app/
    api/
    core/
    models/
    services/
    tests/
frontend/
  app/
  components/
  lib/
  tests/
agents/
  <nombre-del-agente>/
    prompt.md
    handler.py
    tests/
```

Esta estructura es la referencia inicial y se detallará con mayor profundidad en `004-Backend` y `005-Frontend` cuando comience la implementación.

---

# 5. Comentarios

Se permiten únicamente cuando explican **por qué**, no **qué** (el código ya dice qué hace). Prohibido comentar código muerto; se elimina en su lugar.

---

# 6. Criterio de Revisión de Código

Todo pull request se evalúa contra:

* ¿Cumple el estándar del lenguaje correspondiente?
* ¿Tiene pruebas para la lógica nueva?
* ¿Está documentado si introduce un módulo nuevo?
* ¿Introduce dependencias no evaluadas (Norma 15)?
* ¿Es la solución más simple posible (Norma 4)?

---

# Resumen Ejecutivo para IA

Python: black + isort + ruff + mypy estricto. TypeScript: prettier + eslint + strict mode, sin `any`. SQL: snake_case plural, `created_at`/`updated_at` obligatorios. Comentarios solo explican el porqué. Todo PR se revisa contra el checklist de esta sección.
