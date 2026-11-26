# Plugin Spring Boot para Claude Code

Flujo spec → implementación → verificación para Spring Boot 3.x/4.x con Java (Maven o Gradle, módulo único o multimódulo), con la política de calidad definida por proyecto en su `CLAUDE.md`.

## Qué incluye
- **`spring-boot-dev`**: diseña con SOLID antes de escribir, genera código seguro y documentado, crea tests (unitarios y de integración) si la política lo pide y verifica (`verify`) antes de informar.
- **`spring-boot-architect`** (solo lectura): evalúa, compara alternativas, redacta ADR, matrices de decisión y riesgos, planifica upgrades.
- **Skills de desarrollo**: `spring-solid` (precargada en `spring-boot-dev`), `spring-structure-services`, `spring-api`, `spring-persistence`, `spring-security`, `spring-testing-quality`, `spring-config-observability`, `spring-integration`, `spring-graphql`, `spring-project-guidelines`, `spring-review`.
- **Skills de arquitectura**: `spring-architecture-assessment`, `spring-modularity-domain`, `spring-api-integration`, `spring-data-transactions`, `spring-security-identity`, `spring-cloud-runtime`, `spring-observability-resilience`, `spring-modernization-governance`.
- **Hooks**: `PostToolUse` (Spotless sobre el `.java` editado, solo si el proyecto lo tiene configurado) y `Stop`/`SubagentStop` (bloquea el cierre si `tests: required` y hay controladores, servicios, componentes, listeners o advices sin `XTest.java`/`XIT.java`).
- **`/spring-boot:spring-review`**: revisión de solo lectura del diff.

## Sin dependencias externas
No hay skill oficial de Spring Boot que reutilizar: las skills de desarrollo son propias (derivadas de `github-copilot/SpringBoot-Architect`, agrupadas con el detalle en `references/`). Para APIs que dependen de versión, los agentes consultan docs.spring.io.

## Política del proyecto (bloque en el `CLAUDE.md`)
```markdown
## Convenciones Spring Boot
- tests: required | optional | none
- it: required | optional | none
- coverage: 80
- docs: javadoc | none
- api-docs: springdoc | none
- build: maven | gradle
- workspace: single | multi-module
- verify: ./mvnw verify
```
Pide a Claude que use la skill `spring-project-guidelines`: escribe el bloque y, debajo, las reglas de implementación y de specs, que aplican en cualquier flujo (incluidos `/spec` y `/spec-impl`). Defaults si faltan claves: `tests: none`, `it: none`, `docs: javadoc`, `api-docs: springdoc` si `springdoc-openapi` está en las dependencias. `verify` por defecto: `./mvnw verify` (Maven) o `./gradlew build` (Gradle).

## Instalación
```bash
claude plugin marketplace add ./claude-code      # desde la raíz de este repo
claude plugin install spring-boot@ai-tools
```
Prueba sin instalar: `claude --plugin-dir claude-code/plugins/spring-boot`.

### Actualización

```bash
claude plugin marketplace update ai-tools
claude plugin update spring-boot@ai-tools
```

Reinicia Claude Code para aplicar.

## Mantenimiento (desarrolladores)

Tras editar el plugin, sube `version` en `.claude-plugin/plugin.json`: sin cambio de versión, Claude Code usa la caché y los consumidores no reciben la novedad. Después valida, haz commit/push y avisa al equipo para que ejecute la actualización.

```bash
claude plugin validate claude-code/plugins/spring-boot
node claude-code/plugins/spring-boot/validation/check.mjs
```
`check.mjs` es estático (frontmatter, enlaces, skills citadas, restos de Copilot). Para comportamiento, usa `validation/test-prompts.md`.

## Origen del contenido
Las skills de desarrollo derivan de `github-copilot/SpringBoot-Architect` y las de arquitectura de `copilot-365/Spring-Boot-Architecture-Agent`; los cambios no se sincronizan solos.
