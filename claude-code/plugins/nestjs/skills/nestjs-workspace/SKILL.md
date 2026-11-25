---
name: nestjs-workspace
description: 'Workspace y configuración NestJS. Usar en monorepos (modo monorepo del Nest CLI o Nx con @nx/nest) al crear apps o librerías, compartir módulos, importar entre proyectos, límites y etiquetas, ejecutar build/test/lint por proyecto o lo afectado, CI y contratos con un frontend; y al añadir variables de entorno, validar configuración, usar ConfigService, registerAs o gestionar secretos. No usar para decidir si adoptar monorepo o microservicios (agente nestjs-architect).'
---

# Workspace y configuración

## Reglas clave
- Identifica el tipo de workspace (`nest-cli.json` con `"monorepo": true`, `nx.json`, app única) y no lo cambies por iniciativa propia.
- Código compartido en librerías; entre proyectos solo por el punto de entrada público (sin imports profundos ni rutas relativas entre proyectos); respeta etiquetas y límites.
- Las librerías de backend nunca se importan desde el frontend; los contratos compartidos son solo tipos, sin decoradores ni dependencias de servidor.
- Ejecuta tareas del proyecto afectado (`nest build <app>`, `nx affected -t lint test build`), nunca un comando que asuma app única.
- Nunca `process.env` fuera del esquema de configuración: `ConfigService` con validación al arrancar; sin `.env` ni secretos en el repo.

## Referencias
| Tema | Fichero |
|---|---|
| Nest CLI monorepo y Nx, límites, comandos, CI, contratos | [monorepo.md](references/monorepo.md) |
| `@nestjs/config`, validación, `registerAs`, secretos | [config.md](references/config.md) |
