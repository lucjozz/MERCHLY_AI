# 06-Agente-de-Marketing.md

---

title: Contrato Técnico — Agente de Marketing
document: 007-06
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-08-11
next_review: 2027-02-11
related:

* 01-Contrato-Tecnico-Estandar.md
* ../100-Organizacion/06-Agentes-IA.md
* ../006-BaseDatos/02-Esquema-Fase1.md

---

# Agente de Marketing

## Propósito de este documento

Especificar, bajo el esquema de `01-Contrato-Tecnico-Estandar.md`, el tercer agente de Merchly AI con contrato técnico completo. Se eligió el Agente de Marketing como tercer caso porque:

* Es el paso natural siguiente a tener productos ya aprobados en catálogo (`estado = 'en_catalogo'` en `productos_candidatos`): sin una propuesta de campaña, un producto aprobado no genera tráfico ni ventas.
* Reutiliza el mismo patrón de proveedor de IA intercambiable ya validado con el Agente Investigador de Producto (simulado primero, proveedor real después), a diferencia del Agente de Analítica Básica, que no usa ningún proveedor.
* Corresponde al rol **"Marketing IA"** ya existente en `100-Organizacion/06-Agentes-IA.md` (proveedor asignado: ChatGPT), a diferencia del Agente de Contenido (descartado, DEC-026/027), que había requerido una asignación provisional por no tener rol dedicado.

Este agente todavía **no está implementado en código** (etapa "Contrato Aprobado" del ciclo de vida, ver `02-Ciclo-de-Vida-de-Agentes.md`).

---

# 1. Identidad

* **Nombre:** Agente de Marketing.
* **Rol organizacional asociado:** "Marketing IA" (`100-Organizacion/06-Agentes-IA.md`), proveedor actual asignado: ChatGPT.
* **Versión del contrato:** 1.0.0.
* **Propósito en una frase:** dado uno o más productos ya aprobados en catálogo, generar una propuesta de campaña publicitaria (ángulos de mensaje, copy por canal, público objetivo sugerido) sin ejecutar ninguna publicación ni gasto real.
* **Responsable humano:** CMO (validación de estrategia y tono de marca) / CTO (validación técnica de la integración).

---

# 2. Entradas (Input Schema)

| Campo | Tipo | Obligatorio | Origen |
|---|---|---|---|
| `productos_candidato_ids` | array de UUID (mín. 1, máx. 10) | Sí | Usuario humano |
| `canales_objetivo` | array de string (valores: `busqueda_paga`, `redes_sociales`, `email`) | Sí (mín. 1) | Usuario humano |
| `idioma_destino` | string (código ISO 639-1) | Sí | Usuario humano |
| `tono` | string (uno de: `neutral`, `entusiasta`, `tecnico`, `premium`) | No (default: `neutral`) | Usuario humano |
| `presupuesto_mensual_referencia` | number (USD) | No | Usuario humano — solo para dimensionar la propuesta, nunca para ejecutar gasto |

**Validaciones mínimas antes de procesar:**

* Cada `producto_candidato_id` debe corresponder a una fila existente, no eliminada lógicamente, **y con `estado = 'en_catalogo'`** en `productos_candidatos`. Un producto en `candidato` o `descartado` se rechaza explícitamente — coherente con la regla de negocio de que solo un producto ya aprobado por un humano recibe inversión de marketing (ver `006-BaseDatos/02-Esquema-Fase1.md`, sección 3).
* `canales_objetivo` no puede estar vacío ni contener valores fuera del enum.
* `idioma_destino` debe ser un código ISO 639-1 válido de 2 letras.
* `presupuesto_mensual_referencia`, si se provee, debe ser mayor a 0.

---

# 3. Salidas (Output Schema)

Formato JSON:

```json
{
  "productos_candidato_ids": ["uuid"],
  "angulos_de_campana": ["string"],
  "copy_por_canal": {
    "busqueda_paga": [{"titulo": "string", "cuerpo": "string"}],
    "redes_sociales": [{"titulo": "string", "cuerpo": "string"}],
    "email": [{"titulo": "string", "cuerpo": "string"}]
  },
  "publico_objetivo_sugerido": "string",
  "distribucion_presupuesto_sugerida": {"busqueda_paga": 0.5, "redes_sociales": 0.3, "email": 0.2},
  "advertencias": ["string"],
  "metadata": {
    "idioma_destino": "string",
    "tono": "string",
    "fecha_generacion": "string (ISO 8601)",
    "campana_id": "uuid"
  }
}
```

* `distribucion_presupuesto_sugerida`: proporciones (suman 1.0) entre los canales solicitados — **una sugerencia orientativa, nunca una instrucción de gasto ejecutable**. Solo se incluye si se proveyó `presupuesto_mensual_referencia`.
* `advertencias`: igual criterio que el Agente de Contenido — cualquier afirmación que el agente no pudo verificar con los datos del producto (`fuentes_evidencia`, `riesgos_identificados` en `productos_candidatos`) se señala aquí, nunca se omite silenciosamente.

**Destino:** respuesta directa al usuario humano. **No se persiste en base de datos en esta versión** — a diferencia del Agente Investigador de Producto, el resultado de este agente no es un dato de negocio que otros procesos consulten después, sino una propuesta para revisión humana inmediata. Se evaluará agregar una tabla de historial de campañas en una iteración futura si se detecta una necesidad real de comparar versiones o auditar campañas pasadas (coherente con el Principio de Simplicidad, Norma 4 — no se construye persistencia especulativa).

---

# 4. Herramientas Permitidas

