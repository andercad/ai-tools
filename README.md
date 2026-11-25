# ai-tools

Colección de herramientas de IA (agentes y skills) para equipos de desarrollo. Contenido en español. Owner: `andercad`.

## Contenido

| Carpeta | Descripción |
| --- | --- |
| `claude-code/` | Config de Claude Code y marketplace de plugins (`ai-tools`): `angular`, `nestjs`, `spring-boot`, `liferay` |
| `copilot-365/` | Agentes de arquitectura para Microsoft 365 Copilot (Agent Builder) |
| `github-copilot/` | Agentes de desarrollo para GitHub Copilot en VS Code |

Plataformas cubiertas en cada carpeta: Angular, NestJS, Spring Boot y Liferay.

## Plugins de Claude Code

Instalar el marketplace:

```bash
claude plugin marketplace add ./claude-code
```

Cada plugin incluye agentes `*-dev` y `*-architect`, skills y hooks. Las reglas del proyecto llegan por su `CLAUDE.md` (skill `*-project-guidelines`). Funcionan con `/spec` y `/spec-impl` (se instalan aparte). El plugin `angular` depende de la skill oficial `angular-developer` (angular/angular).

Validar un plugin:

```bash
claude plugin validate claude-code/plugins/<plugin>
node claude-code/plugins/<plugin>/validation/check.mjs
```

## Agentes de Copilot

- `copilot-365/<Agente>/`: editar `skills/` y regenerar ZIP con `validation\validate.ps1 -Build`.
- `github-copilot/<Agente>/`: tests con `python3 run_tests.py <angular|nestjs> <ruta-del-agente>` desde `validation/`.

Más detalle en `CLAUDE.md`.
