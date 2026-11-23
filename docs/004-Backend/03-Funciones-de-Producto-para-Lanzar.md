# 03-Funciones-de-Producto-para-Lanzar.md

---

title: Funciones de producto para el lanzamiento
document: 004-03
version: 0.1.0
status: Aprobado por Daniel — pendiente visto bueno del CTO (DEC-034)
owner: CTO
last_updated: 2026-11-24
related:

* 02-Referencia-de-Endpoints.md
* ../007-Agentes/06-Agente-de-Marketing.md
* ../007-Agentes/07-Proveedores-Reales-y-Modelos-por-Plan.md
* ../013-Seguridad/04-Endurecimiento-para-Lanzamiento.md

---

# Funciones de producto para el lanzamiento

## Propósito

Lo que un emprendedor necesita para usar MERCHLY en serio, detectado al recorrer la app como usuario (2026-11-23). Todo respeta 013-04: aislamiento por organización (RLS), roles, validación estricta y "la IA recomienda, las personas deciden".

---

# 1. Historial de campañas

* Tabla `campanas` (RLS por organización): productos, canales, tono, idioma, modelo usado, contenido (`angulos`, `copy_por_canal`, `publico_objetivo`, `advertencias`), `titulo`, `creado_por`, `editada`, timestamps, borrado lógico.
* **Cambio al contrato del Agente de Marketing (006, "no persiste"):** cada campaña generada se guarda automáticamente en el historial. La IA sigue sin publicar nada.
* Endpoints: `GET /campanas` (listado resumido, paginado), `GET /campanas/{id}`, `PATCH /campanas/{id}` (editar título y textos; queda `editada = true`), `DELETE /campanas/{id}` (borrado lógico). Leer: los 4 roles. Editar y borrar: admin, técnico y negocio.

# 2. Canales de venta (sin publicar automáticamente)

* En cada campaña: **copiar** cada texto, **compartir por WhatsApp** (`wa.me/?text=`), **enviar por email** (`mailto:`), **descargar** (.txt).
* Instagram y Facebook: "Copiar para publicar". La conexión directa necesita una app de Meta aprobada (verificación de negocio y revisión): queda como pendiente documentado, no como botón falso.

# 3. Perfil del negocio (onboarding)

* Columnas nuevas en `organizaciones`: `pais` (ISO 3166-1 alfa-2, default `BO`), `rubro` (≤ 120), `presupuesto_mensual` (opcional), `moneda` (`BOB` / `USD`), `tipo_cambio` (Bs por USD, lo define el negocio), `costo_envio_unitario_usd` y `impuestos_importacion_pct` (para calcular el margen), `onboarding_completo`.
* `GET /organizacion` (todos los roles) y `PUT /organizacion/perfil` (solo `admin_principal`).
* El primer ingreso de un admin con el perfil incompleto lo lleva a `/bienvenida`.
* El Investigador recibe el rubro, el presupuesto y el país como **datos delimitados** (prompt injection, 007-07).

# 4. Precios en moneda local y margen real

* La interfaz muestra los precios en la moneda del negocio. Tipo de cambio: el **oficial del BCB, automático** (`GET /tipo-cambio`, caché 1 h, DEC-035) o el propio si el admin lo cargó. Nunca un valor inventado.
* Calculadora de margen en el detalle: costo del proveedor + envío por unidad + impuestos de importación (%) → costo total, ganancia y margen por unidad. Los valores por defecto salen del perfil y se pueden ajustar.
* "Dónde comprarle al proveedor": enlaces de **búsqueda** en AliExpress, Alibaba y Mercado Libre con el nombre del producto. Son búsquedas, no recomendaciones de un vendedor concreto.

# 5. Equipo (invitaciones y roles)

* Tabla `invitaciones`: organización, email, rol, `token_hash` (SHA-256; el token solo existe en el link), `expira_en` (7 días), `aceptada_en`, `creado_por`.
* `GET /usuarios`, `POST /usuarios/invitaciones`, `GET /usuarios/invitaciones`, `PATCH /usuarios/{id}` (rol, activo): **solo `admin_principal`**, y siempre dentro de su organización.
* Reglas: nadie cambia su propio rol ni se desactiva a sí mismo; no se puede dejar a la organización sin ningún admin activo; desactivar a alguien cierra todas sus sesiones.
* `POST /auth/aceptar-invitacion` (pública, con límite de intentos): código corto `XXXX-XXXX-XXXX` (DEC-035) + nombre + contraseña (política de 013-04) → crea el usuario en la organización con el rol de la invitación e inicia sesión.
* Hasta tener un proveedor de email, el admin **copia el link** y lo envía por WhatsApp o email.

# 6. Uso del plan

* `GET /organizacion/uso`: plan, cuotas por hora de cada agente, usadas y restantes, y en cuánto se renuevan (lee los contadores de Redis).
* Se muestra en "Plan y pagos" y en el Dashboard.

# 7. Ayuda

* Página `/ayuda` con preguntas frecuentes.
* Botón de WhatsApp de soporte si está configurado `NEXT_PUBLIC_SOPORTE_WHATSAPP` (número con código de país, sin `+`). Sin número, no se muestra el botón.

# 8. Fuera de alcance por ahora

Ventas reales (requiere conectar la tienda: Shopify, Tiendanube o WooCommerce), publicación directa en Meta, email transaccional y pagos.
