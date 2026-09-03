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

## DEC-015

Fecha:

2026-07-26

Decisión:

Se completa ROADMAP.md con 9 fases (Fundación a Empresa Autónoma), cada una con volúmenes documentales asociados, hitos y criterios de cierre verificables. El cierre de cada fase se rige por criterios, no solo por fecha calendario, conforme al criterio ya establecido en docs/003-CEO/03-Criterios-de-Exito-Fase0.md.

Motivo:

ROADMAP.md estaba vacío desde el inicio del proyecto; sin él no había forma de secuenciar formalmente el trabajo más allá de Fase 0.

Estado:

Aprobada.

---

## DEC-016

Fecha:

2026-07-26

Decisión:

Se crea el volumen docs/007-Agentes, que define el contrato técnico estándar de agentes IA (10 secciones: identidad, entradas, salidas, herramientas, memoria, permisos, límites, errores, métricas, registro), el ciclo de vida de un agente (8 etapas) y el primer agente con contrato técnico completo: el Agente Investigador de Producto.

Motivo:

Cumplir el criterio técnico de cierre de Fase 0 establecido en docs/003-CEO/03-Criterios-de-Exito-Fase0.md: contar con al menos un agente IA con contrato técnico completo (entradas, salidas, límites), antes de iniciar la implementación en 004-Backend.

Estado:

Aprobada.

---

## DEC-017

Fecha:

2026-07-26

Decisión:

Se implementa el primer código funcional del proyecto: backend FastAPI mínimo (backend/) con endpoint /health, y docker-compose.yml en la raíz que levanta backend, PostgreSQL (con extensión pgvector) y Redis. El endpoint /health fue probado localmente (pytest y solicitud HTTP real) y responde 200 con estado "ok".

Motivo:

Cumplir los 2 criterios técnicos restantes de cierre de Fase 0, definidos en docs/003-CEO/03-Criterios-de-Exito-Fase0.md: entorno local funcional vía docker compose y al menos un endpoint de backend funcionando.

Estado:

Aprobada.

---

## DEC-018

Fecha:

2026-07-27

Decisión:

Se conecta el backend realmente a PostgreSQL/pgvector (vía SQLAlchemy 2.0 async + psycopg 3, en backend/app/core/database.py) y a Redis (vía redis.asyncio, en backend/app/core/redis.py). Se separa el endpoint /health original (liveness, sin dependencias) de un nuevo endpoint /health/ready (readiness), que verifica ambas conexiones y responde "ok" o "degraded" sin lanzar error 5xx si alguna dependencia falla. Se agregan 3 tests con dependencias mockeadas (sin requerir Postgres/Redis reales) y se valida manualmente que /health/ready responde 200 con "degraded" cuando no hay servicios reales disponibles.

Motivo:

Primer hito técnico de Fase 1 (Infraestructura) según ROADMAP.md: los contenedores de PostgreSQL y Redis ya existían en docker-compose.yml desde el cierre de Fase 0, pero el backend no los usaba todavía. Separar liveness de readiness sigue la práctica estándar de la industria y evita que un problema temporal de base de datos tumbe el proceso completo.

Estado:

Aprobada.

---

## DEC-019

Fecha:

2026-07-27

Decisión:

Se completa el volumen docs/006-BaseDatos: convenciones de base de datos (nombres, UUID como PK, timestamps con borrado lógico, tipos de datos, pgvector, sin multi-tenancy hasta Fase 7), el esquema real de Fase 1 (tabla productos_candidatos), la estrategia de migraciones con Alembic y la política de backups/retención. Se implementa el código correspondiente: modelo SQLAlchemy (backend/app/models/), configuración de Alembic (backend/alembic/) y la primera migración (productos_candidatos). El modelo fue validado compilando su DDL real de PostgreSQL sin necesitar una base conectada, y la migración fue validada con "alembic upgrade head --sql" (modo offline), coincidiendo exactamente con el esquema documentado.

Motivo:

El Agente Investigador de Producto (docs/007-Agentes) necesita un lugar donde persistir sus resultados antes de poder implementarse en código, conforme a la sección 3 ("Salidas") de su contrato técnico.

Estado:

Aprobada.

---

## DEC-020

Fecha:

2026-07-27

Decisión:

Se implementa en código el Agente Investigador de Producto, adelantando su implementación (prevista para Fase 2) dentro de Fase 1: schemas Pydantic que replican exactamente las secciones 2 y 3 de su contrato técnico (validación de mercado_objetivo ISO 3166-1, rechazo de categorías prohibidas, truncado de cantidad_resultados a 50), un proveedor abstracto (ProveedorInvestigacion) con una implementación provisional simulada (ProveedorInvestigacionSimulado, claramente marcada como no apta para decisiones reales), la orquestación completa (AgenteInvestigadorProducto: validación, reintentos según sección 8 del contrato, persistencia en productos_candidatos, salida estructurada) y el endpoint POST /agentes/investigador-producto. Se agregan 12 tests nuevos (18 en total en el proyecto), todos en verde, más verificación manual del servidor real (incluyendo el caso sin PostgreSQL disponible, que falla de forma esperada por resolución de hostname, no por un error de código).

Motivo:

Con el esquema de datos ya modelado en docs/006-BaseDatos, el siguiente paso natural es el propio agente. Se usa un proveedor simulado en lugar de esperar a la integración real con Gemini para no bloquear el resto de la arquitectura (validación, persistencia, API) con una dependencia externa todavía no configurada.

Estado:

Aprobada.

---

## DEC-021

Fecha:

2026-07-30

Decisión:

Se completa el volumen docs/010-Prompts (convenciones de prompts, el prompt real del Agente Investigador de Producto, y su registro), y se implementa ProveedorInvestigacionGemini (backend/app/services/proveedores/gemini.py): integración real con la API de Gemini vía el SDK google-genai, usando salida estructurada nativa (response_schema) en vez de parseo de texto libre. El endpoint POST /agentes/investigador-producto elige automáticamente entre el proveedor real (si GEMINI_API_KEY está configurada) y el proveedor simulado (si no). Se agregan 5 tests nuevos (23 en total en el proyecto) con un cliente de Gemini mockeado, sin llamar a la API real de Google desde este entorno.

Motivo:

Cerrar el pendiente registrado en DEC-020: reemplazar el proveedor simulado por una integración real, siguiendo la disciplina "documentación antes que código" (primero el prompt en 010-Prompts, después el proveedor en código).

Pendiente:

La verificación final contra la API real de Gemini (con una GEMINI_API_KEY válida y acceso de red a Google) no pudo hacerse desde este entorno de ejecución. Debe correrse en la máquina del usuario o en un entorno de CI/CD con acceso a internet, antes de usar este agente en decisiones de negocio reales.

Estado:

Aprobada.

---

## DEC-022

Fecha:

2026-07-30

Decisión:

Se restaura backend/alembic/env.py, que faltaba en el repositorio (se había escrito en la sesión de docs/006-BaseDatos pero no llegó al ZIP entregado, probablemente perdido en una fusión manual). Sin este archivo, Alembic no podía ejecutar ninguna migración ("ImportError: Can't find Python file alembic/env.py"). Se verificó con "alembic upgrade head --sql" que, restaurado, genera el SQL correcto y coincide con docs/006-BaseDatos/02-Esquema-Fase1.md. Se sincronizan además memory/CONTEXT.md, memory/NEXT_STEPS.md y prompts/MASTER_CONTEXT_PROMPT.md, que habían quedado desactualizados (versión 0.5-0.6 Alpha) en las últimas rondas de trabajo mientras memory/CURRENT_STATE.md y memory/DECISIONS.md sí se mantuvieron al día.

Motivo:

Una auditoría solicitada por el usuario detectó ambos problemas. El archivo faltante es un bug funcional real (Alembic no arranca); la memoria desactualizada es un riesgo de continuidad si otra sesión o instancia de IA confía en esos documentos como fuente de verdad sin cruzarlos con memory/CURRENT_STATE.md.

Estado:

Aprobada.

## DEC-023

Fecha:

2026-08-03

Decisión:

