# 03-Agente-Investigador-de-Producto.md

---

title: Contrato Técnico — Agente Investigador de Producto
document: 007-03
version: 1.0.0
status: Aprobado — primer agente con contrato técnico completo (criterio de cierre Fase 0)
owner: CTO
last_updated: 2026-07-26
next_review: 2027-01-26
related:

* 01-Contrato-Tecnico-Estandar.md
* ../100-Organizacion/06-Agentes-IA.md
* ../003-CEO/03-Criterios-de-Exito-Fase0.md

---

# Agente Investigador de Producto

## Propósito de este documento

Especificar, bajo el esquema de `01-Contrato-Tecnico-Estandar.md`, el primer agente IA de Merchly AI con contrato técnico completo. Se eligió el Agente Investigador de Producto como primer caso porque:

* Corresponde a la primera área operativa listada en `000-Constitucion/05-Objetivos.md` (OBJ-004).
* Es el punto de partida natural de cualquier tienda: sin investigación de producto no hay catálogo que operar.
* Tiene entradas y salidas simples de especificar (no depende de otros agentes todavía construidos), lo que lo hace apto como primer contrato de referencia.

Este agente todavía **no está implementado en código** (etapa "Contrato Aprobado" del ciclo de vida, ver `02-Ciclo-de-Vida-de-Agentes.md`). Su implementación corresponde a Fase 2 (Núcleo de Plataforma).

---

# 1. Identidad

* **Nombre:** Agente Investigador de Producto.
* **Rol organizacional asociado:** "Investigador IA" (`100-Organizacion/06-Agentes-IA.md`), proveedor actual asignado: Gemini.
* **Versión del contrato:** 1.0.0.
* **Propósito en una frase:** dado un nicho o categoría de e-commerce, identificar productos con potencial de venta y devolver una lista estructurada con evidencia de demanda y competencia.
* **Responsable humano:** CEO (validación de negocio) / CTO (validación técnica de la integración).

---

# 2. Entradas (Input Schema)

| Campo | Tipo | Obligatorio | Origen |
|---|---|---|---|
| `categoria` | string | Sí | Usuario humano o CEO IA |
| `mercado_objetivo` | string (código de país, ISO 3166-1 alpha-2) | Sí | Usuario humano |
| `presupuesto_max_producto` | number (moneda: USD) | No | Usuario humano |
| `excluir_marcas` | array de strings | No | Usuario humano |
| `cantidad_resultados` | integer (default: 10, máx: 50) | No | Usuario humano |

**Validaciones mínimas antes de procesar:**

* `categoria` no puede estar vacío ni ser una categoría prohibida (ver sección 7, Límites).
* `mercado_objetivo` debe ser un código ISO 3166-1 alpha-2 válido.
* `cantidad_resultados` se trunca a 50 si excede ese valor; no se rechaza la solicitud completa.

---

# 3. Salidas (Output Schema)

Formato: JSON. Un objeto por producto encontrado, dentro de una lista `productos`:

```json
{
  "productos": [
    {
      "nombre_producto": "string",
      "categoria": "string",
      "precio_estimado_proveedor": "number (USD)",
      "precio_sugerido_venta": "number (USD)",
      "nivel_demanda_estimado": "string (alto | medio | bajo)",
      "nivel_competencia_estimado": "string (alto | medio | bajo)",
      "fuentes_evidencia": ["string (URL o referencia)"],
      "riesgos_identificados": ["string"]
    }
  ],
  "metadata": {
    "categoria_consultada": "string",
    "mercado_objetivo": "string",
    "fecha_investigacion": "string (ISO 8601)",
    "total_productos_evaluados": "integer",
    "total_productos_devueltos": "integer"
  }
}
```

**Destino:** respuesta directa al usuario humano que solicitó la investigación; opcionalmente, persistencia en base de datos (`006-BaseDatos`, cuando exista tabla de catálogo candidato) para consulta posterior por otros agentes (ej. futuro Agente de Precios).

---

# 4. Herramientas Permitidas

* Búsqueda web (para evidencia de demanda y tendencias).
* Consulta a APIs de proveedores/marketplaces ya autorizadas por el CTO (a definir el listado exacto en la implementación de `004-Backend`; hasta entonces, ninguna API de proveedor está autorizada).
* Ninguna herramienta de ejecución de compra, pago, o publicación de producto está permitida bajo este contrato.

Cualquier herramienta no listada explícitamente aquí está prohibida por defecto, conforme a `01-Contrato-Tecnico-Estandar.md`, sección 2.4.

