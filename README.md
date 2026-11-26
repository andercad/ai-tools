# ai-tools

Colección de herramientas de IA (agentes y skills) para equipos de desarrollo. Contenido en español. Owner: `andercad`.

Plataformas cubiertas en cada bloque: Angular, NestJS, Spring Boot y Liferay.

| Bloque | Carpeta | Para qué |
| --- | --- | --- |
| [Claude Code](#claude-code) | `claude-code/` | Marketplace de plugins (`ai-tools`) y config: desarrollo y arquitectura |
| [GitHub Copilot](#github-copilot) | `github-copilot/` | Agentes de desarrollo para VS Code |
| [Microsoft 365 Copilot](#microsoft-365-copilot) | `copilot-365/` | Agentes de arquitectura (Agent Builder) |

Cada bloque tiene dos partes: uso (instalación y actualización, para quien consume las herramientas) y mantenimiento (para quien las desarrolla en este repo).

## Claude Code

Marketplace `ai-tools` con los plugins `angular`, `nestjs`, `spring-boot` y `liferay`. Cada plugin incluye agentes `*-dev` y `*-architect`, skills y hooks. Las reglas del proyecto llegan por su `CLAUDE.md` (skill `*-project-guidelines`). Funcionan con `/spec` y `/spec-impl` (se instalan aparte). El plugin `angular` depende de la skill oficial `angular-developer` (angular/angular).

### Instalación

```bash
claude plugin marketplace add ./claude-code
claude plugin install <plugin>@ai-tools
```

### Actualización

```bash
claude plugin marketplace update ai-tools
claude plugin update <plugin>@ai-tools
```

Reiniciar Claude Code para aplicar.

### Mantenimiento (desarrolladores)

1. Editar el plugin en `claude-code/plugins/<plugin>/`.
2. Subir `version` en `.claude-plugin/plugin.json`. Sin cambio de versión, Claude Code usa la caché y los consumidores no reciben la novedad.
3. Validar:

```bash
claude plugin validate claude-code/plugins/<plugin>
node claude-code/plugins/<plugin>/validation/check.mjs
```

4. Commit y push. Avisar al equipo para que ejecute la actualización.

## GitHub Copilot

Agentes de desarrollo para GitHub Copilot en VS Code (`github-copilot/<Agente>/`): Angular-Architect, Liferay-Architect, NestJS-Architect y SpringBoot-Architect.

### Instalación

Copiar en la raíz del repo del proyecto (detalle en el README de cada agente):

```
.github/agents/<Agente>.agent.md
.github/skills/                    ← carpetas de skills
guidelines/coding-guidelines.md    ← plantilla: adaptar al proyecto
```

`validation/` no hace falta en el proyecto.

### Actualización

Volver a copiar `.github/agents/` y `.github/skills/` desde este repo (sobrescribir) sin pisar `guidelines/coding-guidelines.md` ya adaptado.

### Mantenimiento (desarrolladores)

Editar el agente o sus skills y mantener los tests en verde (desde `validation/` del agente):

```bash
python3 run_tests.py <angular|nestjs> <ruta-del-agente>
```

Reflejar el resultado en `VALIDATION.md`.

## Microsoft 365 Copilot

Agentes de arquitectura para Agent Builder (`copilot-365/<Agente>/`): Angular-Enterprise-Architect, Liferay-Enterprise-Architect, NestJS-Architecture-Agent y Spring-Boot-Architecture-Agent.

### Instalación

Requisito: skills de Agent Builder en preview, solo organizaciones del programa Microsoft Frontier.

1. Crear el agente en Agent Builder y pegar `AGENT_INSTRUCTIONS.md` en sus instrucciones.
2. **Configure > Skills > Add**: subir los ZIP de `skill-packages/`.
3. Conocimiento: sitios de SharePoint y webs oficiales (no se combinan con archivos embebidos en preview).
4. Probar con `validation/test-prompts.md`.

### Actualización

Pegar de nuevo `AGENT_INSTRUCTIONS.md` si cambió y volver a subir los ZIP modificados de `skill-packages/` (reemplazar los anteriores).

### Mantenimiento (desarrolladores)

Editar `skills/` (fuente; los ZIP no se editan a mano) y, desde la carpeta del agente, regenerar ZIP y validar:

```powershell
validation\validate.ps1 -Build   # regenera ZIP y valida
validation\validate.ps1          # solo validar
```

Más detalle en `CLAUDE.md`.
