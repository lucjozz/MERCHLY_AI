# 07-Plan-de-Respuesta-a-Incidentes.md

---

title: Plan de respuesta a incidentes de seguridad
document: 013-07
version: 0.1.0
status: Borrador — pendiente visto bueno del CTO (DEC-037)
owner: CTO
last_updated: 2026-11-24
related:

* 04-Endurecimiento-para-Lanzamiento.md (sección 9: fuga de secretos)
* 06-Bitacora-de-Auditoria.md
* ../002-CTO/07-Despliegue-en-Render.md
* ../006-BaseDatos/04-Politica-de-Backups-y-Retencion.md

---

# Plan de respuesta a incidentes

## Propósito

Saber qué hacer, en orden y sin improvisar, cuando algo sale mal: una cuenta robada, una clave filtrada, datos expuestos, la web caída o un gasto de IA disparado.

# 1. Roles

| Rol | Quién | Qué hace |
|---|---|---|
| Responsable del incidente | Admin técnico de turno (hoy: Daniel) | Decide, coordina y cierra el incidente |
| Apoyo técnico | CTO | Revisa, aprueba cambios urgentes |
| Comunicación | Dueño del negocio / CTO | Avisa a clientes y, si corresponde, a autoridades |

Contactos (completar y mantener actualizado): teléfono y WhatsApp de cada rol, acceso a Render, Cloudflare, GitHub, Google Cloud y OpenAI.

# 2. Gravedad

| Nivel | Ejemplos | Tiempo de respuesta |
|---|---|---|
| **Crítico** | Datos de clientes expuestos, acceso de un tercero a la base, clave de producción filtrada | Inmediato (menos de 1 hora) |
| **Alto** | Cuenta de admin comprometida, web caída, gasto de IA disparado | Menos de 4 horas |
| **Medio** | Ataque de fuerza bruta frenado, vulnerabilidad en una dependencia | Menos de 24 horas |
| **Bajo** | Error sin impacto en datos | Próximo día hábil |

# 3. Los 6 pasos (para cualquier incidente)

1. **Detectar y registrar:** anotar qué se vio, cuándo y quién lo vio (en un documento del incidente, con hora).
2. **Contener:** cortar el daño primero, investigar después (ver recetas de la sección 4).
3. **Investigar:** revisar la **bitácora de auditoría** (Equipo → Actividad de seguridad, o la tabla `eventos_auditoria`), los logs de Render y Cloudflare, y los paneles de gasto de Google y OpenAI.
4. **Erradicar:** corregir la causa (parche, rotación de claves, desactivar la cuenta).
5. **Recuperar:** volver a operar normal; si hubo daño en los datos, restaurar desde backup (simulacro probado: `ops/backups/probar_restauracion.py`).
6. **Aprender:** escribir qué pasó, por qué y qué se cambia para que no se repita, en `docs/015-Bitacora`, en las 72 horas siguientes.

# 4. Recetas por tipo de incidente

### Cuenta de un usuario comprometida
1. Equipo → **Desactivar** a esa persona (corta su acceso al instante y cierra sus sesiones).
2. Revisar en la bitácora qué hizo esa cuenta desde la fecha sospechosa.
3. Pedirle que cambie la contraseña ("¿Olvidaste tu contraseña?") y reactivarla.

### Clave o secreto filtrado (API key, JWT_SECRET_KEY, contraseña de base)
1. **Rotar primero:** generar uno nuevo y reemplazarlo en Render. Borrarlo del repo no alcanza, queda en el historial.
2. Revocar el viejo en el proveedor (Google AI Studio, OpenAI, GitHub, Resend).
3. Si fue `JWT_SECRET_KEY`: rotarlo cierra la sesión de todos los usuarios (es lo buscado).
4. Revisar el uso del proveedor durante la ventana de exposición.

### Datos de clientes expuestos
1. Contener el acceso (cerrar el endpoint, revocar credenciales, cortar el tráfico en Cloudflare si hace falta).
2. Determinar qué datos, de qué negocios y desde cuándo.
3. **Avisar a los negocios afectados** sin demora, con información clara de qué pasó y qué hacer.
4. Consultar con el abogado si hay obligación de avisar a una autoridad en Bolivia u otro país donde operen los clientes.

### Web caída
1. Verificar el estado en Render (servicios, despliegues recientes) y en Cloudflare.
2. Si fue un despliegue: volver a la versión anterior desde Render ("Rollback").
3. Si es la base: revisar el estado del Postgres en Render; restaurar si hay corrupción.

### Gasto de IA disparado
1. Bajar o pausar el tope de gasto en el panel de Google y OpenAI.
2. Revisar qué negocio consume (cuotas por organización, bitácora y logs).
3. Ajustar las cuotas del plan si hace falta.

### Ataque de fuerza bruta o bots
1. Confirmar en la bitácora (muchos `login_fallido`).
2. Endurecer el límite en Cloudflare para `/api/auth/*` y activar el desafío ("Under Attack") si es masivo.

# 5. Después de cada incidente

* Informe breve en `docs/015-Bitacora` (qué, cuándo, impacto, causa, acciones).
* Si cambió algún procedimiento, actualizar este documento.
* Revisar este plan al menos una vez por trimestre.
