# 05-Agente-Analitica-Basica.md

---

title: Contrato Técnico — Agente de Analítica Básica
document: 007-05
version: 1.0.0
status: Aprobado
owner: CTO
last_updated: 2026-08-04
next_review: 2027-02-04
related:

* 01-Contrato-Tecnico-Estandar.md
* 03-Agente-Investigador-de-Producto.md
* ../100-Organizacion/06-Agentes-IA.md
* ../003-CEO/05-Metricas-y-Seguimiento.md
* ../006-BaseDatos/02-Esquema-Fase1.md

---

# Agente de Analítica Básica

## Propósito de este documento

Especificar, bajo el esquema de `01-Contrato-Tecnico-Estandar.md`, el segundo agente IA de Merchly AI con contrato técnico. Se eligió Analítica Básica como segundo agente (sobre otros candidatos de `04-Registro-de-Agentes.md`: SEO, Contenido, Atención al cliente, Marketing) por decisión explícita registrada en `memory/DECISIONS.md` (DEC-026).

## Alcance deliberadamente acotado a los datos que existen hoy

A diferencia del Investigador de Producto, este agente no genera datos nuevos: analiza los que ya existen. En el estado actual del proyecto (Fase 1 cerrada, Fase 2 — Frontend/tienda — no iniciada), la única fuente de datos real y persistida es la tabla `productos_candidatos` (salida del Agente Investigador de Producto), más los registros de ejecución de los agentes mismos.

Por eso este contrato **no incluye** analítica de ventas, tráfico o comportamiento de usuario final — esos datos no existen todavía porque no hay tienda operando (`ROADMAP.md`, Fase 2). Incluirlos ahora sería especificar sobre datos hipotéticos, lo cual contradice la disciplina de `002-CTO/02-Metodologia-Desarrollo.md`. Cuando Fase 2 cierre y exista una tienda con tráfico real, este contrato debe revisarse (versión minor) para incorporar esas métricas — ver sección 9.

Este agente cubre el rol organizacional "Analista IA" (`100-Organizacion/06-Agentes-IA.md`), cuyo propósito declarado —"investigación actualizada de mercado, tecnología y tendencias"— se interpreta aquí, en su primera versión, de forma restringida: análisis del catálogo de productos candidatos generado internamente, no investigación externa de mercado (eso ya lo cubre el Investigador de Producto).

---

# 1. Identidad

* **Nombre:** Agente de Analítica Básica.
* **Rol organizacional asociado:** "Analista IA" (`100-Organizacion/06-Agentes-IA.md`), proveedor actual asignado al rol: Perplexity — este agente, en su primera versión, no necesita búsqueda externa, por lo que puede implementarse con un proveedor distinto sin conflicto (ver `100-Organizacion/06-Agentes-IA.md`, "Los modelos son intercambiables; los roles son permanentes").
* **Versión del contrato:** 1.0.0.
* **Propósito en una frase:** dado un rango de fechas y filtros opcionales, generar un resumen estadístico del catálogo de productos candidatos (por categoría, nivel de demanda/competencia y estado) y de la actividad del Agente Investigador de Producto, para apoyar decisiones humanas sobre qué candidatos avanzan a catálogo real.
* **Responsable humano:** CEO (uso del reporte para decisiones de negocio) / CTO (validación técnica).

---

# 2. Entradas (Input Schema)

| Campo | Tipo | Obligatorio | Origen |
|---|---|---|---|
| `fecha_desde` | string (fecha ISO 8601) | No (default: hace 30 días) | Usuario humano |
| `fecha_hasta` | string (fecha ISO 8601) | No (default: hoy) | Usuario humano |
| `categoria` | string | No (sin filtro = todas) | Usuario humano |
| `mercado_objetivo` | string (ISO 3166-1 alpha-2) | No (sin filtro = todos) | Usuario humano |
| `agrupar_por` | string (enum: `categoria` \| `estado` \| `nivel_demanda_estimado` \| `nivel_competencia_estimado`, default: `categoria`) | No | Usuario humano |

**Validaciones mínimas antes de procesar:**

