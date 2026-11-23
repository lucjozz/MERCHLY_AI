# 06-Bitacora-de-Auditoria.md

---

title: Bitácora de auditoría de seguridad
document: 013-06
version: 0.1.0
status: Aprobado por Daniel — pendiente visto bueno del CTO (DEC-037)
owner: CTO
last_updated: 2026-11-24
related:

* 04-Endurecimiento-para-Lanzamiento.md
* 07-Plan-de-Respuesta-a-Incidentes.md
* ../006-BaseDatos/04-Politica-de-Backups-y-Retencion.md

---

# Bitácora de auditoría de seguridad

## Propósito

Saber **quién hizo qué y cuándo** en cada negocio: inicios de sesión, cambios de roles, borrados. Sirve para investigar un incidente (013-07), para que el admin de cada negocio vea la actividad de su equipo, y para demostrar control ante clientes.

# 1. Qué se registra

| Acción | Cuándo |
|---|---|
| `login_ok` / `login_fallido` | Inicio de sesión con email (el fallido guarda solo un hash del email intentado) |
| `login_google` / `registro_google` | Entrada o alta con Google |
| `logout` / `sesiones_cerradas` | Cierre de sesión / cierre en todos los dispositivos |
| `password_restablecimiento_pedido` / `password_restablecida` | Recuperación de contraseña |
| `invitacion_creada` / `invitacion_revocada` / `invitacion_aceptada` | Equipo |
| `rol_cambiado` / `usuario_desactivado` / `usuario_reactivado` | Equipo (con valor anterior y nuevo) |
| `producto_borrado` / `campana_borrada` | Borrados (lógicos) |
| `perfil_actualizado` | Cambios en el perfil del negocio |

Cada evento guarda: organización, quién lo hizo (si se sabe), acción, sobre qué (tipo e id), detalle mínimo, IP y navegador (recortado), y fecha.

**Nunca** se guardan contraseñas, tokens, códigos de invitación, links de restablecimiento ni el contenido de los productos o campañas.

# 2. Garantías

* **Append-only:** el rol de la app solo puede insertar y leer; no puede editar ni borrar eventos (privilegios de base).
* **Aislamiento:** cada negocio solo puede leer **sus** eventos (RLS). Los intentos de login fallidos sin usuario conocido quedan sin organización y solo los ve el equipo técnico desde la base.
* **No bloquea:** si registrar un evento falla, la acción del usuario no se corta (se loguea el error).
* **Retención:** 12 meses, como mínimo; el borrado de eventos viejos lo hace un proceso administrativo, nunca la app.

# 3. Acceso

* `GET /auditoria` (solo `admin_principal`, su organización, paginado, filtro por acción).
* Pantalla **"Actividad de seguridad"** dentro de Equipo.
