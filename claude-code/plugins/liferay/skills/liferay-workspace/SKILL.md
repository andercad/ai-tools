---
name: liferay-workspace
description: 'Liferay DXP. Workspace Gradle y ciclo de vida: detectar versión (liferay.workspace.product) y modelo de despliegue, estructura de carpetas, Blade CLI, tareas Gradle, dependencias (release.dxp.api, compileOnly project, sin mavenLocal), JDK y javax/jakarta, y actualizaciones trimestrales (upgrade de base de datos, upgrade steps, modernización de código heredado). Usar al empezar en un proyecto Liferay, crear módulos o client extensions con Blade, enlazar módulos, compilar o desplegar, resolver errores de dependencias, subir la versión del workspace o ejecutar un upgrade. No usar para decidir la estrategia de upgrade (liferay-version-upgrade).'
---

# Workspace y actualizaciones

## Reglas clave
- La versión de `liferay.workspace.product` (en `gradle.properties`) es la fuente de verdad; mínimo 2025.Q1: si es anterior, avisa y pregunta.
- Detecta el modelo de despliegue antes de diseñar (SaaS, PaaS, Docker/Kubernetes, bundle); si no es concluyente, pregunta.
- Dependencias: APIs de Liferay con `release.dxp.api` + `compileOnly`; módulos del workspace con `compileOnly project(...)`; nunca `mavenLocal()`.
- No incluyas en el módulo librerías que ya proporciona Liferay.
- Un upgrade se prueba en un entorno con copia de datos antes de producción.

## Referencias
| Tema | Fichero |
|---|---|
| Workspace, versión, modelo de despliegue, Blade, dependencias, tareas | [workspace.md](references/workspace.md) |
| Actualizaciones trimestrales, upgrade de BD, upgrade steps, modernización | [upgrades.md](references/upgrades.md) |

## Checklists
### Workspace
- [ ] Versión leída de `liferay.workspace.product` y ≥ 2025.Q1 (si no, preguntado)
- [ ] Modelo de despliegue identificado o preguntado
- [ ] JDK y espacio de nombres `javax`/`jakarta` de la versión
- [ ] APIs de Liferay con `release.dxp.api` y `compileOnly`, sin versiones sueltas
- [ ] Módulos del workspace enlazados con `compileOnly project(...)`; sin `mavenLocal()`
- [ ] Librerías que ya proporciona Liferay sin incluir en el módulo
- [ ] Configuración por entorno en `configs/<entorno>`, sin secretos
- [ ] Tareas comprobadas con `./gradlew tasks`

### Actualizaciones trimestrales
- [ ] Notas de la versión leídas; ruta de actualización soportada
- [ ] Copia de seguridad completa y prueba con copia de producción
- [ ] Workspace actualizado, compilación limpia, overrides revisados
- [ ] Método de upgrade de base de datos adecuado; un solo nodo en clúster
- [ ] Upgrade steps repetibles para cambios de esquema propios
- [ ] Commerce, PaaS y reindexado según sus guías
- [ ] Plan de modernización priorizado por riesgo en upgrades
