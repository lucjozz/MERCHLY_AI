# 08-Inventario-y-Subagente-Catalogo.md

---

title: Contrato Técnico — Inventario del negocio y Sub-agente Catálogo (hijo del Agente de Marketing)
document: 007-08
version: 0.1.0
status: Propuesta (pendiente de aprobación del CTO)
owner: CTO
last_updated: 2026-11-23
related:

* 01-Contrato-Tecnico-Estandar.md
* 06-Agente-de-Marketing.md
* 09-Agente-de-Atencion-al-Cliente.md
* ../004-Backend/05-Funciones-Diferenciales-Bolivia.md
* ../013-Seguridad/04-Endurecimiento.md

---

## Propósito

Definir dos piezas que van juntas:

1. El **inventario del negocio**: los productos que el negocio vende de verdad, con su precio, sus fotos y la cantidad disponible. Es la fuente de verdad que usan el catálogo y el Agente de Atención al Cliente.
2. El **Sub-agente Catálogo**, hijo del Agente de Marketing. Escribe textos únicos para cada producto y arma un catálogo diseñado (PDF e imagen) para mandar y publicar.

Idea acordada por Daniel y el socio el 2026-11-23 (DEC-039).

---

# 1. Estructura jerárquica de agentes

```
Agente de Marketing (principal, ya existe)
├── Función: campañas (ya existe)
└── Sub-agente Catálogo (nuevo)
    ├── Función 1: textos únicos por producto
    ├── Función 2: diseño del catálogo (PDF / imagen)
    └── Función 3: importar un catálogo existente (cualquier formato)
```

**Regla de carga bajo demanda:** cada sub-agente es un módulo que se importa y se ejecuta **solo cuando se lo pide** (`app/services/agentes/<agente>/<subagente>.py`). No hay procesos corriendo de fondo ni modelos cargados en memoria. Si nadie arma un catálogo, ese código no se ejecuta y no gasta IA.

**Qué usa IA y qué no:** solo la usan las funciones que la necesitan (textos e importación de formatos libres). El diseño y la importación de Excel/CSV son código determinístico: más baratos, más rápidos y sin errores inventados.

---

# 2. Dos vistas: inventario del dueño y catálogo público de la IA

Pedido de Daniel (2026-11-23): **dos catálogos** con propósitos distintos, armados sobre los mismos productos (una sola tabla, `inventario_productos`, para que nunca se desincronicen).

| | **Inventario** (privado, del dueño) | **Catálogo público** (la "cara pública", lo que usa la IA) |
|---|---|---|
| Para qué | controlar el negocio: cuánto costó, cuánto gasto, cuánto hay, cuánto gano | encontrar productos, dar precios y responder mensajes |
| Quién lo ve | el equipo del negocio | el Agente de Atención al Cliente, el Sub-agente Catálogo y los compradores |
| Qué productos | todos | solo los **publicados** (`publicado = true`), no borrados |
| Campos | todos | nombre, descripción, especificaciones, precio de venta, disponibles y fotos |

**Campos de cada producto**

| Campo | Vista | Notas |
|---|---|---|
| `nombre`, `sku` | ambas (el SKU solo el dueño) | |
| `descripcion` | ambas | la escribe el dueño o la propone el Sub-agente Catálogo |
| `especificaciones` | ambas | JSONB clave→valor, p. ej. `{"potencia": "800 W"}` |
| `precio_venta` | ambas | en la moneda del negocio; **el único precio que la IA puede decir** |
| `costo_unitario` | **solo el dueño** | lo que pagó al proveedor |
| `gastos_unitarios` | **solo el dueño** | envío, aduana, despachante, etc., por unidad |
| `proveedor`, `notas_internas` | **solo el dueño** | |
| `stock` | dueño (la IA ve "disponibles") | cantidad real |
| `stock_reservado` | sistema | unidades apartadas por pedidos sin confirmar (007-09) |
| `publicado` | — | si aparece en el catálogo público |
| `origen`, `producto_candidato_id` | solo el dueño | `aprobado` / `importado` / `manual` |

**Disponibles en el catálogo público** = `stock − stock_reservado`. El inventario calcula además, para el dueño, el margen por unidad (`precio_venta − costo_unitario − gastos_unitarios`) y el valor del inventario a costo.

**La separación se garantiza en el código:** la IA solo lee el catálogo público a través de una función que devuelve un schema sin campos privados. Un test verifica que ese schema nunca incluya costo, gastos, proveedor, notas ni stock real.

Lleva multi-tenancy y RLS igual que el resto, y borrado lógico. Pueden editar el admin principal y el responsable de negocio. Cada alta, cambio de precio o de stock, borrado e importación queda en la bitácora de auditoría.

## 2.1 Fotos

* Tipos permitidos: JPEG, PNG y WebP, comprobados por los **bytes del archivo** y no por la extensión. Máximo 5 MB.
* Se re-codifican al subirlas (Pillow). Eso borra los metadatos EXIF, incluida la ubicación GPS del celular, y descarta archivos maliciosos disfrazados de imagen.
* Se guardan con un id aleatorio en la tabla `inventario_fotos` (Postgres, con RLS), ya re-codificadas en WebP de hasta 1600 px (pesan unos 100 a 300 KB). Es más simple que un bucket y además entra en los backups cifrados. Se pasa a Cloudflare R2 solo si el volumen lo justifica.
* El navegador achica la foto antes de subirla, así no hay que subir archivos de 10 MB desde el celular.
* Se sirven solo a usuarios con sesión de esa organización, a través del BFF. Nunca con URL pública permanente.