Se cierra el pendiente registrado en DEC-021: el usuario verificó ProveedorInvestigacionGemini contra la API real de Gemini (con GEMINI_API_KEY válida y acceso de red a Google), confirmando que responde con datos reales (no el proveedor simulado) y que el contenido respeta el prompt documentado en docs/010-Prompts/02-Prompt-Investigador-de-Producto.md (evidencia real, sin inventar productos). En paralelo, se corrige docker-compose.yml: el servicio backend cargaba env_file: ./backend/.env.example en vez de ./backend/.env, por lo que cualquier valor puesto en backend/.env (incluida GEMINI_API_KEY) nunca llegaba al contenedor — el backend arrancaba siempre con ProveedorInvestigacionSimulado sin ningún error visible. Se actualizan docs/007-Agentes/04-Registro-de-Agentes.md y docs/010-Prompts/03-Registro-de-Prompts.md quitando la nota de "pendiente verificación final" (Estado del prompt: Activo), conforme a memory/NEXT_STEPS.md, tarea 1. Se corrige además docs/002-CTO/06-Entorno-Desarrollo.md (sección "Levantamiento Local" con los comandos reales, incluyendo `alembic upgrade head` manual) y README.md (nueva sección "Cómo Empezar" y "Estado Actual" sincronizado con memory/CURRENT_STATE.md, que seguía en 0.1 Alpha / Fundación).

Motivo:

La separación entre backend/.env (secretos reales, en .gitignore) y backend/.env.example (plantilla pública, sin secretos) era y sigue siendo correcta por Norma 11 (Seguridad por Diseño). El bug estaba un nivel más abajo: docker-compose.yml apuntaba al archivo equivocado, lo cual habría bloqueado silenciosamente la verificación de Gemini que pedía memory/NEXT_STEPS.md como prioridad actual.

Estado:

Aprobada.

---

## DEC-024

Fecha:

2026-08-04

Decisión:

Se corrigen contradicciones internas detectadas en memory/CURRENT_STATE.md, introducidas al integrar DEC-023 sobre una versión desactualizada del archivo: el campo "Fase" decía "en curso" cuando ROADMAP.md ya marca Fase 1 como "Cerrada"; la sección 003-CEO todavía listaba el modelo de negocio como "propuesta A/B/C, pendiente de elección" pese a que DEC-014 lo resolvió hace semanas; la sección del Agente Investigador de Producto seguía marcada "con proveedor provisional simulado, pendiente reemplazar por Gemini" pese a que la propia DEC-023 (en el mismo archivo) confirma la verificación contra la API real; y la sección de conexión a PostgreSQL/Redis conservaba la frase "todavía no hay esquema de negocio", contradicha por la sección de 006-BaseDatos inmediatamente debajo. Se corrige además el mismo error de "Fase 1 en curso" en README.md, y se sincroniza la fecha de "Última actualización" en memory/CONTEXT.md (seguía en 2026-07-30).

Motivo:

Una revisión del usuario detectó las contradicciones. El patrón de fondo: cuando una actualización de memoria se hace insertando una decisión nueva sobre una copia del archivo que no es la más reciente, el resultado mezcla estados de distintos momentos del proyecto dentro del mismo documento. La corrección no solo arregla el contenido; deja registrado el patrón para evitar repetirlo.

Estado:

Aprobada.

---

## DEC-025

Fecha:

2026-08-04

Decisión:

Se completa el volumen docs/004-Backend, documentando el backend tal como existe hoy en código (a diferencia de la disciplina habitual de documentar antes de programar, aplicada aquí en retrospectiva porque el código avanzó más rápido de lo previsto): arquitectura de módulos y ciclo de vida de una request (01), catálogo real de los 3 endpoints existentes (02), el patrón de 6 pasos para agregar un agente nuevo extraído del proceso real seguido con el Agente Investigador de Producto, incluyendo una sección explícita de "qué no repetir" (03), y las convenciones de manejo de errores y configuración ya en uso (04).

Motivo:

Con un segundo agente probablemente en camino (ver memory/NEXT_STEPS.md), documentar el patrón ya usado evita que cada agente nuevo reinvente su propia estructura, y cierra la brecha de tener código real sin su volumen de documentación correspondiente.

Estado:

Aprobada.

---

## DEC-026

Fecha:

2026-08-04

Decisión:

