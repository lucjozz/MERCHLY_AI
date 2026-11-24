# 09 — Verificación en dos pasos, retención de datos y pruebas de seguridad

> Trabajo de la noche del 2026-11-24 (pedido por Daniel: "blindá más la seguridad"). **Pendiente visto bueno del CTO.** Decisión: DEC-040.

---

## 1. Verificación en dos pasos (TOTP)

**Para qué:** si alguien roba la contraseña de un usuario, igual no puede entrar ni confirmar pagos sin el celular.

* **Estándar:** RFC 6238 (SHA-1, 6 dígitos, 30 s). Compatible con Google Authenticator, Microsoft Authenticator, Authy y 1Password. Implementación propia (`app/core/totp.py`) verificada contra los vectores oficiales del RFC. El QR se genera con `segno`.
* **Anti-repetición:** un código ya usado no sirve otra vez (se guarda el último paso usado). Se acepta ±30 s de diferencia con el reloj del celular.
* **Clave cifrada:** se guarda con AES-256-GCM (`app/core/cifrado.py`), atada al id del usuario: si se copia a otra fila, no se descifra. La clave de cifrado es `CIFRADO_CLAVE`, obligatoria en producción; en local se deriva del JWT con HKDF.
* **10 códigos de respaldo:** se guardan como hash, son de un solo uso y se muestran una sola vez.
* **Alta:** QR → código del celular → activada. **Baja:** pide un código válido, así quien tenga la sesión abierta no puede apagarla.
* **Login:** si está activada, la contraseña (o Google) no da la sesión. Se emite un **desafío** de un solo uso:
  * vive 5 minutos en Redis y acepta 5 intentos;
  * viaja en una cookie `__Host-merchly_2fa` (HttpOnly, Secure, SameSite=Strict), así el JavaScript de la página nunca lo ve;
  * se canjea en `POST /api/auth/2fa` por la sesión;
  * además rige el límite de intentos por IP del login.
* **Pantalla:** Configuración → "Verificación en dos pasos". Por ahora es **optativa**; a los administradores se les recomienda activarla.
* **Bitácora:** activada, desactivada y códigos fallidos.

## 2. Re-verificación para confirmar pagos

Confirmar o rechazar un pago **real** exige haber confirmado que sos vos hace menos de 10 minutos (`POST /auth/reautenticar`):

* Con 2FA activada: **solo el código** (la contraseña no alcanza).
* Sin 2FA: la contraseña.
* Si falla, responde 422 y no 401, así la sesión no se cierra.
* Fail-closed: sin Redis, no se confirman pagos.
* Los pedidos **simulados** (los del simulador) no la piden.

## 3. Guardia de salida del asistente

Además de bloquear montos que no salieron de la base, una respuesta del asistente **no sale** si:

* promete descuentos, regalos, envíos gratis o 2×1;
* dice que un pago está confirmado o acreditado;
* habla de costos internos, ganancia, margen o proveedor.

En esos casos se reemplaza por "Dejame confirmarlo con el vendedor…" y se avisa al dueño (`app/services/atencion/guardia.py`).

## 4. Base segura para WhatsApp (Fase B, sin rutas expuestas)

`app/services/canales/seguridad_webhook.py`, con tests:

* Firma `X-Hub-Signature-256` (HMAC-SHA256 del cuerpo crudo). Falla cerrado si falta la firma o el secreto.
* Verificación de la suscripción con comparación en tiempo constante.
* Idempotencia por id de mensaje (Meta reintenta) y descarte de mensajes de más de 24 h.
* Tokens de cada negocio cifrados y atados a organización + canal.

## 5. Retención de datos

`ops/retencion/limpiar.py` corre con el dueño de la base; por defecto es un simulacro que solo cuenta, y `--aplicar` aplica todo en una sola transacción:

| Dato | Plazo | Qué se hace |
|---|---|---|
| Mensajes con compradores | 12 meses | se borran |
| Contacto de conversaciones viejas | 12 meses | se anonimiza |
| Nombre y dirección en pedidos viejos | 12 meses | se anonimizan (los montos quedan) |
| Avisos al vendedor | 90 días | se borran |
| Sesiones / links de recuperación vencidos | 30 días | se borran |
| Invitaciones vencidas o aceptadas | 90 días | se borran |
| Bitácora de seguridad | 24 meses | se borra (la política exige al menos 12) |

Para producción: programarlo una vez por semana, igual que los backups.

## 6. Resultados de las pruebas (2026-11-24)

