# MERCHLY AI NEXT STEPS


## Prioridad actual

Obtener aprobación del CTO para docs/007-Agentes/05-Agente-Analitica-Basica.md (Agente de Analítica Básica, DEC-026) y, una vez aprobado, avanzar los pasos 2-6 del patrón de docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md.


---

# Próximas tareas


## 1

Llevar el Agente de Analítica Básica a código, una vez aprobado el contrato:

- Paso 1 (contrato técnico) completado: docs/007-Agentes/05-Agente-Analitica-Basica.md.
- Paso 2 (esquema): no aplica — el agente es de solo lectura sobre productos_candidatos, no persiste nada nuevo.
- Paso 3: schemas Pydantic en backend/app/schemas/ que repliquen las secciones 2 y 3 del contrato.
- Paso 4: proveedor — evaluar si hace falta un LLM (para redactar el resumen) o si es agregación SQL pura; si usa LLM, simulado primero, prompt documentado en 010-Prompts antes del proveedor real.
- Paso 5: servicio de orquestación (backend/app/services/) — solo lectura, sin reintentos con backoff (ver sección 8 del contrato).
- Paso 6: endpoint nuevo (ej. GET /agentes/analitica-basica) en backend/app/api/agentes.py o un router nuevo.


---

## 2

Evaluar docs/005-Frontend:

- A diferencia de 004-Backend (documentado después del código, por necesidad), conviene decidir si documentar el frontend antes de escribir su primera línea de código, volviendo a la disciplina "documentación antes que código" ahora que la brecha de 004-Backend ya se cerró.


---

## 3

Endpoints pendientes identificados en docs/004-Backend/02-Referencia-de-Endpoints.md:

- Cambiar estado de un producto candidato (candidato → en_catalogo / descartado) — requiere autenticación/autorización humana, todavía no diseñada (013-Seguridad sigue vacío).
- Listar/consultar productos candidatos ya persistidos.


---

# Objetivo siguiente etapa

Con el patrón de construcción de agentes ya documentado (docs/004-Backend) y probado de punta a punta con el primer agente, el proyecto está listo para escalar horizontalmente: cada agente nuevo debería tomar menos esfuerzo que el anterior. El criterio de éxito del próximo agente es justamente ese — medir si efectivamente toma menos pasos que el primero.