* `fecha_desde` no puede ser posterior a `fecha_hasta`.
* El rango de fechas no puede exceder 365 días (evita reportes que escaneen toda la tabla sin límite razonable).
* `mercado_objetivo`, si se provee, debe ser un código ISO 3166-1 alpha-2 válido (misma regla que el Investigador de Producto).
* `agrupar_por` debe ser uno de los cuatro valores permitidos; cualquier otro valor se rechaza (no se asume un default silencioso ante un valor inválido, para no confundir "no especificado" con "especificado mal").

---

# 3. Salidas (Output Schema)

Formato: JSON.

```json
{
  "periodo": {
    "fecha_desde": "string (ISO 8601)",
    "fecha_hasta": "string (ISO 8601)"
  },
  "resumen_catalogo": {
    "total_productos_candidatos": "integer",
    "agrupado_por": "string (categoria | estado | nivel_demanda_estimado | nivel_competencia_estimado)",
    "grupos": [
      {
        "clave": "string",
        "cantidad": "integer",
        "porcentaje_del_total": "number"
      }
    ]
  },
  "tasa_conversion_catalogo": {
    "candidato": "integer",
    "en_catalogo": "integer",
    "descartado": "integer",
    "tasa_candidato_a_en_catalogo": "number (0-1)"
  },
  "actividad_agente_investigador": {
    "total_investigaciones": "integer",
    "promedio_productos_por_investigacion": "number",
    "categorias_mas_investigadas": ["string"]
  },
  "metadata": {
    "fecha_generacion_reporte": "string (ISO 8601)",
    "filtros_aplicados": "object (eco de la sección 2)"
  }
}
```

**Destino:** respuesta directa al usuario humano que solicitó el reporte (CEO/CTO). No se persiste por defecto (es un reporte derivado, recalculable en cualquier momento a partir de `productos_candidatos`); si en el futuro se requiere historial de reportes generados, se evalúa como cambio minor del contrato.

---

# 4. Herramientas Permitidas

* Lectura (`SELECT`) de la tabla `productos_candidatos` vía la sesión de base de datos inyectada por el backend.
* Ninguna otra tabla, API externa, ni herramienta de búsqueda está autorizada en esta versión del contrato.
* Explícitamente prohibido: cualquier operación de escritura (`INSERT`/`UPDATE`/`DELETE`) sobre `productos_candidatos` u otra tabla — este agente es de solo lectura.

Cualquier herramienta no listada aquí está prohibida por defecto, conforme a `01-Contrato-Tecnico-Estandar.md`, sección 2.4.

---

# 5. Memoria

* **Memoria temporal:** los filtros y el rango de fechas de la consulta en curso — vive solo durante la ejecución, no persiste.
* **Memoria operativa:** ninguna. Este agente no tiene criterios propios que deba recordar entre ejecuciones (a diferencia del Investigador de Producto); cada reporte se calcula desde cero sobre los datos vigentes en `productos_candidatos`.
* **Memoria histórica:** ninguna propia. La "historia" que analiza es la de otro agente (`productos_candidatos`, poblada por el Investigador de Producto); este agente no mantiene su propio historial de investigaciones, solo el registro de actividad de la sección 10.

---

# 6. Permisos

* **Nivel:** 0 — Solo lectura (escala de `001-Arquitectura/03-Arquitectura-de-Agentes.md`).
* **Justificación:** es el nivel más bajo posible porque el agente únicamente lee y agrega datos ya existentes; no genera recomendaciones nuevas (a diferencia del Investigador de Producto, que está en Nivel 1) ni ejecuta ninguna acción. Es, de los dos agentes existentes, el de menor superficie de riesgo.

---

# 7. Límites Explícitos

El agente **no puede**:

* Escribir, modificar ni eliminar ningún registro de `productos_candidatos` u otra tabla.
* Decidir ni sugerir qué producto candidato debería pasar a `en_catalogo` — solo reporta cuántos están en cada estado, sin emitir juicio sobre casos individuales.
* Generar métricas de ventas, tráfico o comportamiento de usuario mientras no exista una tienda operando (ver "Alcance deliberadamente acotado" al inicio de este documento).
* Acceder a ninguna tabla fuera de `productos_candidatos` sin una revisión de este contrato (cambio minor).

