# MERCHLY AI NEXT STEPS


## Prioridad actual

Elegir entre: (a) integrar el proveedor real de ChatGPT para el Agente de Marketing (cerrando su único pendiente), o (b) especificar un cuarto agente (SEO o atención al cliente), siguiendo docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md.


---

# Próximas tareas


## 1

Integrar ChatGPT real para el Agente de Marketing:

- Documentar el prompt en docs/010-Prompts antes del código (mismo orden ya usado con Gemini para el Investigador de Producto).
- Implementar ProveedorMarketingChatGPT en backend/app/services/proveedores/, con tests usando un cliente mockeado.
- La verificación final contra la API real de OpenAI corresponde al usuario (no se puede hacer desde este entorno de ejecución, sin acceso de red a proveedores externos).


---

## 2

Elegir y especificar el cuarto agente:

- Candidatos, según docs/007-Agentes/04-Registro-de-Agentes.md: SEO, atención al cliente (primer nivel).
- Seguir los 6 pasos documentados en docs/004-Backend/03-Patron-para-Agregar-un-Agente-Nuevo.md.


---

## 3

Evaluar si retomar el Agente de Contenido:

- Su contrato técnico se redactó pero fue descartado cuando el proyecto avanzó con Analítica Básica en su lugar (dos sesiones en paralelo, ver DEC-026/DEC-027).
- Si sigue siendo prioritario para el negocio, requiere una nueva decisión explícita y volver a redactar su contrato (el original ya no está en el repo).


---

## 4

Evaluar docs/005-Frontend:

- A diferencia de 004-Backend (documentado después del código, por necesidad), conviene decidir si documentar el frontend antes de escribir su primera línea de código.


---

## 5

Endpoints pendientes identificados en docs/004-Backend/02-Referencia-de-Endpoints.md:

- Cambiar estado de un producto candidato (candidato → en_catalogo / descartado) — requiere autenticación/autorización humana, todavía no diseñada (013-Seguridad sigue vacío). Este endpoint es además un prerequisito de negocio real para el Agente de Marketing, que solo opera sobre productos en 'en_catalogo'.
- Listar/consultar productos candidatos individuales.


---

# Objetivo siguiente etapa

Con tres agentes funcionando (uno con IA real, uno sin IA, uno con IA simulada), el patrón de 6 pasos está validado en varios escenarios. El cuello de botella real ahora es que no existe forma de mover un producto de 'candidato' a 'en_catalogo' — sin ese endpoint, el Agente de Marketing no tiene productos reales sobre los que operar en un flujo end-to-end genuino.
