# MERCHLY AI DECISIONS LOG


## DEC-001

Fecha:

2026-07-21


Decisión:

El idioma oficial del proyecto será español.


Motivo:

Mantener coherencia documental.


Estado:

Aprobada.


---

## DEC-002

Fecha:

2026-07-21


Decisión:

GitHub será la fuente principal de almacenamiento del proyecto.


Motivo:

Garantizar continuidad y control de versiones.


Estado:

Aprobada.


---

## DEC-003

Fecha:

2026-07-21


Decisión:

Toda decisión estratégica requiere aprobación humana.


Motivo:

La IA recomienda, el humano mantiene control estratégico.


Estado:

Aprobada.


---

## DEC-004

Fecha:

2026-07-21


Decisión:

La documentación tiene la misma importancia que el código.


Motivo:

MERCHLY AI debe funcionar como una empresa tecnológica desde el inicio.


Estado:

Aprobada.


---

## DEC-005

Fecha:

2026-07-22


Decisión:

La estructura documental 000-020 no se modifica al documentar la organización empresarial. Se crea una serie separada, 100-Organizacion, con numeración propia.


Motivo:

Son dos preguntas distintas: dónde vive el conocimiento (000-020) frente a quién es responsable de cada capacidad (100+).


Estado:

Aprobada.


---

## DEC-006

Fecha:

2026-07-22


Decisión:

100-Organizacion se documenta con una estructura condensada de 7 documentos en lugar de un documento por cada subtema.


Motivo:

Evitar duplicar contenido ya cubierto en la Constitución (gobernanza, flujo de decisiones) y evitar un historial por carpeta cuando ya existe uno único del proyecto.


Estado:

Aprobada.


---

## DEC-007

Fecha:

2026-07-22


Decisión:

Los agentes de inteligencia artificial se organizan por rol (Arquitecto IA, Investigador IA, Revisor IA, Analista IA, etc.), no por proveedor. El proveedor que implementa cada rol es un detalle reemplazable.


Motivo:

Independencia tecnológica: permite cambiar de modelo de IA sin rediseñar procesos ni documentación.


Estado:

Aprobada.


---

## DEC-008

Fecha:

2026-07-22


Decisión:

Ningún agente IA puede ocupar el rol de Aprobador (A) en la Matriz RACI. Los agentes IA son siempre Responsables de ejecución (R) o Consultados (C).


Motivo:

Mantener el control humano sobre decisiones con consecuencias relevantes, conforme a la Constitución.


Estado:

Aprobada.


---

## DEC-009

Fecha:

2026-07-25


Decisión:

El stack técnico definitivo de Fase 0 queda fijado en: Python + FastAPI (backend), Next.js + React + TypeScript (frontend), PostgreSQL + pgvector + Redis (datos), Docker + GitHub Actions + Ubuntu (infraestructura), n8n (automatización). Documentado en docs/002-CTO/03-Stack-Tecnico.md.


Motivo:

Evitar deriva tecnológica: cualquier cambio futuro de stack debe ser una decisión consciente y registrada, no una elección ad hoc durante la implementación.


Estado:

Aprobada.


---

## DEC-010

Fecha:

2026-07-25


Decisión:

Se adopta Conventional Commits (en español) y un modelo de ramas main + feature/fix/docs/chore. Todo cambio no trivial requiere pull request con al menos una aprobación humana, incluyendo el trabajo producido por agentes IA.


Motivo:

Unificar el flujo de trabajo entre colaboradores humanos y agentes IA, y mantener el control humano sobre lo que se integra al proyecto (coherente con DEC-003).


Estado:

Aprobada.


---

## DEC-011

Fecha:

2026-07-25


Decisión:

docs/002-CTO se documenta como volumen técnico-operativo (metodología, stack, flujo Git, estándares de código, entorno de desarrollo), separado del rol organizacional del CTO ya definido en 100-Organizacion/03-Roles-Ejecutivos.md.


Motivo:

Mismo criterio que DEC-005: separar "quién es responsable" (100-Organizacion) de "cómo se ejecuta" (002-CTO), evitando duplicar contenido entre volúmenes.


Estado:

Aprobada.


---

## DEC-012

Fecha:

2026-07-25


Decisión:

Se documenta un modelo de negocio propuesto en tres opciones (tiendas propias / SaaS a terceros / híbrido) en docs/003-CEO/02-Modelo-de-Negocio.md, recomendando el híbrido. La elección final entre las tres queda PENDIENTE de aprobación explícita del CEO.


Motivo:

Es una decisión estratégica que, conforme a DEC-003, requiere aprobación humana explícita y no puede darse por asumida solo porque exista una recomendación documentada.


Estado:

Superada por DEC-014.

---

## DEC-014

Fecha:

2026-07-26

Decisión:

Se aprueba la Opción C (Híbrido) como modelo de negocio de AICOS: Fase 0-1 con AICOS operando exclusivamente tiendas propias de Merchly como banco de pruebas; Fase 2+ se evalúa abrir AICOS como plataforma a terceros (Opción B), reutilizando lo ya construido. Se descarta, por ahora, un camino inicial de white-label a terceros. Documentado en docs/003-CEO/02-Modelo-de-Negocio.md.

Motivo:

Coherente con el Principio de Simplicidad (Norma 4 de 000-Constitucion/08-Normas-de-Ingenieria.md): no construir multi-tenancy antes de tener una sola tienda propia funcionando. Consecuencia directa: 004-Backend no necesita diseñarse multi-tenant desde el día uno.

Estado:

Aprobada.


---

## DEC-013

Fecha:

2026-07-25


Decisión:

Se establecen criterios verificables de cierre de la Fase 0 (Fundación) en docs/003-CEO/03-Criterios-de-Exito-Fase0.md, como referencia operativa temporal mientras ROADMAP.md permanezca vacío.


Motivo:

Sin criterios explícitos de cierre de fase, no hay forma objetiva de saber cuándo avanzar a Fase 1, lo que genera riesgo de extender la Fundación indefinidamente.


Estado:

Aprobada.

---

## DEC-015

Fecha:

2026-07-26

Decisión:

Se completa ROADMAP.md con 9 fases (Fundación a Empresa Autónoma), cada una con volúmenes documentales asociados, hitos y criterios de cierre verificables. El cierre de cada fase se rige por criterios, no solo por fecha calendario, conforme al criterio ya establecido en docs/003-CEO/03-Criterios-de-Exito-Fase0.md.

Motivo:

ROADMAP.md estaba vacío desde el inicio del proyecto; sin él no había forma de secuenciar formalmente el trabajo más allá de Fase 0.

Estado:

Aprobada.