* Consulta de solo lectura a `productos_candidatos`, para obtener `nombre_producto`, `categoria`, `fuentes_evidencia` y `riesgos_identificados` de cada producto referenciado.
* Proveedor de IA (ver sección 1 — ChatGPT, o cualquier otro que lo sustituya conforme a las Reglas de Sustitución de Proveedor de `100-Organizacion/06-Agentes-IA.md`).

Explícitamente **prohibido**: cualquier API de plataforma publicitaria real (Google Ads, Meta Ads, etc.) — este agente no publica ni ejecuta gasto, solo genera texto y una distribución de presupuesto sugerida. Integrar una API de publicación real requeriría un contrato nuevo (o una revisión mayor de este), con su propia evaluación de `013-Seguridad`.

Cualquier herramienta no listada aquí está prohibida por defecto, conforme a `01-Contrato-Tecnico-Estandar.md`, sección 2.4.

---

# 5. Memoria

* **Memoria temporal:** los datos de los productos candidatos consultados y el contexto de la generación en curso — vive solo durante la ejecución.
* **Memoria operativa:** ninguna todavía. A futuro, podría incluir guías de tono de marca reutilizables entre campañas (mismo criterio que el Agente de Contenido: se agrega solo si se detecta una necesidad real, no de forma especulativa).
* **Memoria histórica:** ninguna en esta versión (ver sección 3 — no hay persistencia todavía).

---

# 6. Permisos

* **Nivel:** 1 — Análisis y recomendaciones (misma escala que el Agente Investigador de Producto y el Agente de Contenido descartado).
* **Justificación:** el agente genera una propuesta de campaña, pero no publica ningún anuncio ni ejecuta ningún gasto. Nivel 2 o superior se evaluaría solo si en el futuro se automatiza la publicación real en plataformas publicitarias, lo cual requeriría además una revisión de `013-Seguridad` (todavía vacío) por el riesgo financiero y de cumplimiento publicitario que eso implica.

---

# 7. Límites Explícitos

El agente **no puede**:

* Publicar ningún anuncio en ninguna plataforma real.
* Ejecutar o autorizar ningún gasto publicitario real — `distribucion_presupuesto_sugerida` es siempre una sugerencia, nunca una orden de ejecución.
* Generar campañas para un producto candidato que no esté en `estado = 'en_catalogo'`.
* Afirmar beneficios, certificaciones, o comparaciones con competidores que no estén respaldados por `fuentes_evidencia` del producto.
* Usar marcas, logos, o contenido de terceros protegido por derechos de autor.

**Requiere aprobación humana explícita antes de:**

* Que cualquier copy generado se publique en un canal real.
* Que la distribución de presupuesto sugerida se traduzca en una asignación real de gasto.

Coherente con DEC-008: este agente nunca ocupa el rol de Aprobador en la Matriz RACI.

---

# 8. Manejo de Errores

* Si algún `producto_candidato_id` no existe o no está en `estado = 'en_catalogo'`: se rechaza la solicitud completa antes de invocar al proveedor de IA (falla rápido, evita gastar cuota en una solicitud inválida) — mismo criterio que el Agente de Contenido.
* Si el proveedor de IA falla: máximo 2 reintentos, con espera de 5 segundos entre intentos (misma política que el Agente Investigador de Producto).
* Si tras agotar los reintentos el proveedor sigue fallando, se devuelve una respuesta vacía (sin ángulos ni copy) con la advertencia correspondiente, nunca contenido fabricado sin pasar por el modelo.
* Si alguno de los productos referenciados tiene `fuentes_evidencia` vacío, el agente genera una propuesta más genérica para ese producto y lo señala explícitamente en `advertencias`.

---

# 9. Métricas de Evaluación

| Métrica | Definición | Umbral inicial |
|---|---|---|
| Precisión | % de campañas aprobadas por un humano sin cambios mayores | A definir tras las primeras 10 ejecuciones reales |
| Velocidad | Tiempo total de una generación completa | Objetivo inicial: menor a 2 minutos |
| Coste | Coste de API/modelo por generación | A monitorear desde la primera ejecución |
| Impacto | % de campañas generadas que efectivamente se publican | A definir tras Fase 2 |
| Seguridad | Nº de veces que el agente respeta los límites de la sección 7 sin intervención humana correctiva | Debe ser 100%; cualquier incumplimiento se registra como incidente |

---

# 10. Registro de Actividad

Por cada ejecución se registra: fecha y hora, `productos_candidato_ids`, canales solicitados, entrada completa, salida generada (o motivo de fallo), duración, coste estimado, responsable humano que solicitó la generación. Mientras no exista persistencia dedicada (ver sección 3), se registra en `memory/` o en logs de la aplicación, igual que el criterio original del Agente Investigador de Producto antes de tener base de datos operativa.

---

# Resumen Ejecutivo para IA

El Agente de Marketing es el tercer agente de Merchly AI con contrato técnico completo: recibe entre 1 y 10 productos ya aprobados en catálogo (`estado = 'en_catalogo'`, nunca `candidato` ni `descartado`) y canales objetivo, y genera ángulos de campaña, copy por canal, público objetivo sugerido y una distribución de presupuesto orientativa — nunca ejecuta publicación ni gasto real. Nivel de permiso 1, misma política de reintentos que el Investigador de Producto. No persiste resultados en esta versión (a diferencia del Investigador de Producto), por no haber todavía una necesidad real de historial de campañas. Corresponde al rol "Marketing IA" ya existente en el catálogo organizacional, proveedor ChatGPT.
