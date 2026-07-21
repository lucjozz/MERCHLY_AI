# 08-Normas-de-Ingeniería.md

---

title: Normas de Ingeniería de Merchly AI
document: 000-08
version: 1.0.0
status: Approved
owner: CTO
last_updated: 2026-07-20
next_review: 2027-01-20
related:

* 04-Principios.md
* 07-Gobernanza.md
* 10-Estandares-de-Calidad.md

---

# Normas de Ingeniería

## Propósito

Este documento establece los estándares técnicos obligatorios para diseñar, desarrollar, mantener y evolucionar Merchly AI.

Su objetivo es garantizar que el sistema sea:

* Escalable.
* Seguro.
* Mantenible.
* Documentado.
* Modular.
* Preparado para integrar nuevas tecnologías.

---

# 1. Idioma Oficial del Proyecto

## Norma

Toda documentación de Merchly AI deberá estar escrita en español.

## Aplicación

Incluye:

* Documentación técnica.
* Manuales.
* Reportes.
* Procesos.
* Prompts.
* Especificaciones.
* Registros de decisiones.

## Excepciones

Se permiten términos técnicos internacionales cuando sean necesarios:

Ejemplos:

* API.
* Framework.
* Backend.
* Frontend.
* Docker.
* Python.
* PostgreSQL.
* GitHub.

La explicación asociada deberá mantenerse en español.

---

# 2. Diseño Antes del Desarrollo

## Norma

Ninguna funcionalidad importante deberá comenzar sin una definición previa.

## Requisitos mínimos

Antes de desarrollar:

* Objetivo definido.
* Alcance establecido.
* Dependencias identificadas.
* Impacto evaluado.
* Criterios de aceptación definidos.

---

# 3. Arquitectura Modular

## Norma

Todo componente debe diseñarse como un módulo independiente.

## Reglas

Cada módulo debe tener:

* Responsabilidad única.
* Interfaz definida.
* Documentación propia.
* Pruebas asociadas.

Debe evitarse:

* Código duplicado.
* Dependencias innecesarias.
* Componentes demasiado grandes.

---

# 4. Principio de Simplicidad

## Norma

La solución más sencilla que cumpla correctamente los requisitos será preferida.

## Prohibiciones

No se aceptará:

* Complejidad por moda tecnológica.
* Uso de herramientas sin necesidad.
* Sobreingeniería anticipada.

---

# 5. Control de Versiones

## Norma

Todo código y documentación deberá gestionarse mediante control de versiones.

## Estándar

Se utilizará:

* Git.
* Repositorio centralizado.
* Historial de cambios.
* Ramas organizadas.

---

# 6. Organización del Código

## Norma

La estructura del código debe permitir que cualquier desarrollador o agente IA pueda comprender el sistema rápidamente.

## Requisitos

Debe existir:

* Separación clara de responsabilidades.
* Nombres descriptivos.
* Estructura consistente.
* Comentarios únicamente cuando aporten contexto.

---

# 7. Documentación Obligatoria

## Norma

El código sin documentación suficiente no se considera terminado.

Cada módulo deberá incluir:

* Propósito.
* Funcionamiento.
* Instalación.
* Configuración.
* Dependencias.
* Uso.
* Limitaciones.

---

# 8. Desarrollo con Inteligencia Artificial

## Norma

Las herramientas de IA serán utilizadas como asistentes de ingeniería, no como sustitutos del criterio técnico.

## Uso permitido

La IA puede ayudar en:

* Generación de código.
* Revisión.
* Documentación.
* Investigación.
* Optimización.

## Obligaciones

Todo código generado por IA deberá:

* Ser revisado.
* Ser comprendido.
* Ser probado.
* Cumplir estándares del proyecto.

---

# 9. Desarrollo de Agentes IA

Cada agente deberá tener:

## Identidad

* Nombre.
* Propósito.
* Responsable.

## Definición

* Entradas.
* Procesos.
* Salidas.
* Límites.

## Control

* Permisos.
* Registro de actividad.
* Métricas.

---

# 10. Gestión de Datos

## Norma

Los datos son un activo estratégico de Merchly AI.

## Requisitos

Todo sistema deberá considerar:

* Seguridad.
* Integridad.
* Privacidad.
* Organización.
* Recuperación.

---

# 11. Seguridad por Diseño

## Norma

La seguridad debe incorporarse desde el inicio.

## Reglas

Nunca almacenar:

* Contraseñas sin protección.
* Claves privadas expuestas.
* Información sensible sin control.

Debe aplicarse:

* Control de accesos.
* Gestión de permisos.
* Auditoría.

---

# 12. Pruebas de Calidad

## Norma

Toda funcionalidad importante deberá validarse antes de producción.

Tipos de pruebas:

* Unitarias.
* Integración.
* Rendimiento.
* Seguridad.
* Validación funcional.

---

# 13. Revisión de Código

## Norma

Todo cambio relevante debe pasar por revisión.

Debe evaluarse:

* Calidad.
* Seguridad.
* Arquitectura.
* Mantenimiento futuro.

---

# 14. Gestión de Errores

## Norma

Los errores deben registrarse y analizarse.

Todo error importante debe incluir:

* Descripción.
* Causa.
* Solución.
* Prevención futura.

---

# 15. Uso de Dependencias Externas

## Norma

Toda dependencia externa debe evaluarse antes de incorporarse.

Debe analizarse:

* Seguridad.
* Costo.
* Mantenimiento.
* Dependencia del proveedor.
* Alternativas existentes.

---

# 16. Optimización

## Norma

La optimización deberá basarse en datos reales.

No se optimizará:

* Por intuición.
* Por moda.
* Antes de identificar problemas reales.

---

# 17. Infraestructura

## Norma

La infraestructura debe diseñarse pensando en crecimiento futuro.

Debe considerar:

* Escalabilidad.
* Disponibilidad.
* Seguridad.
* Costos.

---

# 18. Preparación para Automatización

## Norma

Todo proceso repetitivo deberá evaluarse como candidato para automatización.

La automatización debe:

* Reducir esfuerzo.
* Mejorar precisión.
* Ser medible.

---

# 19. Criterio de Finalización

Una funcionalidad solo se considera terminada cuando:

☐ Código implementado.

☐ Documentación actualizada.

☐ Pruebas realizadas.

☐ Seguridad revisada.

☐ Integración validada.

☐ Métricas definidas.

☐ Cambios registrados.

---

# Resumen Ejecutivo para IA

Merchly AI debe construirse mediante una ingeniería disciplinada basada en modularidad, documentación, seguridad, simplicidad, pruebas y automatización.

Toda contribución humana o generada mediante IA debe cumplir estas normas antes de integrarse al sistema.

---

# Lista de Verificación

Antes de aprobar cualquier desarrollo:

* ¿Está documentado?
* ¿Es modular?
* ¿Es mantenible?
* ¿Tiene pruebas?
* ¿Es seguro?
* ¿Puede escalar?
* ¿Reduce complejidad?
* ¿Está alineado con los principios de Merchly AI?

---

# Vigencia

Estas normas representan el estándar técnico mínimo de Merchly AI.

Cualquier excepción deberá ser documentada y aprobada mediante el sistema de gobernanza establecido.