Se elige Analítica Básica, entre los candidatos de docs/007-Agentes/04-Registro-de-Agentes.md (SEO, Contenido, Atención al cliente, Analítica básica, Marketing), como el segundo agente de Merchly AI en recibir contrato técnico, siguiendo el paso 1 del patrón de docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md. Se redacta docs/007-Agentes/05-Agente-Analitica-Basica.md con las 10 secciones del contrato estándar, y se registra en docs/007-Agentes/04-Registro-de-Agentes.md en etapa "Contrato en Diseño" (docs/007-Agentes/02-Ciclo-de-Vida-de-Agentes.md, sección 1.2) — pendiente de que el CTO lo revise y lo pase a "Contrato Aprobado" antes de iniciar implementación en 004-Backend.

El contrato acota deliberadamente el alcance del agente a la única fuente de datos real que existe hoy (la tabla productos_candidatos, poblada por el Agente Investigador de Producto) más la actividad de ese mismo agente, en vez de especificar analítica de ventas o tráfico de tienda — esos datos no existen todavía porque Fase 2 (Frontend/tienda) no ha comenzado. El agente queda especificado en Nivel de permiso 0 (solo lectura), el más bajo de la escala de 001-Arquitectura/03-Arquitectura-de-Agentes.md, sin memoria operativa ni histórica propia.

Motivo:

Mantener la disciplina de no documentar (ni implementar) sobre datos hipotéticos, coherente con cómo se especificó el Investigador de Producto y con el criterio de completitud de 007-Agentes/01-Contrato-Tecnico-Estandar.md, sección 3. La ampliación a métricas de negocio queda anotada explícitamente en la sección 9 del contrato como revisión futura (versión minor), condicionada al cierre de Fase 2, no como pendiente abierto de esta versión.

Estado:

Aprobada (la decisión de qué agente especificar; el contrato del agente en sí queda "Contrato en Diseño", pendiente de aprobación técnica separada por el CTO).

---

## DEC-027

Fecha:

2026-08-05

Decisión:

El CTO aprueba el contrato técnico del Agente de Analítica Básica (docs/007-Agentes/05-Agente-Analitica-Basica.md), pasándolo de "Contrato en Diseño" a "Contrato Aprobado". Se implementan los pasos 3 a 6 del patrón de docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md (el paso 2 no aplica: el contrato es de solo lectura, no requiere tabla nueva): se reutilizan los schemas Pydantic ya existentes (backend/app/schemas/analitica_basica.py, escritos en una sesión previa junto con el contrato), se agrega el servicio de orquestación (AgenteAnaliticaBasica), que agrega en Python — no en SQL — las filas de productos_candidatos filtradas por fecha/categoría/mercado, y el endpoint POST /agentes/analitica-basica. A diferencia del Investigador de Producto, este agente no usa ningún proveedor de IA: es agregación determinística sobre datos ya persistidos (Nivel de permiso 0, solo lectura). Se agregan 15 tests nuevos (38 en total en el proyecto), todos en verde, y se verificó el servidor real end-to-end (422 en validaciones, 500 esperado sin PostgreSQL real disponible en este entorno).

Motivo:

Resolver el conflicto identificado entre dos líneas de trabajo paralelas (esta sesión había avanzado con un Agente de Contenido, contrato con su propio DEC-026; otra sesión avanzó con Analítica Básica, sobrescribiendo esa decisión). El usuario eligió explícitamente continuar con Analítica Básica.

Estado:

Aprobada.

---

## DEC-028

Fecha:

2026-08-11

Decisión:

Se aprueba el contrato técnico del Agente de Marketing (docs/007-Agentes/06-Agente-de-Marketing.md), tercer agente de Merchly AI: recibe entre 1 y 10 productos ya aprobados en catálogo (estado = 'en_catalogo') y canales objetivo, y genera ángulos de campaña, copy por canal, público objetivo sugerido y una distribución de presupuesto orientativa, sin ejecutar publicación ni gasto real. Corresponde al rol "Marketing IA" ya existente en docs/100-Organizacion/06-Agentes-IA.md (proveedor asignado: ChatGPT). No persiste resultados en esta versión (a diferencia del Investigador de Producto), por no existir todavía una necesidad real de historial de campañas. Se actualiza docs/007-Agentes/04-Registro-de-Agentes.md.

