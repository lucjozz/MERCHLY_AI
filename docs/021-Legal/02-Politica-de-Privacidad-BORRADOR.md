# Política de Privacidad de MERCHLY AI — BORRADOR

> ⚠️ Borrador para revisión de un abogado. No vigente. Ver `README.md`.

**Última actualización:** [fecha]

## 1. Responsable

[Razón social], NIT [número], [domicilio], Bolivia. Contacto para privacidad: [email].

## 2. Qué datos tratamos

Esta lista refleja lo que el sistema guarda hoy (ver `docs/006-BaseDatos/02-Esquema-Fase1.md`):

| Dato | Para qué |
|---|---|
| Nombre y email de cada usuario | Crear la cuenta, iniciar sesión, avisos de seguridad |
| Contraseña | Solo se guarda un hash irreversible (bcrypt); nunca la contraseña |
| Identificador de cuenta de Google (si entrás con Google) | Iniciar sesión con Google |
| Datos del negocio: nombre, país, rubro, presupuesto, moneda, tipo de cambio, costos | Personalizar las recomendaciones y calcular márgenes |
| Productos, decisiones (con su motivo) y campañas | Prestar el Servicio e historial del negocio |
| Registro de actividad de seguridad: inicios de sesión, cambios de rol, borrados, con IP y navegador | Seguridad, prevención de fraude e investigación de incidentes |
| Cookies de sesión (técnicas, necesarias) | Mantener la sesión iniciada de forma segura |

No usamos cookies de publicidad ni vendemos datos personales.

## 3. Con quién se comparten (encargados)

Para prestar el Servicio usamos proveedores que procesan datos por cuenta nuestra:

* **Hosting e infraestructura:** [Render, Cloudflare] (servidores fuera de Bolivia).
* **Inteligencia artificial:** Google (Gemini) y OpenAI. Se les envían solo los datos necesarios para cada pedido (por ejemplo la categoría, el rubro y los datos de los productos de **tu** negocio); nunca contraseñas, tokens ni datos de otros negocios. Con OpenAI las solicitudes se hacen con almacenamiento desactivado (`store=false`).
* **Email:** [Resend] para avisos de cuenta (por ejemplo, restablecer la contraseña).
* **Google Sign-In**, si elegís entrar con Google.

[Transferencia internacional de datos: base legal y garantías — a definir por el abogado].

## 4. Cuánto tiempo guardamos los datos

* Datos de cuenta y del negocio: mientras la cuenta esté activa y [plazo] después de la baja.
* Registro de actividad de seguridad: al menos 12 meses.
* Copias de seguridad cifradas: hasta 12 meses según la política de retención.

## 5. Seguridad

Cada negocio está aislado de los demás también a nivel de base de datos; las sesiones viajan en cookies protegidas; los backups están cifrados; hay registro de actividad que no se puede editar. Ningún sistema es 100% infalible: si ocurre un incidente que afecte tus datos, te avisaremos sin demora.

## 6. Tus derechos

Podés pedir acceso, corrección, exportación o eliminación de tus datos personales escribiendo a [email]. [Plazos y procedimiento según la ley aplicable — a definir por el abogado].

## 7. Cambios

Si cambiamos esta política de forma importante, te avisaremos por email o en la aplicación antes de que el cambio rija.
