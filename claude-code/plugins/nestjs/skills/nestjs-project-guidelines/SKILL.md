---
name: nestjs-project-guidelines
description: Crea o actualiza en el CLAUDE.md del proyecto el bloque "Convenciones NestJS" (política de tests unitarios y e2e, docs, API docs, workspace, verify) y las reglas de implementación y de specs que aplican en cualquier flujo, incluido /spec y /spec-impl. Usar cuando el proyecto no tiene ese bloque, el usuario pide configurar los agentes NestJS para su proyecto o cambiar la política de calidad. No usar para implementar código.
---

# Política del proyecto → `CLAUDE.md`

Claude Code carga el `CLAUDE.md` en cada sesión y en cualquier flujo (también `/spec` y `/spec-impl`); un plugin no puede aportarlo. Por eso las reglas van ahí. El agente `nestjs-dev` y el hook de parada leen el bloque `## Convenciones NestJS`.

## Bloque a escribir (adapta las claves; borra comentarios)

````markdown
## Convenciones NestJS
- tests: required | optional | none      # .spec.ts por servicio, controlador, resolver, guard, pipe, interceptor, filtro nuevos
- e2e: required | optional | none        # test/*.e2e-spec.ts por endpoint nuevo
- coverage: 80                           # opcional
- docs: jsdoc | none                     # JSDoc en API pública (clases, métodos públicos)
- api-docs: swagger | none               # decoradores @nestjs/swagger en controladores y DTOs
- workspace: app | nest-monorepo | nx
- verify: npm run build && npm test && npm run lint

### Al implementar código NestJS
Aplica siempre, también al implementar una spec:
1. Antes de escribir una pieza >30 líneas o que toque varias clases, decide en 5–8 líneas piezas, responsabilidad única, dependencias y extensión (SOLID; skill `nestjs-solid`). Sin capas ni abstracciones prematuras. No generes para luego rehacer.
2. Controladores, resolvers y handlers sin lógica de negocio; DI solo por constructor; toda entrada validada con DTOs (`whitelist` + `forbidNonWhitelisted`); no expongas entidades.
3. Seguridad desde el primer borrador (skill `nestjs-security`): autorización por recurso, sin asignación masiva, consultas parametrizadas, sin secretos en el repo.
4. `docs: jsdoc` → JSDoc conciso en API pública, nada sobre lo evidente.
5. `tests: required` → crea el `.spec.ts` junto a cada pieza nueva o modificada, en el mismo paso, no en uno posterior. `e2e: required` → test e2e por endpoint nuevo.
6. Solo APIs estables de la versión instalada de Nest; ante la duda, consulta docs.nestjs.com.
7. Antes de dar un paso por terminado, ejecuta `verify` y corrige. Informa qué verificaste y qué no.

### Al redactar specs de este proyecto
Además de lo que pida la plantilla de `/spec`, cada spec NestJS incluye:
- **Diseño de clases**: módulos, piezas, responsabilidad de cada una y dependencias (SOLID).
- **Contrato de API**: rutas, DTOs de entrada/salida, códigos de estado y errores, y reglas de autorización por recurso.
- **Plan de tests** por pieza (casos y límites) si `tests` ≠ none, y e2e si `e2e` ≠ none, en el mismo paso del plan que la pieza.
- **Comando `verify`** como criterio de aceptación final.
````

Defaults si falta una clave: `tests: none`, `e2e: none`, `docs: jsdoc`, `api-docs: swagger` si `@nestjs/swagger` está instalado, `verify` deducible de `package.json` y del workspace.

## Pasos
1. Lee el `CLAUDE.md`; si ya existe el bloque, actualízalo, no lo dupliques.
2. Deduce valores del repo: `package.json` (runner, scripts, `@nestjs/swagger`, ORM), `nest-cli.json`/`nx.json`, `tsconfig*.json` (alias), `src/`, ESLint.
3. Pregunta solo lo no deducible (máx. 3): política de tests unitarios/e2e, documentación de API y si hay normativa o datos sensibles.
4. Escribe el bloque con los valores reales; elimina las líneas que no apliquen. Añade, solo si aporta, estructura, alias, ORM y autenticación con [templates/coding-guidelines.md](templates/coding-guidelines.md) como guía.
5. Muestra el diff; no inventes datos de cliente ni de dominio.
