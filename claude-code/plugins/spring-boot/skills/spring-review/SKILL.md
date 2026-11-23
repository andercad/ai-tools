---
name: spring-review
description: Revisa con el agente spring-boot-architect los cambios actuales (git diff) o una ruta, contra las reglas Spring Boot del plugin. Solo lectura.
disable-model-invocation: true
argument-hint: "[ruta o rango git opcional]"
---

Objetivo: `$ARGUMENTS` (si está vacío, el diff sin confirmar: `git diff HEAD`).

Delega en el subagente `spring-boot-architect` una revisión de esos cambios. Su prompt debe incluir la lista de ficheros y pedir hallazgos con severidad BLOCKER/MAJOR/MINOR (BLOCKER y MAJOR con evidencia `fichero:línea`), agrupados por: reglas de Spring Boot de la versión instalada, validación/DTOs, seguridad (autorización por recurso, asignación masiva, inyección), transacciones/persistencia, errores/logging y tests. Sin modificar ficheros.

Devuelve solo los hallazgos y el veredicto.
