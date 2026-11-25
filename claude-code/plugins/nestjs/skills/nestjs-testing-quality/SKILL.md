---
name: nestjs-testing-quality
description: 'Tests y calidad de código NestJS. Usar al escribir o corregir tests unitarios de servicios, guards y pipes, tests de controladores, e2e con supertest, base de datos real con Testcontainers, mocks tipados y cobertura (Jest o Vitest con @nestjs/testing), y al configurar ESLint, Prettier, SonarQube, logging (Logger/pino) o pasar el checklist pre-PR. No usar para estrategia de pruebas a nivel arquitectura (agente nestjs-architect).'
---

# Tests y calidad

## Reglas clave
- Usa el runner del proyecto (Jest o Vitest); sin `any`, tampoco en tests; mocks tipados.
- Prueba comportamiento y casos límite, no implementación; un test e2e por endpoint nuevo si `e2e` lo pide.
- Ejecuta el test antes de informar; no declares que pasa sin haberlo corrido.
- Sin `console.log` en producción: usa el logger del proyecto; no registres contraseñas, tokens ni datos personales.
- Sin código muerto ni supresiones de lint sin motivo; complejidad cognitiva baja.
- Cobertura según `coverage:` del `CLAUDE.md` del proyecto.

## Referencias
| Tema | Fichero |
|---|---|
| Unitarios, controladores, e2e, Testcontainers, cobertura | [testing.md](references/testing.md) |
| ESLint, Prettier, SonarQube, logging, checklist pre-PR | [quality.md](references/quality.md) |