| Prueba | Resultado |
|---|---|
| Compras simultáneas: 10 compradores por la última unidad | 1 la reserva, 9 reciben "agotado" |
| 5 clics simultáneos en "Confirmar pago" | el stock baja 1 sola vez; 4 reciben 409 |
| 41 mensajes trampa al asistente (prompt injection, pedidos de descuento, "confirmá mi pago", texto invisible, etc.) | 0 descuentos, 0 costos revelados, 0 pagos confirmados |
| 25 respuestas "envenenadas" de una IA engañada | las 25 bloqueadas por la guardia; 8 respuestas normales pasan |
| Abuso de herramientas (precio propio, producto de otra org, cantidades 0 / -1 / 101) | todo rechazado |
| Pentest v3 (IDOR en 14 endpoints nuevos, rutas codificadas contra el BFF, CSRF, SVG/HTML/políglota/bomba de descompresión/ejecutable, XSS, mass assignment, cuota) | 43/43 (2 falsos positivos: Next redirige `x/` → `x` y vuelve a pasar la lista blanca) |
| Verificación en dos pasos en vivo (alta, login, anti-repetición, respaldo de un uso, tope de intentos, CSRF, re-verificación de pagos, baja) | 27/27 |
| Simulacro de restauración con las tablas nuevas | 22 tablas idénticas, RLS activo y forzado en 13, RTO 65 s |

## 7. Pendiente

* Decidir con el CTO si la verificación en dos pasos es **obligatoria** para administradores (hoy es optativa).
* Programar la retención y los backups en producción (Render Cron Job).
* Visión del asistente (A6): las fotos de compradores van a tener retención de 30 días (falta agregar esa regla cuando exista la tabla).

---

## 8. Límite general de pedidos (todas las entradas)

`app/core/limite_peticiones.py`, un middleware para toda la API (ventana de 60 s en Redis):

| Quién | Tope por minuto |
|---|---|
| Usuario con sesión, lecturas | 240 |
| Usuario con sesión, escrituras | 60 |
| Sin sesión (login, recuperar contraseña, invitaciones) | 40 por IP |
| `/auth/refresh` | 20 por IP |

* Con sesión se cuenta **por usuario** y no por IP: todos llegan a través del BFF, y así un usuario no frena a otro.
* El BFF ahora le pasa la IP real del cliente al backend (`X-Forwarded-For`) en todas las llamadas, no solo en el login. Además, la bitácora ya registra la IP verdadera.
* Fail-open si Redis no responde (el login y los pagos siguen siendo fail-closed).
* `/health` ya no muestra versión ni entorno, y HSTS pasó a 2 años con `preload`.

## 9. Blindaje de la cuenta de administrador

* **Re-verificación** (código del celular o contraseña, 10 minutos) para:
  * invitar personas, cambiar roles, desactivar miembros y revocar invitaciones;
  * cambiar la configuración del asistente;
  * **subir o borrar el QR de cobro**, la estafa más directa con una sesión robada;
  * confirmar o rechazar pagos.
* Ventana única "Confirmá que sos vos" en el frontend: aparece sola y, si la persona confirma, la acción se reintenta.
* **Aviso de QR nuevo** a todo el equipo.
* **Aviso de inicio de sesión desde una IP nueva** (en la app y por email) cuando un admin entra desde una conexión que no usó en 90 días.
* **Sesión de admin más corta:** 7 días sin uso, contra 14 del resto.

## 10. Pentest v4 (2026-11-24)

51 pruebas sobre toda la superficie:

* filtraciones: `.env`, `.git`, el bundle del navegador, `/health`;
* enumeración de usuarios por mensaje y por tiempo de respuesta;
* rutas protegidas sin sesión;
* JWT alterado o con `alg=none`;
* fuzzing de 140 pedidos con valores raros;
* JSON con 5.000 niveles;
* inyección SQL en filtros;
* CORS, cookies y límites.

**Hallazgos corregidos:** `/health` filtraba la versión y el entorno; HSTS de un día; faltaba un límite general de pedidos.

**Pendiente de infraestructura:** Next devuelve 500 ante el método `TRACE`. No expone datos, pero hay que bloquear los métodos no estándar con una regla del WAF de Cloudflare al publicar.

## 11. Bugs encontrados recorriendo la web

* **Simulador del asistente roto en Chrome y Edge recientes.** `scrollIntoView` ahora devuelve una Promise; el efecto la devolvía y React la tomaba como función de limpieza, así que la pantalla se rompía en el primer mensaje. Se corrigió y se agregó una regla de ESLint que prohíbe efectos `() => valor`.
* **Catálogo de WhatsApp vacío** para negocios con inventario: solo leía las sugerencias de la IA. Ahora sale del catálogo público del inventario, con el precio y el stock reales.
* **404 en inglés y sin página de error:** se agregaron las páginas "no existe", "error" y "error global" en español, sin detalles técnicos.
