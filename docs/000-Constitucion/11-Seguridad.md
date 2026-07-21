# 11-Seguridad.md

---

title: Política de Seguridad de Merchly AI
document: 000-11
version: 1.0.0
status: Approved
owner: CTO
last_updated: 2026-07-20
next_review: 2027-01-20
related:

* 04-Principios.md
* 07-Gobernanza.md
* 08-Normas-de-Ingenieria.md
* 10-Estandares-de-Calidad.md

---

# Política de Seguridad

## Propósito

Este documento establece los principios, normas y controles necesarios para proteger Merchly AI, sus datos, infraestructura, usuarios, agentes de inteligencia artificial y activos estratégicos.

La seguridad es considerada una característica fundamental del sistema y deberá incorporarse desde la etapa inicial de diseño.

---

# Principio Fundamental

## Seguridad por Diseño

Toda funcionalidad, módulo, agente IA o integración deberá considerar la seguridad desde su creación.

No se aceptarán soluciones donde la seguridad sea tratada como una corrección posterior.

---

# Objetivos de Seguridad

Merchly AI deberá garantizar:

* Confidencialidad de la información.
* Integridad de los datos.
* Disponibilidad del sistema.
* Control de accesos.
* Trazabilidad de acciones.
* Protección contra usos indebidos.

---

# Modelo de Seguridad

La seguridad de Merchly AI se basa en cinco pilares:

```text id="6r6pj1"
Identidad

↓

Permisos

↓

Protección de datos

↓

Monitoreo

↓

Respuesta ante incidentes
```

---

# 1. Gestión de Identidad

## Norma

Toda persona, sistema o agente IA deberá tener una identidad identificable.

Debe existir:

* Usuario o identificador único.
* Registro de actividad.
* Permisos asignados.
* Historial de acciones.

---

# 2. Control de Acceso

## Principio de Mínimo Privilegio

Cada usuario o agente tendrá únicamente los permisos necesarios para cumplir su función.

Está prohibido:

* Otorgar permisos innecesarios.
* Compartir cuentas.
* Utilizar accesos genéricos sin control.

---

# Niveles de Acceso

## Nivel Estratégico

Acceso a:

* Objetivos.
* Decisiones.
* Configuración global.

Responsables:

* CEO.
* CTO.

---

## Nivel Administrativo

Acceso a:

* Gestión operativa.
* Configuraciones específicas.
* Administración de módulos.

---

## Nivel Operativo

Acceso limitado a:

* Ejecución de tareas autorizadas.
* Procesos definidos.

---

## Nivel Agente IA

Acceso:

* Exclusivamente a herramientas necesarias.
* Bajo permisos definidos.
* Con registro obligatorio.

---

# 3. Seguridad de Credenciales

## Norma

Las credenciales son activos críticos.

Nunca deberán:

* Guardarse en código.
* Compartirse públicamente.
* Almacenarse sin protección.

---

## Gestión Correcta

Debe utilizarse:

* Variables de entorno.
* Sistemas seguros de almacenamiento.
* Rotación periódica.

---

# 4. Protección de Datos

## Clasificación de Información

Merchly AI clasificará los datos como:

---

## Público

Información que puede compartirse libremente.

Ejemplo:

* Documentación pública.

---

## Interno

Información del funcionamiento del proyecto.

Ejemplo:

* Procesos internos.
* Documentación privada.

---

## Confidencial

Información empresarial sensible.

Ejemplo:

* Estrategias.
* Datos comerciales.

---

## Crítico

Información cuya exposición generaría daños importantes.

Ejemplo:

* Credenciales.
* Información financiera.
* Datos privados de clientes.

---

# 5. Seguridad de Datos Utilizados por IA

Los agentes IA deberán cumplir:

* No utilizar información no autorizada.
* No almacenar datos sensibles innecesariamente.
* Registrar fuentes utilizadas.
* Mantener trazabilidad.

---

# 6. Seguridad de Agentes IA

Cada agente deberá contar con:

## Límites Operativos

Definir:

* Qué puede hacer.
* Qué no puede hacer.
* Qué herramientas puede utilizar.

---

## Supervisión

Debe existir:

* Registro de acciones.
* Historial de decisiones.
* Sistema de auditoría.

---

## Control Humano

Los agentes no podrán:

* Modificar reglas fundamentales.
* Cambiar objetivos.
* Ejecutar acciones críticas sin aprobación.

---

# 7. Seguridad de Código

Todo desarrollo deberá cumplir:

* Revisión antes de integración.
* Control de versiones.
* Análisis de vulnerabilidades.
* Eliminación de información sensible.

---

# 8. Seguridad de Dependencias

Toda dependencia externa deberá evaluarse considerando:

* Reputación.
* Actualizaciones.
* Seguridad.
* Mantenimiento.
* Riesgo de abandono.

---

# 9. Seguridad de Infraestructura

La infraestructura deberá considerar:

* Actualizaciones constantes.
* Copias de seguridad.
* Control de accesos.
* Monitoreo.
* Recuperación ante fallos.

---

# 10. Registro y Auditoría

Merchly AI deberá registrar eventos relevantes:

* Accesos.
* Cambios.
* Decisiones.
* Ejecuciones automáticas.
* Errores.

---

# 11. Gestión de Incidentes

Ante un incidente de seguridad se deberá:

## Fase 1 — Detección

Identificar:

* Qué ocurrió.
* Cuándo ocurrió.
* Qué elementos fueron afectados.

---

## Fase 2 — Contención

Limitar el impacto.

---

## Fase 3 — Recuperación

Restaurar funcionamiento normal.

---

## Fase 4 — Prevención

Documentar:

* Causa.
* Solución.
* Mejoras futuras.

---

# 12. Seguridad en Decisiones IA

Cuando una decisión generada por IA tenga impacto relevante:

El agente deberá:

* Explicar el contexto.
* Presentar alternativas.
* Indicar riesgos.
* Solicitar aprobación humana.

---

# 13. Copias de Seguridad

Merchly AI deberá mantener mecanismos para recuperar:

* Código.
* Documentación.
* Configuraciones.
* Datos importantes.

---

# 14. Principio de Transparencia

Toda acción importante debe poder responder:

* Quién la realizó.
* Cuándo ocurrió.
* Qué información utilizó.
* Qué resultado produjo.

---

# 15. Evaluación Continua

La seguridad deberá revisarse periódicamente mediante:

* Auditorías.
* Pruebas.
* Revisiones de permisos.
* Evaluación de riesgos.

---

# Resumen Ejecutivo para IA

Merchly AI aplica seguridad por diseño.

Toda persona, sistema o agente IA debe operar bajo identidad, permisos definidos, trazabilidad y supervisión.

La protección de información, infraestructura y decisiones automatizadas es un requisito fundamental del proyecto.

---

# Lista de Verificación

Antes de aprobar cualquier módulo:

☐ Tiene control de acceso.

☐ Protege credenciales.

☐ Registra acciones importantes.

☐ Cumple mínimo privilegio.

☐ Protege datos.

☐ Tiene plan de recuperación.

☐ Permite auditoría.

☐ Respeta control humano.

---

# Vigencia

La política de seguridad evolucionará junto con Merchly AI, adaptándose a nuevas tecnologías, amenazas y necesidades del sistema.

Toda modificación deberá mantenerse alineada con los principios fundamentales del proyecto.
