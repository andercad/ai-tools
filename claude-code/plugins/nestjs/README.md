# Plugin NestJS para Claude Code

Flujo spec → implementación → verificación para NestJS (app única, modo monorepo del Nest CLI o Nx), con la política de calidad definida por proyecto en su `CLAUDE.md`.

## Qué incluye
- **`nestjs-dev`**: diseña con SOLID antes de escribir, genera código seguro y documentado, crea tests (unitarios y e2e) si la política lo pide y verifica (`verify`) antes de informar.
- **`nestjs-architect`** (solo lectura): evalúa, compara alternativas, redacta ADR, matrices de decisión y riesgos, planifica upgrades.
- **Skills de desarrollo**: `nestjs-solid` (precargada en `nestjs-dev`), `nestjs-modules-services`, `nestjs-api`, `nestjs-persistence`, `nestjs-security`, `nestjs-testing-quality`, `nestjs-graphql`, `nestjs-microservices`, `nestjs-workspace`, `nestjs-project-guidelines`.
- **Skills de arquitectura**: `nestjs-architecture-assessment`, `nestjs-modularity-domain`, `nestjs-api-integration`, `nestjs-data-messaging`, `nestjs-security-identity`, `nestjs-observability-resilience`, `nestjs-runtime-deployment`, `nestjs-modernization-governance`.
- **Hooks**: `PostToolUse` (prettier/eslint si el proyecto los tiene) y `Stop`/`SubagentStop` (bloquea el cierre si `tests: required` y hay controladores, servicios, resolvers o filtros sin `.spec.ts`).
- **`/nestjs:nestjs-review`**: revisión de solo lectura del diff.

## Sin dependencias externas
A diferencia del plugin Angular, no hay skill oficial de NestJS que reutilizar: las skills de desarrollo son propias (derivadas de `github-copilot/NestJS-Architect`, agrupadas con el detalle en `references/`). Para APIs que dependen de versión, los agentes consultan docs.nestjs.com.

## Política del proyecto (bloque en el `CLAUDE.md`)
```markdown
## Convenciones NestJS
- tests: required | optional | none
- e2e: required | optional | none
- coverage: 80
- docs: jsdoc | none
- api-docs: swagger | none
- workspace: app | nest-monorepo | nx
- verify: npm run build && npm test && npm run lint
```
Pide a Claude que use la skill `nestjs-project-guidelines`: escribe el bloque y, debajo, las reglas de implementación y de specs, que aplican en cualquier flujo (incluidos `/spec` y `/spec-impl`). Defaults si faltan claves: `tests: none`, `e2e: none`, `docs: jsdoc`, `api-docs: swagger` si `@nestjs/swagger` está instalado.

## Instalación
```bash
claude plugin marketplace add ./claude-code      # desde la raíz de este repo
claude plugin install nestjs@ai-tools
```
Prueba sin instalar: `claude --plugin-dir claude-code/plugins/nestjs`.

### Actualización

```bash
claude plugin marketplace update ai-tools
claude plugin update nestjs@ai-tools
```

Reinicia Claude Code para aplicar.

## Mantenimiento (desarrolladores)

Tras editar el plugin, sube `version` en `.claude-plugin/plugin.json`: sin cambio de versión, Claude Code usa la caché y los consumidores no reciben la novedad. Después valida, haz commit/push y avisa al equipo para que ejecute la actualización.

```bash
claude plugin validate claude-code/plugins/nestjs
node claude-code/plugins/nestjs/validation/check.mjs
```
`check.mjs` es estático (frontmatter, enlaces, skills citadas, restos de Copilot). Para comportamiento, usa `validation/test-prompts.md`.

## Origen del contenido
Las skills de desarrollo derivan de `github-copilot/NestJS-Architect` y las de arquitectura de `copilot-365/NestJS-Architecture-Agent`; los cambios no se sincronizan solos.
