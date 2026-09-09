# Volumen 013 - Seguridad

> **Versión:** 0.1 Alpha (Contrato en Diseño)
> **Estado:** Pendiente de aprobación del CTO
> **Propietario:** CTO
> **Última actualización:** 2026-09-02

---

## Propósito

Este volumen define el **diseño técnico e implementable** de la autenticación, autorización y protección de endpoints de AICOS: cómo se identifica un usuario, cómo se le otorgan permisos, y qué partes del sistema quedan detrás de ese control.

Ya existen `000-Constitucion/11-Seguridad.md` (principios y normas generales de seguridad) y `001-Arquitectura/08-Arquitectura-de-Seguridad.md` (modelo conceptual: identidad, roles, niveles de acceso, clasificación de datos). Este volumen no repite esos principios — los aterriza en un mecanismo concreto: JWT, una tabla `usuarios`, y una matriz real de qué rol puede llamar a qué endpoint. Es la misma relación que existe entre `001-Arquitectura/04-Arquitectura-de-Datos.md` (conceptual) y `006-BaseDatos` (implementable).

**Por qué se diseña ahora:** el sistema de Decisiones Humanas (`POST /decisiones`, ver DEC-030) ya está en producción aceptando `user_id` como texto libre, sin validar quién es realmente el que decide. Es el primer endpoint con impacto real (cambia el `estado` de un producto) que necesita saber, de verdad, quién lo está llamando.

---

## Objetivos

- Definir un mecanismo de autenticación real (JWT con login/password), reemplazando el `user_id` de texto libre.
- Implementar los 4 roles humanos ya definidos en `001-Arquitectura/08-...` (Administrador principal, Responsable técnico, Responsable negocio, Usuario operativo) desde el inicio, no como trabajo futuro.
- Proteger los endpoints que ejecutan acciones (los 3 de agentes + decisiones), dejando de lado por ahora los de solo lectura.
- Mantener la disciplina "documentación antes que código": este volumen se aprueba antes de escribir una sola línea de implementación.

---

## Estructura

| Archivo | Descripción |
|---|---|
| 01-Modelo-de-Usuarios-y-Autenticacion.md | Tabla `usuarios`, hashing de contraseñas, JWT (claims, expiración, algoritmo), endpoints `POST /auth/login` y `GET /auth/me`. |
| 02-Roles-y-Permisos.md | Los 4 roles, sus permisos, y la matriz rol × endpoint protegido. |
| 03-Alcance-y-Plan-de-Migracion.md | Qué endpoints quedan protegidos y cuáles públicos, y cómo se migra `POST /decisiones` sin romper lo que ya existe. |

---

## Relación con otros volúmenes

- `000-Constitucion/11-Seguridad.md` y `001-Arquitectura/08-Arquitectura-de-Seguridad.md`: principios y modelo conceptual que este volumen implementa.
- `100-Organizacion/03-Roles-Ejecutivos.md`: define CEO/CTO como roles ejecutivos; este volumen los mapea a un rol técnico (`admin_principal`) para efectos de autenticación.
- `004-Backend/02-Referencia-de-Endpoints.md`: se actualizará cuando se implemente, agregando `POST /auth/login` y `GET /auth/me`, y marcando qué endpoints existentes pasan a requerir autenticación.
- `006-BaseDatos/02-Esquema-Fase1.md`: se actualizará con la tabla `usuarios` cuando se implemente.
- DEC-030 (`memory/DECISIONS.md`): el hallazgo que motivó diseñar este volumen ahora.

## Principio Rector

> **Este volumen se aprueba completo antes de escribir código.** Ningún endpoint pasa a requerir autenticación, y no se crea la tabla `usuarios`, hasta que el CTO confirme el diseño de las 3 secciones.

---

## Estado de Aprobación

Diseñado el 2026-09-02, a partir de 3 decisiones explícitas del CTO: JWT con login/password, proteger los endpoints que escriben/ejecutan (agentes + decisiones), y los 4 roles desde el inicio. **Pendiente:** revisión y aprobación final de los detalles técnicos (esquema de la tabla, expiración del token, matriz de permisos exacta) antes de pasar a `004-Backend` e implementar.
