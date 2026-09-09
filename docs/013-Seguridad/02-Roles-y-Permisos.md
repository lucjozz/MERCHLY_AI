# 02-Roles-y-Permisos.md

---

title: Roles y Permisos
document: 013-02
version: 0.1.0
status: Draft — pendiente de aprobación
owner: CTO
last_updated: 2026-09-02
next_review: al aprobarse, o 2027-03-02
related:

* README.md
* 01-Modelo-de-Usuarios-y-Autenticacion.md
* 03-Alcance-y-Plan-de-Migracion.md
* ../001-Arquitectura/08-Arquitectura-de-Seguridad.md
* ../100-Organizacion/03-Roles-Ejecutivos.md

---

# Roles y Permisos

## Propósito

Aterrizar el sistema de roles humanos ya definido en `001-Arquitectura/08-Arquitectura-de-Seguridad.md` (sección "Sistema de Roles") a valores técnicos concretos y a una matriz real de qué rol puede llamar a qué endpoint protegido.

---

# 1. Los 4 Roles

| Rol técnico (`usuarios.rol`) | Nombre en `001-Arquitectura` | Corresponde hoy a |
|---|---|---|
| `admin_principal` | Administrador principal | Lucas (CEO + CTO, `100-Organizacion/03-Roles-Ejecutivos.md`) |
| `responsable_tecnico` | Responsable técnico | Sin titular humano hoy — rol preparado para cuando se sume alguien al equipo técnico. |
| `responsable_negocio` | Responsable negocio | Sin titular humano hoy — rol preparado para cuando se sume alguien al equipo de negocio/marketing. |
| `usuario_operativo` | Usuario operativo | Sin titular humano hoy — el rol de menor privilegio, para tareas operativas puntuales. |

Los 4 se crean en el `CHECK` de la tabla `usuarios` desde el día uno, aunque hoy solo exista un usuario real (`admin_principal`) — es la decisión explícita del CTO de implementarlos desde el inicio, no agregarlos después.

---

# 2. Matriz de Permisos

Aplica el Principio de Mínimo Privilegio de `000-Constitucion/11-Seguridad.md`: cada rol recibe solo lo que necesita para su función, tal como está definida en `100-Organizacion/03-Roles-Ejecutivos.md` y `04-Departamentos.md`.

| Endpoint | admin_principal | responsable_tecnico | responsable_negocio | usuario_operativo |
|---|---|---|---|---|
| `POST /agentes/investigador-producto` | ✅ | ✅ | ✅ | ❌ |
| `POST /agentes/analitica-basica` | ✅ | ✅ | ✅ | ✅ |
| `POST /agentes/marketing` | ✅ | ✅ | ✅ | ❌ |
| `POST /decisiones` | ✅ | ✅ | ✅ | ❌ |

**Criterio aplicado:**

* `investigador-producto` y `marketing` generan trabajo (y en el caso del primero, costo real de API de Gemini) y sus resultados alimentan decisiones de negocio — se restringen a roles con responsabilidad de negocio o técnica, no a `usuario_operativo`.
* `analitica-basica` es de solo lectura y sin costo de proveedor de IA (Nivel de permiso 0, ver `001-Arquitectura/03-Arquitectura-de-Agentes.md`) — se habilita para los 4 roles, incluido `usuario_operativo`, porque no hay riesgo real en que cualquiera consulte métricas agregadas.
* `POST /decisiones` es la acción con más impacto real (cambia el `estado` de un producto candidato) — se restringe a los 3 roles con responsabilidad de negocio o técnica. `usuario_operativo` no puede aprobar ni descartar productos.

**Este criterio es una propuesta inicial, no una verdad fija.** Al no haber hoy ningún titular real de `responsable_tecnico`, `responsable_negocio` ni `usuario_operativo`, esta matriz se ajusta con la primera persona real que se sume a alguno de esos roles, según lo que su trabajo concreto requiera — no antes.

---

# 3. Gestión de Usuarios

* Solo `admin_principal` puede crear, desactivar o cambiar el rol de otro usuario. No hay endpoint de auto-registro (`01-Modelo-de-Usuarios-y-Autenticacion.md`, sección 5).
* Un usuario no puede cambiar su propio rol (evita que un `usuario_operativo` se autoasigne `admin_principal`).
* Esto implica un endpoint de administración de usuarios (`POST /usuarios`, `PATCH /usuarios/{id}`) que **no se diseña en detalle en esta versión** — se especifica cuando exista un segundo usuario real que lo necesite (Principio de Simplicidad: no se documenta funcionalidad para un caso de uso hipotético). Mientras tanto, el primer usuario se crea por script/seed (`01-...`, sección 1).

---

# Resumen Ejecutivo para IA

AICOS implementa 4 roles desde el inicio (`admin_principal`, `responsable_tecnico`, `responsable_negocio`, `usuario_operativo`), aunque hoy solo `admin_principal` (Lucas) tiene un usuario real. Los endpoints con costo o impacto de negocio (`investigador-producto`, `marketing`, `decisiones`) requieren uno de los 3 roles con responsabilidad de negocio o técnica; el de solo lectura (`analitica-basica`) está abierto a los 4. La gestión de usuarios (crear, desactivar) es exclusiva de `admin_principal` y todavía no tiene endpoint propio.
