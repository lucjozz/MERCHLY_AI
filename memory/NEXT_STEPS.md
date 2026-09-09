# MERCHLY AI NEXT STEPS


## Prioridad actual

Aprobar el diseño de docs/013-Seguridad (DEC-031, Contrato en Diseño) e implementarlo: tabla `usuarios`, JWT, y proteger los 4 endpoints de acción (agentes + decisiones). Hasta que esto se implemente, `POST /decisiones` sigue aceptando `user_id` como texto libre sin validar. En paralelo, sigue pendiente elegir entre: (a) integrar el proveedor real de ChatGPT para el Agente de Marketing, o (b) especificar un cuarto agente (SEO o atención al cliente).


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

Resuelto (ver DEC-030): `POST /decisiones` ya permite cambiar el estado de un producto candidato (candidato → en_catalogo / descartado), y `GET /productos-candidatos` / `GET /productos-candidatos/{id}` ya permiten listar y consultar productos individuales. Pendiente derivado de esto: `user_id` en `POST /decisiones` sigue siendo texto libre sin autenticación real — requiere 013-Seguridad para cerrarse del todo.

## 6

Implementar 013-Seguridad (ver DEC-031 — el diseño ya está completo, falta el código):

- Orden fijo definido en docs/013-Seguridad/03-Alcance-y-Plan-de-Migracion.md sección 3.4: tabla `usuarios` + migración → seed del usuario admin_principal (Lucas) → `POST /auth/login` + `GET /auth/me` → dependencia `usuario_actual` → aplicar a los 4 endpoints de acción (quitando `user_id` del body de `POST /decisiones`) → actualizar 004-Backend/02-Referencia-de-Endpoints.md → tests.
- Requiere aprobación final del CTO sobre los detalles técnicos del documento antes de arrancar (README.md del volumen, "Estado de Aprobación").

## 7

Evaluar si usar `decision_outcomes`:

- La tabla existe (migración `202608260001`) pero ningún endpoint la escribe ni la lee todavía.
- Pensada para medir después si una decisión (ej. aprobar un producto) funcionó o no — relevante recién cuando haya datos de ventas/tráfico reales.


---

# Objetivo siguiente etapa

Con tres agentes funcionando (uno con IA real, uno sin IA, uno con IA simulada) y el sistema de Decisiones ya operativo y corregido (DEC-030), el flujo candidato → decisión humana → en_catalogo → marketing es end-to-end por primera vez. El cuello de botella real ahora es la falta de autenticación real (013-Seguridad) y, en paralelo, decidir el cuarto agente o cerrar ChatGPT para Marketing.