**Requiere aprobación humana explícita antes de:**

* Ampliar el alcance a nuevas tablas o fuentes de datos (sección 4).
* Programarse como reporte automático recurrente (ej. envío semanal) — en esta versión el agente solo responde a solicitudes explícitas vía endpoint, no corre en background.

Coherente con DEC-008: este agente nunca ocupa el rol de Aprobador en la Matriz RACI (`100-Organizacion/07-Matriz-RACI.md`).

---

# 8. Manejo de Errores

* Si el rango de fechas o filtros no devuelven ningún registro: el agente responde con `resumen_catalogo.total_productos_candidatos = 0` y grupos vacíos, no con un error — un resultado vacío es una respuesta válida, no un fallo.
* Si la consulta a base de datos falla (conexión, timeout): un reintento inmediato; si falla de nuevo, se devuelve un error explícito al usuario (no un reporte parcial o inventado).
* Política de reintentos: máximo 1 reintento, sin backoff (a diferencia del Investigador de Producto, esta es una consulta de solo lectura sobre infraestructura propia, no una fuente externa — un fallo persistente indica un problema de infraestructura, no de disponibilidad de una fuente de terceros).
* Escalamiento: fallos repetidos (2 consecutivos) se registran como incidente técnico para el CTO, no se reintentan indefinidamente.

---

# 9. Métricas de Evaluación

| Métrica | Definición | Umbral inicial |
|---|---|---|
| Precisión | Los totales del reporte coinciden exactamente con un conteo manual (`SELECT COUNT(*)`) sobre los mismos filtros | 100% — es agregación determinística, no hay margen de "casi correcto" |
| Velocidad | Tiempo de generación de un reporte sobre el catálogo completo | Objetivo inicial: menor a 2 segundos |
| Coste | Coste de API/modelo por reporte generado | Si la implementación usa un LLM solo para redactar el resumen (no para calcular los números), el coste debería ser marginal comparado con el Investigador de Producto — a monitorear desde la primera ejecución |
| Impacto | Nº de veces que un reporte de este agente es citado como base de una decisión de mover un candidato a `en_catalogo` | A definir tras las primeras ejecuciones reales |
| Seguridad | Nº de veces que el agente intenta o ejecuta una escritura fuera de sus permisos (sección 4) | Debe ser 0; cualquier ocurrencia se registra como incidente |

**Nota de revisión futura:** cuando Fase 2 cierre y exista tráfico real de tienda, este contrato debe revisarse (versión minor como mínimo) para agregar métricas de negocio (conversión de catálogo a venta, etc.), conforme a `003-CEO/05-Metricas-y-Seguimiento.md`, sección 3.

---

# 10. Registro de Actividad

Por cada ejecución se registra:

* Fecha y hora (ISO 8601).
* Filtros de entrada recibidos (sección 2).
* Resumen de la salida generada (sección 3) — no hace falta guardar el JSON completo, basta con los totales, para no duplicar innecesariamente datos que ya están en `productos_candidatos`.
* Duración de la ejecución.
* Coste estimado (si el reporte usa un LLM para redacción, no solo agregación SQL).
* Responsable humano que solicitó el reporte.

**Dónde se registra:** mientras no exista base de datos operativa para logs de agentes, en `memory/` (archivo de log por agente, mismo patrón que el Investigador de Producto); migra a `006-BaseDatos` cuando se diseñe una tabla de registro de actividad compartida entre agentes (pendiente, no específico de este agente).

---

# Resumen Ejecutivo para IA

El Agente de Analítica Básica es el segundo agente de Merchly AI con contrato técnico. A diferencia del Investigador de Producto, es de solo lectura (Nivel de permiso 0): no genera datos nuevos, agrega y resume los que ya existen en `productos_candidatos` — distribución por categoría/estado/nivel de demanda, tasa de conversión candidato→en_catalogo, y actividad del Investigador de Producto. Deliberadamente no incluye analítica de ventas o tráfico porque esos datos no existen todavía (no hay tienda operando, Fase 2 pendiente); esa ampliación queda anotada como revisión futura del contrato, no como pendiente abierto de esta versión.
