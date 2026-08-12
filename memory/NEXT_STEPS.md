# MERCHLY AI NEXT STEPS


## Prioridad actual

Elegir y especificar el tercer agente (SEO, atención al cliente, o marketing), siguiendo el patrón de 6 pasos en docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md. Alternativamente, evaluar si retomar el Agente de Contenido (contrato descartado en favor de Analítica Básica) sigue siendo prioritario.


---

# Próximas tareas


## 1

Elegir y especificar el tercer agente:

- Candidatos, según docs/007-Agentes/04-Registro-de-Agentes.md: SEO, atención al cliente (primer nivel), marketing.
- Seguir los 6 pasos documentados en docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md.
- Si el agente necesita un proveedor de IA, documentar primero el prompt en docs/010-Prompts antes del código del proveedor real (orden ya validado con el Investigador de Producto).


---

## 2

Evaluar si retomar el Agente de Contenido:

- Su contrato técnico se redactó pero fue descartado cuando el proyecto avanzó con Analítica Básica en su lugar (dos sesiones en paralelo, ver DEC-026/DEC-027).
- Si sigue siendo prioritario para el negocio, requiere una nueva decisión explícita y volver a redactar su contrato (el original ya no está en el repo).


---

## 3

Evaluar docs/005-Frontend:

- A diferencia de 004-Backend (documentado después del código, por necesidad), conviene decidir si documentar el frontend antes de escribir su primera línea de código.


---

## 4

Endpoints pendientes identificados en docs/004-Backend/02-Referencia-de-Endpoints.md:

- Cambiar estado de un producto candidato (candidato → en_catalogo / descartado) — requiere autenticación/autorización humana, todavía no diseñada (013-Seguridad sigue vacío).
- Listar/consultar productos candidatos individuales.


---

# Objetivo siguiente etapa

Con dos agentes funcionando de punta a punta (uno con IA real, uno sin IA — agregación pura), el patrón de 6 pasos quedó validado en dos escenarios distintos. El tercer agente es una buena oportunidad para medir si el patrón sigue acelerando el desarrollo, o si necesita ajustes.
