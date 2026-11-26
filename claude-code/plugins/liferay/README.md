# Plugin Liferay para Claude Code

Flujo spec → implementación → verificación para Liferay DXP 2025.Q1 o posterior con Liferay Workspace (Gradle), con la política de calidad definida por proyecto en su `CLAUDE.md`.

## Qué incluye
- **`liferay-dev`**: detecta versión y modelo de despliegue, elige el mecanismo de extensión (configuración → Objects/contenido → client extensions → OSGi → overrides), genera código seguro y documentado, crea tests si la política lo pide y verifica (`verify`, logs) antes de informar.
- **`liferay-architect`** (solo lectura): evalúa instalaciones, elige mecanismo, compara alternativas, redacta ADR, matrices de decisión y riesgos, planifica upgrades.
- **Skills de desarrollo**: `liferay-extension-model` (precargada en `liferay-dev`), `liferay-workspace`, `liferay-osgi` (incluye Service Builder), `liferay-objects-workflow`, `liferay-client-extensions`, `liferay-headless`, `liferay-content-experience` (contenido, fragments, sites, personalización, Analytics), `liferay-commerce`, `liferay-search`, `liferay-security`, `liferay-testing-quality`, `liferay-config-operations` (configuración, despliegue, PaaS/SaaS, diagnóstico), `liferay-project-guidelines`, `liferay-review`.
- **Skills de arquitectura**: `liferay-architecture-assessment`, `liferay-solution-architecture`, `liferay-platform-customization`, `liferay-client-extensions-integration`, `liferay-content-search`, `liferay-security-identity`, `liferay-cloud-operations`, `liferay-version-upgrade`.
- **Hooks**: `PostToolUse` (Source Formatter, solo con `format: source-formatter`) y `Stop`/`SubagentStop` (bloquea el cierre si `tests: required` y hay componentes `@Component` con lógica sin `XTest.java`/`XIT.java`).
- **`/liferay:liferay-review`**: revisión de solo lectura del diff.

## Sin dependencias externas
No hay skill oficial de Liferay que reutilizar: las skills de desarrollo son propias (derivadas de `github-copilot/Liferay-Architect`, agrupadas con el detalle en `references/`). Para APIs que dependen de versión, los agentes consultan learn.liferay.com y el código de `liferay-portal` de la etiqueta de la versión del proyecto.

Si instalas los plugins de Angular o Spring Boot, `liferay-dev` les remite el frontend de los custom elements y los microservicios.

## Política del proyecto (bloque en el `CLAUDE.md`)
```markdown
## Convenciones Liferay
- tests: required | optional | none
- it: required | optional | none
- docs: javadoc | none
- deployment: saas | paas | self-hosted-docker | self-hosted-k8s | self-hosted-bundle
- product: dxp-2025.q1.0
- base-package: com.acme.portal
- format: source-formatter | none
- verify: ./gradlew build
```
Pide a Claude que use la skill `liferay-project-guidelines`: escribe el bloque y, debajo, las reglas de implementación y de specs, que aplican en cualquier flujo (incluidos `/spec` y `/spec-impl`). Defaults si faltan claves: `tests: none`, `it: none`, `docs: javadoc`, `format: none`, `verify: ./gradlew build`.

`format: source-formatter` ejecuta `gradlew :modules:<modulo>:formatSource` tras editar `.java`, `.jsp`, `.ftl`, `.scss`, `.css` o `.js` bajo `modules/` o `themes/`. Formatea el módulo entero y puede tardar; sin esa clave el hook no hace nada.

## Instalación
```bash
claude plugin marketplace add ./claude-code      # desde la raíz de este repo
claude plugin install liferay@ai-tools
```
Prueba sin instalar: `claude --plugin-dir claude-code/plugins/liferay`.

### Actualización

```bash
claude plugin marketplace update ai-tools
claude plugin update liferay@ai-tools
```

Reinicia Claude Code para aplicar.

## Mantenimiento (desarrolladores)

Tras editar el plugin, sube `version` en `.claude-plugin/plugin.json`: sin cambio de versión, Claude Code usa la caché y los consumidores no reciben la novedad. Después valida, haz commit/push y avisa al equipo para que ejecute la actualización.

```bash
claude plugin validate claude-code/plugins/liferay
node claude-code/plugins/liferay/validation/check.mjs
```
`check.mjs` es estático (frontmatter, enlaces, skills citadas, restos de Copilot). Para comportamiento, usa `validation/test-prompts.md`.

## Origen del contenido
Las skills de desarrollo derivan de `github-copilot/Liferay-Architect` y las de arquitectura de `copilot-365/Liferay-Enterprise-Architect`; los cambios no se sincronizan solos.