---

# 3. Sub-agente Catálogo

## 3.1 Función 1 — Textos únicos por producto

* **Entrada:** producto del inventario (nombre, especificaciones, precio, fotos opcionales) y perfil del negocio (rubro, tono, país).
* **Salida:** título comercial, descripción corta (≤ 300 caracteres), 3 beneficios y texto para el estado de WhatsApp.
* **Único:** el texto se genera con el tono y los datos de **ese** negocio. Antes de proponerlo se compara con la descripción del proveedor y con los textos de otros productos del mismo negocio. Si se parece demasiado (similitud > 0,8), se regenera una vez y, si sigue parecido, se marca como advertencia. Nunca se copian textos de otros negocios: el agente no tiene acceso a ellos (RLS).
* **Humano decide:** el texto es una **propuesta**. Se guarda en el inventario solo cuando el dueño lo acepta o lo edita.
* No puede inventar características que no estén en las especificaciones ni prometer certificaciones o garantías.

## 3.2 Función 2 — Diseño del catálogo (PDF e imagen)

* **Salidas:**
  * PDF A4 con portada y una grilla de productos (foto, nombre, precio y descripción corta).
  * Imagen vertical 1080×1920 para estados e historias.
  * Imagen cuadrada 1080×1080 para posts.
* **Identidad del negocio:** logo, colores y nombre que carga el dueño en Configuración. Si no hay, se propone una paleta a partir del rubro.
* **Único:** el diseño sale de combinar plantilla, paleta y tipografía con el logo y las fotos propias del negocio. Dos negocios con el mismo producto no reciben el mismo catálogo.
* **Técnica:** render del lado del servidor con plantillas propias (Pillow para imágenes y ReportLab para PDF; dependencias con mantenimiento activo y sin navegador). No usa IA para dibujar: así no aparecen precios ni textos mal escritos dentro de la imagen.
* Incluye solo productos **activos** con disponibilidad > 0, a menos que el dueño elija mostrar los agotados.
* Se descarga o se comparte. Nunca se publica solo.

## 3.3 Función 3 — Importar un catálogo existente (cualquier formato)

| Formato | Cómo se lee | Usa IA |
|---|---|---|
| Excel (.xlsx) / CSV | lectura directa de columnas, con mapeo de columnas que confirma el dueño | no |
| PDF con texto | extracción de texto + IA para estructurar | sí |
| PDF escaneado, fotos de un catálogo impreso o capturas | IA con visión | sí |
| Word (.docx) | extracción de texto + IA | sí |

**Regla clave:** la importación **nunca guarda directo**. Siempre muestra una **tabla de vista previa** (nombre, precio, stock y especificaciones detectadas, con las dudas marcadas). El dueño corrige y confirma qué filas entran. Lo que la IA no está segura de haber leído, como un precio borroso, queda vacío y marcado, nunca inventado.

**Seguridad de archivos:**
* Tope de 10 MB y de 500 filas por importación.
* Excel abierto sin ejecutar fórmulas ni macros (`openpyxl`, `read_only`, `data_only`) y XML leído con protección (`defusedxml`).
* El contenido del archivo es un **dato no confiable**: va delimitado a la IA (`seguridad_llm.py`), así un texto escondido en el archivo no puede darle órdenes.
* Límite de importaciones por día según la cuota del plan.

---

# 4. Permisos y límites

* **Nivel:** 1 (analiza y propone). No publica ni manda nada.
* **No puede:** cambiar precios ni stock sin la confirmación del dueño, ver el costo al escribir textos de venta, usar logos o marcas de terceros, ni ver datos de otros negocios.
* **Proveedor de IA:** el del Agente de Marketing según el plan (007-07). La visión para importar usa el modelo multimodal del plan.

# 5. Manejo de errores

* Si la IA falla: 2 reintentos y después un error claro. Nunca contenido fabricado sin pasar por el modelo.
* Si el archivo no se puede leer: se le dice al dueño qué pasó ("el PDF está protegido con contraseña", "no encontramos columnas de precio") y no se guarda nada.

# 6. Métricas

| Métrica | Umbral inicial |
|---|---|
| % de textos aceptados sin cambios grandes | a medir con las primeras 20 generaciones |
| % de filas importadas que el dueño no tuvo que corregir | a medir |
| Tiempo para generar un catálogo de 20 productos | < 30 s (sin IA) |
| Cumplimiento de límites (sección 4) | 100 % |

---

# Resumen Ejecutivo para IA

Dos vistas sobre la misma tabla: el inventario del dueño (costos, gastos, stock real y margen) y el catálogo público que usa la IA (solo productos publicados, sin datos privados; un test lo garantiza). Fotos re-codificadas, RLS y auditoría. El Sub-agente Catálogo depende del Agente de Marketing, se carga solo cuando se usa y tiene tres funciones: textos únicos (propuesta que el dueño acepta), catálogo diseñado en PDF e imagen sin IA para dibujar, e importación de cualquier formato con vista previa obligatoria antes de guardar. Nivel 1: no publica ni cambia datos sin el dueño.
