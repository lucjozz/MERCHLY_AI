# MERCHLY AI NEXT STEPS


## Prioridad actual

Especificar el siguiente agente (SEO, contenido, atención al cliente, analítica básica o marketing), siguiendo el patrón de 6 pasos ya documentado en docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md.


---

# Próximas tareas


## 1

Elegir y especificar el siguiente agente:

- Candidatos, según docs/007-Agentes/04-Registro-de-Agentes.md: SEO, contenido, atención al cliente (primer nivel), analítica básica, marketing.
- Seguir los 6 pasos documentados en docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md: contrato técnico (007-Agentes) → esquema si hace falta (006-BaseDatos) → schemas Pydantic → proveedor (simulado primero, prompt en 010-Prompts, proveedor real después) → servicio de orquestación → endpoint.


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