Motivo:

Tercer paso del patrón de 6 pasos (docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md): paso 1 (contrato técnico), siguiendo la disciplina "documentación antes que código". El usuario eligió explícitamente Marketing como tercer agente entre las opciones disponibles (SEO, atención al cliente, marketing, retomar Contenido, o documentar 005-Frontend).

Estado:

Aprobada.

---

## DEC-029

Fecha:

2026-08-11

Decisión:

Se implementa en código el Agente de Marketing (pasos 3 a 6 del patrón, ver DEC-028 para el paso 1): schemas Pydantic (productos_candidato_ids hasta 10, canales_objetivo sin duplicados, idioma ISO 639-1, tono, presupuesto opcional), proveedor abstracto con implementación provisional simulada (ProveedorMarketingSimulado, claramente marcada como no apta para campañas reales), el servicio de orquestación (AgenteMarketing: valida que cada producto exista y esté en estado 'en_catalogo' antes de invocar al proveedor, reintentos según contrato sección 8, distribución de presupuesto uniforme determinística, nunca persiste nada) y el endpoint POST /agentes/marketing. Se agregan 19 tests nuevos (57 en total en el proyecto), todos en verde, más verificación manual del servidor real (422 en validaciones, 500 esperado sin PostgreSQL real disponible en este entorno).

Motivo:

Completar el patrón de 6 pasos para el tercer agente, siguiendo el mismo orden ya validado con el Investigador de Producto: proveedor simulado primero, proveedor real (ChatGPT) queda como trabajo futuro explícito.

Estado:

Aprobada.

---

## DEC-030

Fecha:

2026-09-02

Decisión:

Se documenta en retrospectiva y se corrige el sistema de Decisiones Humanas (`decision_records`, `decision_context`, `decision_evidence`, `decision_outcomes`; endpoints `POST /decisiones`, `GET /decisiones/{id}`, `GET /productos-candidatos`, `GET /productos-candidatos/{id}`), implementado en código en una sesión anterior (migración fechada 2026-08-26) sin contrato previo, sin tests y sin registrar ningún DEC — violando la disciplina "documentación antes que código" y la práctica de testear todo código nuevo. Se detectó en una auditoría general del repositorio.

Al auditar el código se encontró además un bug funcional real: el modelo SQLAlchemy `DecisionRecord` no declaraba las relaciones ORM hacia `DecisionContext` ni `DecisionEvidence`. El efecto era silencioso: `context_data` y `evidencias` sí se guardaban correctamente en sus tablas al hacer `POST /decisiones`, pero la API siempre los devolvía vacíos (`null` / `[]`) en la respuesta y en cualquier `GET /decisiones/{id}` posterior — la información quedaba persistida pero invisible, sin ningún error que lo delatara.

Se corrige agregando las relaciones faltantes (`relationship()`, con `back_populates` y `cascade="all, delete-orphan"`), cargándolas explícitamente con `selectinload` (necesario en sesión async), y separando la conversión a `DecisionOutput` en una función propia (`_a_decision_output`) en vez de depender de la serialización automática de Pydantic sobre el ORM. Se agregan 20 tests nuevos (77 en total en el proyecto): 5 sobre el modelo y la conversión (incluyendo una reproducción directa del bug — revertir el fix hace fallar 2 de esos tests), 5 sobre el servicio `registrar_decision` con sesión mockeada, y 10 sobre los 4 endpoints HTTP nuevos. Se documenta el feature en `docs/004-Backend/02-Referencia-de-Endpoints.md` (secciones 6-9) y `docs/006-BaseDatos/02-Esquema-Fase1.md` (sección 4), incluyendo la limitación explícita de que `user_id` es texto libre sin autenticación real todavía (pendiente de `013-Seguridad`).

Motivo:

Cerrar la brecha de tener código real en producción sin contrato, sin tests y sin decisión registrada — exactamente el tipo de drift entre memoria y código que el proyecto ya identificó como riesgo recurrente de sesiones paralelas. El bug de las relaciones ORM es además un caso concreto de por qué la disciplina de testing importa: sin tests, este tipo de pérdida silenciosa de datos en la respuesta de la API puede pasar desapercibida indefinidamente.

Estado:

Aprobada.