---

# 5. Memoria

* **Memoria temporal:** contexto de la investigación en curso (categoría, mercado, resultados parciales) — vive solo durante la ejecución, no persiste.
* **Memoria operativa:** criterios de evaluación de demanda/competencia reutilizables entre ejecuciones — a definir su almacenamiento concreto al implementarse (`006-BaseDatos` o archivo de configuración versionado).
* **Memoria histórica:** registro de investigaciones previas por categoría, para evitar recomendar productos ya descartados — se persiste en `memory/` mientras no exista base de datos operativa; migra a `006-BaseDatos` en Fase 2.

---

# 6. Permisos

* **Nivel:** 1 — Análisis y recomendaciones (escala de `001-Arquitectura/03-Arquitectura-de-Agentes.md`).
* **Justificación:** el agente investiga y recomienda, pero no ejecuta ninguna acción sobre el catálogo real, proveedores o presupuesto. No requiere nivel 2 o superior porque no hay ejecución de tareas transaccionales en su alcance actual.

---

# 7. Límites Explícitos

El agente **no puede**:

* Agregar productos al catálogo real de una tienda sin aprobación humana.
* Contactar proveedores ni iniciar negociaciones.
* Investigar categorías prohibidas por política de la empresa (ej. productos regulados, ilegales, o que violen `000-Constitucion/03-Valores.md`).
* Tomar la decisión final de qué producto se vende; solo recomienda con evidencia.

**Requiere aprobación humana explícita antes de:**

* Que cualquier producto recomendado pase a estado "en catálogo".
* Ampliar el listado de proveedores/APIs consultables (sección 4).

Coherente con DEC-008: este agente nunca ocupa el rol de Aprobador en la Matriz RACI (`100-Organizacion/07-Matriz-RACI.md`).

---

# 8. Manejo de Errores

* Si una fuente de búsqueda falla o no responde: se excluye esa fuente y se continúa con las demás disponibles; no se aborta la investigación completa por el fallo de una sola fuente.
* Política de reintentos: máximo 2 reintentos por fuente, con espera de 5 segundos entre intentos.
* Si menos del 50% de las fuentes esperadas responden, el agente marca el resultado como "confianza baja" en `metadata` y notifica al humano responsable en lugar de presentar el resultado como definitivo.
* Escalamiento: si la categoría solicitada no puede evaluarse por falta total de datos, el agente devuelve una lista vacía con `riesgos_identificados` explicando el motivo, en vez de inventar productos.

---

# 9. Métricas de Evaluación

| Métrica | Definición | Umbral inicial |
|---|---|---|
| Precisión | % de productos recomendados que, tras revisión humana, se consideran viables | A definir tras las primeras 10 ejecuciones reales |
| Velocidad | Tiempo total de una investigación completa | Objetivo inicial: menor a 5 minutos |
| Coste | Coste de API/modelo por investigación | A monitorear desde la primera ejecución (ver `003-CEO/02-Modelo-de-Negocio.md`, sección 3) |
| Impacto | Nº de productos recomendados que efectivamente se incorporan al catálogo | A definir tras Fase 2 |
| Seguridad | Nº de veces que el agente respeta los límites de la sección 7 sin intervención humana correctiva | Debe ser 100%; cualquier incumplimiento se registra como incidente |

---

# 10. Registro de Actividad

Por cada ejecución se registra:

* Fecha y hora (ISO 8601).
* Entradas recibidas (sección 2).
* Salida generada (sección 3), o motivo de fallo si no se pudo completar.
* Duración de la ejecución.
* Coste estimado (si aplica, según proveedor de IA usado).
* Responsable humano que solicitó la investigación.

**Dónde se registra:** mientras no exista base de datos operativa, en `memory/` (archivo de log por agente); migra a `006-BaseDatos` en Fase 2, conforme a `02-Ciclo-de-Vida-de-Agentes.md`.

---

# Resumen Ejecutivo para IA

El Agente Investigador de Producto es el primer agente de Merchly AI con contrato técnico completo: recibe categoría, mercado y presupuesto; devuelve una lista estructurada de productos candidatos con evidencia de demanda y competencia. Opera en nivel de permiso 1 (análisis y recomendación), no ejecuta ninguna acción transaccional, y todo resultado requiere validación humana antes de incorporarse al catálogo real. Su implementación en código corresponde a Fase 2 (Núcleo de Plataforma).
