# Plugin Angular para Claude Code

Flujo spec → implementación → verificación para Angular (app única, Angular CLI multiproyecto o Nx), con la política de calidad definida por proyecto en su `CLAUDE.md`.

## Qué incluye
- **`angular-dev`**: diseña con SOLID antes de escribir, genera código accesible y documentado, crea tests si la política lo pide y verifica (`verify`) antes de informar.
- **`angular-architect`** (solo lectura): evalúa, compara alternativas, redacta ADR, matrices de decisión y riesgos, planifica upgrades.
- **Skills propias**: `angular-solid` (precargada en `angular-dev`), `angular-quality-a11y`, `angular-i18n`, `angular-security`, `angular-workspace`, `angular-project-guidelines`, más 8 de arquitectura (`angular-architecture-assessment`, `angular-architecture`, `angular-reactivity-state`, `angular-rendering-performance`, `angular-quality-security`, `angular-backend-integration`, `angular-liferay-integration`, `angular-modernization-governance`).
- **Convenciones por defecto** (skill `angular-conventions`, precargada en `angular-dev`): `src/app/shared/` (común y global) + una carpeta por funcionalidad (`components/`, `pages/`, `services/`...); componentes de ruta en `pages/`; un `.html` por componente; alias de `tsconfig` por carpeta (`@shared/*`, `@<funcionalidad>/*`); separadores de sección en clases. Código nuevo; no migra lo existente.
- **Hooks**: `PostToolUse` (prettier/eslint si el proyecto los tiene) y `Stop`/`SubagentStop` (bloquea el cierre si `tests: required` y hay componentes/servicios/directivas/pipes/guards sin `.spec.ts`, o si un componente usa `template:` inline salvo `templates: inline`).
- **`/angular:angular-review`**: revisión de solo lectura del diff.

## Dependencias (se instalan solas y siguen a `main`)
El `marketplace.json` envuelve un repo que no es plugin:
- `angular-skills`: skill oficial `angular-developer` (`angular/angular`, `skills/dev-skills/angular-developer`, MIT). Sintaxis, señales, formularios, rutas, SSR, testing, CLI.

Sin `sha` fijado, recibe cambios de upstream automáticamente (con auto-update del marketplace activado); a cambio, un cambio roto de upstream te llega sin avisar. Para congelar una versión, añade `"sha": "<40 hex>"` en la entrada del marketplace.

## Política del proyecto (bloque en el `CLAUDE.md`)
```markdown
## Convenciones Angular
- tests: required | optional | none
- coverage: 80
- a11y: WCAG-2.2-AA        # base obligatoria; cambia solo si el proyecto exige otro nivel
- docs: jsdoc | none
- i18n: es,en | none
- workspace: app | cli-multiproject | nx
- structure: features       # defecto; describe otra si el repo ya usa una distinta
- templates: external | inline   # external (defecto): sin template inline
- verify: ng build && ng test --watch=false && ng lint
```
Pide a Claude que use la skill `angular-project-guidelines`: escribe el bloque y, debajo, las reglas de implementación y de specs, que aplican en cualquier flujo (incluidos `/spec` y `/spec-impl`). Defaults si faltan claves: `a11y: WCAG-2.2-AA` (siempre), `tests: none`, `docs: jsdoc`, `i18n: none`.

## Instalación
```bash
claude plugin marketplace add ./claude-code      # desde la raíz de este repo
claude plugin install angular@ai-tools           # instala también las dependencias
```
Prueba sin instalar (sin resolver dependencias): `claude --plugin-dir claude-code/plugins/angular`.

## Validación
```bash
claude plugin validate claude-code/plugins/angular
node claude-code/plugins/angular/validation/check.mjs
```
`check.mjs` es estático. Para comportamiento, usa `validation/test-prompts.md`.
