---
name: liferay-config-operations
description: 'Liferay DXP. Configuración, despliegue y operación: portal-ext.properties, variables LIFERAY_*, ficheros .config de OSGi, System/Instance/Site Settings, feature flags; despliegue self-hosted (bundle, Docker, Kubernetes con Helm, clúster, almacén de documentos); Liferay PaaS (LCP.json) y SaaS; diagnóstico (logs, Gogo Shell, módulos que no arrancan, rendimiento, conversión de documentos). Usar al cambiar una propiedad o configuración, dockerizar o desplegar, configurar un LCP.json, decidir qué cabe en SaaS, o investigar un fallo o lentitud. No usar para decisiones de arquitectura cloud (liferay-cloud-operations).'
---

# Configuración, despliegue y operación

## Reglas clave
- Secretos nunca en el repositorio (`portal-ext.properties`, `.config`, `client-extension.yaml`, `LCP.json`): variables de entorno o secretos de Kubernetes/PaaS.
- Configuración por entorno en `configs/<entorno>`; lo común en `configs/common`.
- SaaS: solo client extensions y configuración, sin `portal-ext.properties` ni acceso al servidor. PaaS: configuración en el repositorio y en las variables del servicio.
- Usa la variable de entorno documentada junto a cada propiedad (`Env:` en `portal.properties`) en lugar de construirla de memoria.
- Diagnostica con logs y Gogo Shell antes de cambiar nada; no reinicies para «ver si se arregla».

## Referencias
| Tema | Fichero |
|---|---|
| portal-ext, variables, .config, scopes, config por entorno | [configuration.md](references/configuration.md) |
| Bundle, Docker, Kubernetes, clúster, almacén de documentos | [deployment.md](references/deployment.md) |
| PaaS (LCP.json) y SaaS | [cloud.md](references/cloud.md) |
| Logs, Gogo Shell, rendimiento, documentos, soporte | [troubleshooting.md](references/troubleshooting.md) |

## Checklists
### portal-ext
- [ ] Cada configuración en su mecanismo y ámbito
- [ ] Propiedades copiadas de la referencia de la versión; ninguna modificación de `portal.properties`
- [ ] Variables `LIFERAY_*` para secretos y valores por entorno
- [ ] `.config` con PID y tipos exactos (exportados desde System Settings)
- [ ] `configs/common` + `configs/<entorno>`; `prod` mínimo
- [ ] Sin feature flags beta/dev salvo petición explícita

### Bundle
- [ ] Base de datos externa y soportada; búsqueda remota; almacén compartido si hay varios nodos
- [ ] Mismo JDK en compilación y ejecución; JVM con UTF-8 y GMT
- [ ] Imagen oficial con la etiqueta de la versión del workspace
- [ ] Variables `LIFERAY_*` copiadas de `portal.properties`; secretos fuera de la imagen y del repositorio
- [ ] Probes de Kubernetes adaptadas al arranque de Liferay
- [ ] Clúster con Cluster Link, sesiones persistentes y despliegues en todos los nodos
- [ ] Upgrades de base de datos fuera de *rolling updates*

### PaaS (LCP.json) y SaaS
- [ ] Modelo identificado (PaaS o SaaS) y restricciones respetadas
- [ ] PaaS: `LCP.json` por servicio, imágenes alineadas con `liferay.workspace.product`, overrides por entorno
- [ ] PaaS: secretos en la consola, no en el repositorio
- [ ] Mismo build promocionado `dev` → `uat` → `prd`; copia de seguridad antes de upgrades
- [ ] SaaS: nada que requiera módulos OSGi o acceso al servidor
- [ ] SaaS: client extensions desplegadas también en el entorno DR si existe

### Logs
- [ ] Evidencias recogidas antes de cambiar nada
- [ ] Primera excepción y su causa identificadas
- [ ] Gogo Shell para bundles y componentes
- [ ] Diferencias de versión, configuración y despliegue entre entornos revisadas
- [ ] Mediciones antes y después en problemas de rendimiento
- [ ] Niveles de log restaurados; sin DEBUG en producción
