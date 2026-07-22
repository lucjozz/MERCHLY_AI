# README.md

---

title: Organización de Merchly AI
document: 100-README
version: 1.0.0
status: Approved
owner: CEO & CTO
last_updated: 2026-07-22
next_review: 2027-01-22
related:

* ../000-Constitucion/
* ../001-Arquitectura/
* ../002-CTO/
* ../003-CEO/

---

# Organización de Merchly AI

## Propósito

La carpeta `100-Organizacion` define la estructura organizacional de MERCHLY AI como una empresa tecnológica asistida por inteligencia artificial.

Su objetivo es establecer:

* La estructura jerárquica del sistema.
* Los roles ejecutivos.
* Los departamentos.
* Los equipos de trabajo.
* Los roles de inteligencia artificial.
* La asignación de responsabilidades.
* El flujo de decisiones.
* Las reglas de gobernanza operativa.
* Los mecanismos de delegación y comunicación.

Esta documentación permite que MERCHLY AI evolucione de un repositorio técnico a un sistema operativo empresarial coherente, escalable y mantenible.

---

# Objetivo de esta carpeta

La organización responde a la pregunta:

> **¿Quién hace qué dentro de MERCHLY AI?**

Mientras que la arquitectura define cómo está construido el sistema, la organización define cómo se coordinan las personas, los agentes IA y los procesos.

---

# Alcance

La carpeta `100-Organizacion` documenta:

* La estructura empresarial de MERCHLY AI.
* Los roles humanos ejecutivos.
* Los departamentos funcionales.
* Los equipos técnicos y operativos.
* Los roles abstractos de inteligencia artificial.
* Las responsabilidades de cada rol.
* Las relaciones entre áreas.
* Los límites de autoridad.
* Los procesos de aprobación.
* La comunicación interna.
* La evolución futura de la organización.

No reemplaza la documentación técnica específica de cada área.

---

# Principio organizacional

MERCHLY AI se organiza como una empresa tecnológica donde:

* Los humanos definen estrategia, prioridades y decisiones críticas.
* Los agentes IA asisten, analizan, ejecutan y optimizan procesos.
* Las automatizaciones reducen trabajo repetitivo.
* Cada responsabilidad tiene un responsable claro.
* Ninguna decisión crítica queda sin supervisión humana.

---

# Estructura conceptual

```text
MERCHLY AI
│
├── Dirección Ejecutiva
│   ├── CEO
│   ├── CTO
│   ├── CMO
│   ├── COO
│   └── CFO
│
├── Departamentos
│   ├── Tecnología
│   ├── Marketing
│   ├── Operaciones
│   ├── Finanzas
│   └── Investigación
│
├── Equipos
│   ├── Backend
│   ├── Frontend
│   ├── Base de Datos
│   ├── Automatización
│   ├── SEO
│   ├── Publicidad
│   └── Analítica
│
└── Agentes IA
    ├── Arquitecto IA
    ├── Programador IA
    ├── Investigador IA
    ├── Revisor IA
    ├── Analista IA
    ├── Especialista Marketing IA
    └── QA IA
```

---

# Principios de organización

## Responsabilidad clara

Cada función debe tener un responsable identificado.

---

## Separación de decisiones

Las decisiones estratégicas, tácticas y operativas deben distinguirse claramente.

---

## Delegación controlada

Las tareas pueden delegarse a personas, agentes IA o automatizaciones, pero los límites deben estar documentados.

---

## Independencia de proveedores

Los roles de inteligencia artificial se documentan por capacidad, no por proveedor específico.

---

## Escalabilidad

La estructura debe permitir incorporar nuevos departamentos, equipos, agentes IA y procesos sin reorganizar toda la documentación.

---

# Relación con otras carpetas

| Carpeta            | Función                                                  |
| ------------------ | -------------------------------------------------------- |
| `000-Constitucion` | Define identidad, principios y reglas permanentes.       |
| `001-Arquitectura` | Define el diseño técnico del sistema.                    |
| `100-Organizacion` | Define la estructura empresarial y de responsabilidades. |
| `002-CTO`          | Define la dirección técnica.                             |
| `003-CEO`          | Define la dirección estratégica.                         |
| `004-020`          | Documentan áreas específicas de ejecución.               |

---

# Estructura de esta carpeta

```text
100-Organizacion/
├── README.md
├── 01-Organigrama.md
├── 02-Estructura-Empresarial.md
├── 03-Roles-Ejecutivos.md
├── 04-Departamentos.md
├── 05-Capacidades-Organizacionales.md
├── 06-Agentes-IA.md
└── 07-Matriz-RACI.md
```

Esta carpeta usa una estructura condensada de 7 documentos en lugar de un documento por cada subtema, para evitar duplicar contenido entre archivos.

---

# Descripción de los documentos

| Documento                            | Propósito                                                      |
| ------------------------------------- | -------------------------------------------------------------- |
| `01-Organigrama.md`                  | Representa la estructura jerárquica de la organización.        |
| `02-Estructura-Empresarial.md`       | Define las áreas principales de la empresa.                    |
| `03-Roles-Ejecutivos.md`             | Define responsabilidades, autoridad y delegación de CEO, CTO, CMO, COO y CFO. |
| `04-Departamentos.md`                | Describe los departamentos y los equipos de trabajo dentro de cada Dirección Ejecutiva. |
| `05-Capacidades-Organizacionales.md` | Define las capacidades permanentes de la organización, independientes de personas o tecnologías. |
| `06-Agentes-IA.md`                   | Define el catálogo de roles de inteligencia artificial y su independencia de proveedor. |
| `07-Matriz-RACI.md`                  | Asigna responsables, aprobadores, consultados e informados por tipo de decisión y departamento. |

El flujo de decisiones y la gobernanza operativa se documentan en `../000-Constitucion/07-Gobernanza.md`, para mantener una única fuente de verdad sobre cómo se decide dentro de Merchly AI. El historial de cambios organizativos se registra junto con el resto del proyecto en `../000-Constitucion/14-Historial.md`, sin duplicar un historial por carpeta.

---

# Regla fundamental

> **Toda responsabilidad debe tener un responsable claro.**

> **Toda decisión relevante debe tener un aprobador definido.**

> **Toda delegación debe tener límites documentados.**

> **Toda automatización debe tener supervisión apropiada.**

---

# Relación humano - IA

MERCHLY AI adopta un modelo híbrido donde:

* La IA propone opciones.
* La IA analiza información.
* La IA ejecuta tareas delegadas.
* La IA optimiza procesos repetitivos.
* Los humanos validan decisiones estratégicas.
* Los humanos mantienen control final sobre el negocio.

---

# Resumen ejecutivo para IA

La carpeta `100-Organizacion` define cómo se estructura MERCHLY AI como empresa tecnológica.

Debe utilizarse para comprender roles, responsabilidades, autoridad, delegación, comunicación y flujo de decisiones antes de ejecutar tareas que afecten a otras áreas del sistema.

---

# Estado

Documento:

`100-README`

Versión:

`1.0.0`

Estado:

`Approved`

Próximo documento recomendado:

`01-Organigrama.md`

---

# Fin del documento

