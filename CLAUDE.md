# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Qué es este repo

Colección de herramientas de IA (no hay app ni build global): contenido en Markdown/PowerShell/Python que define agentes y skills. Idioma del contenido: español. Tres áreas independientes:

- `claude-code/.claude/` — config de Claude Code: hook `PostToolUse` (`hooks/format-lint.mjs`, corre prettier + eslint con `npx` sobre el fichero editado; ignora `.claude/`, `node_modules/`, etc.), comando `/worktree` (worktree en `.trees/[nombre]` + subagente) y skill `telegram-send` (`send.mjs`, lee `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` de `settings.local.json`; no commitear secretos).
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

`validate.ps1` comprueba frontmatter, términos requeridos por skill (`$required`), escenarios de enrutamiento (la `description` de la skill debe contener el disparador) y mojibake. Si cambias una skill o su `description`, actualiza los arrays `$required`/`$scenarios` del script. El README del agente Angular menciona un `build-vscode.ps1` (genera `vscode-agents.zip` para VS Code) que no existe en este repo.

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
