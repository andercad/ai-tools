---
name: nestjs-review
description: Revisa con el agente nestjs-architect los cambios actuales (git diff) o una ruta, contra las reglas NestJS del plugin. Solo lectura.
disable-model-invocation: true
argument-hint: "[ruta o rango git opcional]"
---

Objetivo: `$ARGUMENTS` (si está vacío, el diff sin confirmar: `git diff HEAD`).

Delega en el subagente `nestjs-architect` una revisión de esos cambios. Su prompt debe incluir la lista de ficheros y pedir hallazgos con severidad BLOCKER/MAJOR/MINOR (BLOCKER y MAJOR con evidencia `fichero:línea`), agrupados por: reglas de NestJS de la versión instalada, validación/DTOs, seguridad (autorización por recurso, asignación masiva, inyección), persistencia, errores/logging y tests. Sin modificar ficheros.

Devuelve solo los hallazgos y el veredicto.
