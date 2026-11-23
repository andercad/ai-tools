---
name: angular-review
description: Revisa con el agente angular-architect los cambios actuales (git diff) o una ruta, contra las reglas Angular del plugin. Solo lectura.
disable-model-invocation: true
argument-hint: "[ruta o rango git opcional]"
---

Objetivo: `$ARGUMENTS` (si está vacío, el diff sin confirmar: `git diff HEAD`).

Delega en el subagente `angular-architect` una revisión de esos cambios. Su prompt debe incluir la lista de ficheros y pedir hallazgos con severidad BLOCKER/MAJOR/MINOR (BLOCKER y MAJOR con evidencia `fichero:línea`), agrupados por: reglas Angular de la versión instalada, estado/HTTP, seguridad, accesibilidad, rendimiento y tests. Sin modificar ficheros.

Devuelve solo los hallazgos y el veredicto.
