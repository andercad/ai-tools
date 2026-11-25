---
name: angular-workspace
description: 'Estructura de workspace Angular. Usar en monorepos (Angular CLI multiproyecto o Nx), al crear o publicar librerías con ng-packagr, o al gestionar variables de entorno, librerías de terceros y actualizaciones de versión (ng update, nx migrate). No usar para decidir si adoptar monorepo o microfrontends (agente angular-architect) ni para planificar upgrades de versión mayor (angular-modernization-governance).'
---

# Workspace, librerías y entorno

## Reglas clave
- Identifica el tipo de workspace (`angular.json` multiproyecto, `nx.json`, app única) antes de escribir código; no lo cambies por iniciativa propia.
- Monorepo: el código reutilizable va en librerías; entre proyectos solo imports por el punto de entrada público; respeta las reglas de límites; el frontend no importa código de backend.
- Ejecuta tareas del proyecto afectado (`ng build <proyecto>`, `nx affected -t lint test build`), nunca un comando que asuma app única.
- Configuración por entorno fuera del código; sin secretos en el repo.
- Antes de añadir una dependencia: ¿ya existe algo equivalente?, mantenimiento, licencia, vulnerabilidades.

## Referencias
| Tema | Fichero |
|---|---|
| Angular CLI multiproyecto y Nx, límites, comandos, CI | [monorepo.md](references/monorepo.md) |
| Crear, versionar y publicar librerías | [library.md](references/library.md) |
| Variables de entorno, terceros, actualizar Angular | [environment.md](references/environment.md) |
