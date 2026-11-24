# 05 — Funciones diferenciales para Bolivia

> Propuesta del equipo técnico (Daniel, 2026-11-23). **Pendiente del visto bueno del CTO.** Decisión asociada: DEC-038.

Las herramientas parecidas (Jungle Scout, Helium 10, Minea, etc.) están pensadas para vender en Amazon o Shopify, en dólares y desde EE.UU. MERCHLY AI se diferencia por resolver lo que vive un emprendedor en Bolivia: **cuánto le cuesta de verdad el producto puesto acá, cómo lo vende por WhatsApp y cuándo conviene venderlo.**

Las tres funciones respetan el principio rector: **la IA recomienda, las personas deciden**. Ninguna compra, publica ni manda mensajes sola.

---

## 1. Costo real puesto en Bolivia

**Problema:** la calculadora de margen sumaba un único "% de impuestos". En Bolivia la aduana cobra en cascada, y casi nadie sabe calcularlo.

**Qué hace:** cuando el negocio vende en Bolivia (`pais = BO`), la calculadora de margen del detalle de producto muestra el desglose:

| Concepto | Cálculo | Editable |
|---|---|---|
| Valor FOB | precio del proveedor | sí |
| Flete | envío por unidad (perfil) | sí |
| Seguro | 2 % del FOB (seguro presunto cuando no hay póliza) | no |
| **CIF** | FOB + flete + seguro | — |
| Gravamen arancelario (GA) | CIF × GA % (por defecto 10 %; varía entre 0 y 40 % según la partida) | sí |
| IVA de importación | (CIF + GA) × 14,94 % (el 13 % del IVA calculado "por dentro") | no |
| Gastos locales | despachante, transporte interno, etc., por unidad | sí |
| Comisión de cobro | % del precio de venta (QR, Tigo Money, tarjeta) | sí |

Resultado: costo puesto en Bolivia, ganancia por unidad y margen. Todo en Bs con el dólar oficial del BCB (o el tipo de cambio propio del negocio).

**Límites explícitos:**
- Son **estimaciones**. La pantalla avisa que el GA depende de la partida arancelaria y que conviene confirmar con un despachante.
- No se calcula el ICE (solo aplica a algunos productos) ni los regímenes especiales de courier o de menor cuantía.
- **Dólar paralelo: no se implementa.** Desde el régimen flexible del BCB (RD 142/2026), el Tipo de Cambio Oficial sale de las operaciones reales de la banca y es el único valor oficial. Quien compre dólares a otro precio carga su **tipo de cambio propio** en Configuración (ya existe).
- No hay columnas nuevas en la base. El campo `impuestos_importacion_pct` del perfil se usa como GA por defecto para Bolivia (si está en 0, se usa 10 %). Los demás valores se ajustan en la calculadora y no se guardan.

**Tests:** las funciones de cálculo (`frontend/lib/moneda.ts`) tienen tests con `node --test` (`npm test`), que también corren en el CI.

---

## 2. Catálogo listo para WhatsApp

**Problema:** en Bolivia se vende por WhatsApp, no por una tienda online. El emprendedor arma la lista de precios a mano.

**Qué hace:** pantalla nueva **Catálogo WhatsApp** (`/catalogo`):
- Lista los productos **aprobados por una persona** (`estado = en_catalogo`). Lo que la IA sugirió y nadie aprobó no aparece.
- Por cada producto se elige si entra y a qué precio se vende (en Bs). Por defecto, el precio sugerido.
- Se agregan un encabezado (el nombre del negocio) y una nota (envíos, formas de pago, contacto).
- Muestra la vista previa del mensaje con el formato de WhatsApp (`*negrita*`).
- Botones **Copiar** y **Abrir en WhatsApp**. Este último abre `https://wa.me/?text=…`, y la persona elige a quién mandarlo o lo pega en su estado.

**Límites explícitos:**
- **No manda nada solo.** Siempre envía la persona, desde su propio WhatsApp.
- Sin fotos: hoy no guardamos imágenes de productos.
- Los precios y la selección se recuerdan **solo en ese navegador** (`localStorage`), como comodidad. No se guardan en el servidor.

---

## 3. Calendario de temporadas bolivianas

**Problema:** las ventas fuertes dependen de fechas (Día de la Madre, Navidad, regreso a clases) y, si el producto se importa, hay que prepararse con semanas de anticipación.

**Qué hace:**
- **Servicio `temporadas.py`** (sin FastAPI): fechas comerciales de Bolivia con su anticipación recomendada e ideas de productos. Carnaval se calcula a partir de la Pascua; Black Friday, como el cuarto viernes de noviembre. Las fechas que cambian cada año, como el regreso a clases, se marcan como aproximadas.
- **Endpoint `GET /temporadas`** (requiere sesión; los 4 roles): devuelve las próximas temporadas de los siguientes 120 días con los días que faltan.
- **Panel de inicio:** la tarjeta "Próximas temporadas" muestra las 3 más cercanas, con "Empezá a preparar ya" cuando el tiempo es menor a la anticipación recomendada. Cada idea lleva a Productos con la búsqueda precargada para Bolivia.
- **IA:** si el negocio es de Bolivia, el contexto que recibe el Investigador incluye las próximas temporadas (como dato delimitado, igual que el rubro), para que las tenga en cuenta.

**Fechas incluidas:** Año Nuevo, Alasitas (24/1), regreso a clases (aprox. 1ª semana de febrero), San Valentín, Carnaval, Día del Padre (19/3), Día del Niño (12/4), Día de la Madre (27/5), Año Nuevo Andino (21/6), Día del Estudiante y de la Primavera (21/9), Día de la Mujer Boliviana (11/10), Todos Santos (2/11), Black Friday y Navidad.

---

## 4. Idea a futuro (no se implementa ahora): agente vendedor por WhatsApp

Propuesta de Daniel: un agente que responda a los clientes del negocio por la API de WhatsApp Business, con tono natural, para cerrar la venta. Solo en planes pagos.

**Evaluación técnica:** buena idea y diferencial fuerte, con estas condiciones:

1. **Choca con el principio rector si cierra ventas solo.** Propuesta: el agente responde las consultas con información **aprobada** (catálogo, precios, envíos, horarios, formas de pago) y **deriva a una persona** todo lo que comprometa al negocio: descuentos, precios fuera del catálogo, reclamos, confirmar un pedido o un pago. La persona decide y el agente prepara el borrador.
2. **Natural, pero sin hacerse pasar por humano.** Puede escribir en tono local y cercano, pero si el cliente pregunta, dice que es un asistente del negocio. Lo exige la honestidad con el cliente final y lo piden las reglas de Meta para bots de negocio. También nos protege legalmente.
3. **Riesgo de que invente cosas.** Si promete un precio o un plazo que no existe, el responsable es el negocio. Mitigación: responde solo con datos del catálogo y, si no sabe algo, dice "te confirmo en un rato" y avisa a la persona.
4. **Requisitos externos:** una app de Meta y la verificación del negocio en Meta Business, un número de WhatsApp Business por cliente, webhooks públicos (con firma verificada) y el costo por conversación de Meta, que hay que trasladar al precio del plan.
5. **Seguridad:** los mensajes de los clientes son datos no confiables (prompt injection). Se aplican las mismas defensas de `seguridad_llm.py`, se registra cada respuesta en la bitácora y hay un botón para apagar el agente al instante por negocio.

**Cuándo:** después del lanzamiento de la beta, cuando existan la app de Meta y los planes pagos. Cuando se apruebe, va a tener su propio contrato de agente en `docs/007-Agentes`.
