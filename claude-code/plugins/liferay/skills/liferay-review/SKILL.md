---
name: liferay-review
description: 'Revisa con el agente liferay-architect los cambios actuales (git diff) o una ruta, contra las reglas Liferay del plugin. Solo lectura.'
disable-model-invocation: true
argument-hint: "[ruta o rango git opcional]"
---

Objetivo: `$ARGUMENTS` (si está vacío, el diff sin confirmar: `git diff HEAD`).

Delega en el subagente `liferay-architect` una revisión de esos cambios. Su prompt debe incluir la lista de ficheros y pedir hallazgos con severidad BLOCKER/MAJOR/MINOR (BLOCKER y MAJOR con evidencia `fichero:línea`), agrupados por: mecanismo de extensión elegido y modelo de despliegue (`liferay-extension-model`), versión y APIs de `liferay.workspace.product`, permisos (`*LocalService` sin comprobación, `ModelResourcePermission`), seguridad (FreeMarker sin escapar, `serviceLocator`, secretos, SQL directo, CSRF/XSS), OSGi (`*ServiceUtil`, JSP con scriptlets, IDs fijos en lugar de nombres), configuración como código y tests. Sin modificar ficheros.

Devuelve solo los hallazgos y el veredicto.
