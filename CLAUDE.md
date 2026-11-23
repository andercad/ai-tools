# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repo

Colección de herramientas de IA (no hay app ni build global): contenido en Markdown/PowerShell/Python que define agentes y skills. Idioma del contenido: español. Tres áreas independientes:

- `claude-code/.claude/` — config de Claude Code: hook `PostToolUse` (`hooks/format-lint.mjs`, corre prettier + eslint con `npx` sobre el fichero editado; ignora `.claude/`, `node_modules/`, etc.), comando `/worktree` (worktree en `.trees/[nombre]` + subagente) y skill `telegram-send` (`send.mjs`, lee `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` de `settings.local.json`; no commitear secretos).
- `claude-code/` es también un marketplace de plugins (`.claude-plugin/marketplace.json`). `claude-code/plugins/angular/` (piloto): agentes `angular-dev` y `angular-architect` (solo lectura), skills con `references/`, hooks (formato/lint y Stop que exige specs si `tests: required` en el `CLAUDE.md` del proyecto). Depende, vía entrada del marketplace con `git-subdir`, de la skill oficial `angular-developer` (angular/angular): no se copia. Funciona con `/spec` y `/spec-impl` (se instalan aparte): las reglas llegan por el `CLAUDE.md` del proyecto, que genera la skill `angular-project-guidelines`. Instalar: `claude plugin marketplace add ./claude-code`. Validar: `claude plugin validate claude-code/plugins/angular` y `node claude-code/plugins/angular/validation/check.mjs`. Sus skills derivan de `github-copilot/Angular-Architect` y `copilot-365/Angular-Enterprise-Architect`; los cambios no se sincronizan solos.
- `claude-code/plugins/nestjs/`: mismo patrón que Angular para NestJS (agentes `nestjs-dev` y `nestjs-architect`, hooks, bloque `## Convenciones NestJS` en el `CLAUDE.md` del proyecto vía skill `nestjs-project-guidelines`). Sin dependencia externa (no hay skill oficial de NestJS): las skills de desarrollo derivan de `github-copilot/NestJS-Architect` (16 skills agrupadas en 9, detalle en `references/`) y las de arquitectura de `copilot-365/NestJS-Architecture-Agent`; no se sincronizan solas. Validar: `claude plugin validate claude-code/plugins/nestjs` y `node claude-code/plugins/nestjs/validation/check.mjs`.
- `claude-code/plugins/spring-boot/`: mismo patrón para Spring Boot 3.x/4.x con Java (agentes `spring-boot-dev` y `spring-boot-architect`, bloque `## Convenciones Spring Boot` en el `CLAUDE.md` del proyecto vía skill `spring-project-guidelines`; hooks: Spotless solo si está configurado y Stop que exige `XTest.java` si `tests: required`). Sin dependencia externa: las skills de desarrollo derivan de `github-copilot/SpringBoot-Architect` (con `references/`) y las de arquitectura de `copilot-365/Spring-Boot-Architecture-Agent`; no se sincronizan solas. Validar: `claude plugin validate claude-code/plugins/spring-boot` y `node claude-code/plugins/spring-boot/validation/check.mjs`.
- `copilot-365/<Agente>/` — agentes para Microsoft 365 Copilot (Agent Builder): Angular-Enterprise-Architect, Liferay-Enterprise-Architect, NestJS-Architecture-Agent, Spring-Boot-Architecture-Agent. Enfocados en decisiones de arquitectura.
- `github-copilot/<Agente>/` — agentes para GitHub Copilot en VS Code: Angular-Architect, Liferay-Architect, NestJS-Architect, SpringBoot-Architect. Enfocados en desarrollo. `github-copilot/guidelines/coding-guidelines.md` es plantilla de convenciones por proyecto (el agente la lee antes de actuar).

## Estructura de un agente copilot-365

- `AGENT_INSTRUCTIONS.md` — instrucciones del agente; **< 8000 caracteres** (límite Agent Builder).
- `skills/<skill>/SKILL.md` (+ `templates/`, `reference/`, `scripts/`) — **fuente editable**. Máximo 8 skills por agente.
- `skill-packages/*.zip` — generados desde `skills/`, con `SKILL.md` en la raíz. **No editar a mano.**
- `validation/validate.ps1`, `validation/test-prompts.md`, `VALIDATION.md`.

Flujo: editar `skills/` y regenerar ZIP + validar (desde la carpeta del agente):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File validation\validate.ps1 -Build   # regenera ZIP y valida
powershell -NoProfile -ExecutionPolicy Bypass -File validation\validate.ps1           # solo validar
```

`validate.ps1` comprueba frontmatter, términos requeridos por skill (`$required`), escenarios de enrutamiento (la `description` de la skill debe contener el disparador) y mojibake. Si cambias una skill o su `description`, actualiza los arrays `$required`/`$scenarios` del script. No existe script `build-vscode.ps1`; los README de copilot-365 explican la copia manual de `skills/` a `.github/skills/`.

## Estructura de un agente github-copilot

- `.github/agents/<Nombre>.agent.md` — agente.
- `.github/skills/<skill>/` — skills (formato Agent Skills); las descripciones llevan prefijo de lado (p. ej. "Frontend Angular.") para no confundirse con skills de NestJS cuando conviven.
- `validation/` — banco de pruebas Python; `VALIDATION.md` registra resultados por versión.

Tests (desde `validation/` del agente; requiere Node, paquete `typescript` — `TS_PATH` si no está en la ruta de módulos — y PyYAML; Liferay/SpringBoot usan `ParseJava.java`):

```bash
python3 run_tests.py <angular|nestjs> <ruta-del-agente>   # p. ej. python3 run_tests.py angular ..
```

Niveles: estructura, coherencia con restricciones críticas del agente, sintaxis de bloques de código (TS/YAML), hechos contrastados, escenarios de enrutamiento, ambigüedad, mutaciones. Cambios en agente o skills deben mantener `run_tests.py`/`scenarios.py` en verde y reflejarse en `VALIDATION.md`.

## Notas

- `README.md` raíz es solo un título. `.trees/` (worktrees) debe estar en `.gitignore`.
- Los cuatro agentes de cada plataforma comparten temática; cambios transversales (p. ej. normativa UE, reglas de monorepo) suelen requerir tocar varios agentes.
