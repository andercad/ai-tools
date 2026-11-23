# Validación del agente Angular Architect — v5 (monorepos)

## Cambios de esta versión

1. **Nueva skill `angular-monorepo`**, que cubre:
   - **Workspace multiproyecto de Angular CLI**: `ng new --no-create-application`, aplicaciones y librerías en `projects/`, comandos por proyecto y límites con `no-restricted-imports`.
   - **Monorepo Nx**: generadores de `@nx/angular`, librerías de workspace, compilables o publicables, los dos modelos de enlace (aliases o workspaces con referencias de proyecto), etiquetas y `@nx/enforce-module-boundaries`, `nx affected`, caché y `nx migrate`.
   - **Frontend y backend en el mismo Nx**: ámbitos, contrato compartido solo con tipos, proxy de desarrollo e instrucciones por ruta (`applyTo`).
   - Configuración por aplicación y CI.
2. **Agente**: detecta el tipo de workspace, cambia las reglas de estructura en un monorepo (librerías, aliases por librería, imports solo por el punto de entrada público), valida por proyecto o con lo afectado, y añade una restricción crítica de límites del monorepo.
3. **Skills ajustadas** porque daban por hecho una sola aplicación:
   - `angular-quality` y `angular-testing`: comandos por proyecto o afectados.
   - `angular-environment`: configuración por aplicación y `nx migrate` en Nx.
   - `angular-library`: librerías dentro del monorepo.
   - `angular-i18n`: traducciones por aplicación y por librería.
   - `angular-routing`: rutas exportadas por librerías `feature`.
   - Referencias puntuales en `angular-components`, `angular-http`, `angular-performance`, `angular-security`, `angular-solid`, `angular-ssr` y `angular-styling`.
4. **Todas las descripciones empiezan por "Frontend Angular."**, para que Copilot no confunda estas skills con las del agente de NestJS cuando conviven en el mismo repositorio.

## Pruebas

| Nivel | Qué comprueba | v4 | v5 |
|---|---|---|---|
| 1. Estructura | Frontmatter, routing, referencias cruzadas, descripción con prefijo de lado | 99/99 | 122/122 |
| 2. Coherencia | Restricciones críticas, orden de miembros y `OnPush`, más las reglas nuevas de monorepo: sin imports profundos, sin rutas relativas entre proyectos, el frontend no importa el backend, contratos sin decoradores ni dependencias de servidor | OK | OK |
| 3. Sintaxis | Bloques TypeScript (compilador de TS 5.8) y YAML (PyYAML) | 90 TS | 96 TS + 1 YAML |
| 4. Hechos | Afirmaciones contrastadas con la documentación de Nx y Angular, requeridas o prohibidas | — | 8/8 |
| 5. Escenarios | Peticiones realistas → skill esperada en el top 3 | 20/20 | 23/23 |
| 6. Ambigüedad | Skills de Angular y NestJS juntas: skill correcta y lado correcto | — | 12/12 y 12/12 |
| 7. Mutaciones | Defectos introducidos para comprobar que los tests los detectan | 5/5 | 5/5 en Angular (10/10 entre los dos agentes, tras la corrección del banco) |

Para repetir las pruebas:

```
python3 validation/run_tests.py angular .
python3 validation/scenarios.py angular .
python3 validation/scenarios.py combined <ruta-angular> <ruta-nestjs>
```

Requiere Node, el paquete `typescript` (indica la ruta con `TS_PATH` si no está en la ruta de módulos) y PyYAML.

## Defectos encontrados en esta iteración

| # | Defecto | Origen | Corrección |
|---|---|---|---|
| 1 | No había instrucciones para monorepos: varias skills daban comandos y rutas que suponen una sola aplicación | Hueco de diseño | Skill nueva y skills ajustadas |
| 2 | Con las skills de NestJS en el mismo repositorio, 3 de 12 peticiones se iban al lado equivocado. Además, no había aplicado lo que anuncié: que cada descripción dijera "frontend" o "backend" | **Promesa mía sin cumplir** | Prefijo "Frontend Angular." en las 17 descripciones |
| 3 | Al añadir la skill de monorepo, la petición "notificación global cuando falle cualquier petición HTTP" dejó de encontrar `angular-http` | Regresión de esta iteración | Descripción ampliada |
| 4 | `angular-monorepo` remitía a `angular-http` para versionar contratos, pero esa skill no lo trata | Error mío | Referencia eliminada |
| 5 | El banco solo comprobaba que el hecho "`nx migrate` en Nx" apareciera en algún sitio; no detectaba que alguien añadiera `ng update` como comando en un monorepo Nx | **Debilidad del banco**, encontrada con las mutaciones | Comprobación de contradicción añadida |

## Afirmaciones de esta versión contrastadas con la documentación

- `ng new --no-create-application` y proyectos en `projects/` (`newProjectRoot`).
- Etiquetas en `project.json` y `@nx/enforce-module-boundaries` con `depConstraints` y la configuración plana `flat/base` y `flat/typescript`.
- Librerías de workspace compiladas con la aplicación. `--buildable` solo puede depender de otras compilables, y `--publishable` requiere `--import-path`.
- Generador de aplicación de `@nx/angular` con `--prefix`, `--tags` y `--backendProject`.
- Dos modelos de enlace en Nx: aliases en `tsconfig.base.json`, o workspaces del gestor de paquetes con referencias de proyecto y `nx sync`.
- `nx migrate` más `--run-migrations`, una versión mayor cada vez, obligatorio con Angular.
- `npx nx@latest init` para migrar un workspace de Angular CLI.

**Sin verificar**:
- El soporte de Angular en el modelo de workspaces de Nx: la skill remite a la documentación de la versión instalada.
- La sintaxis exacta de `applyTo` con varios patrones: la skill indica que se compruebe.

## Limitaciones

- **No se ha ejecutado nada contra Angular ni Nx reales**: el registro de npm no está accesible en el entorno de prueba. La siguiente validación debería crear un workspace con `create-nx-workspace` (Angular más NestJS) y otro con `ng new --no-create-application`, y probar generadores, límites, `nx affected` y builds.
- **La selección de skills sigue siendo una simulación** por palabras. Prefijar las descripciones ayuda, pero en el repositorio real lo más fiable son las instrucciones por ruta (`applyTo`) y elegir el agente adecuado en el chat.
- **No se ha comprobado el límite práctico** de skills cargadas con 32 en el mismo repositorio (17 de Angular y 15 de NestJS).

## Autoevaluación

| Dimensión | Nota | Comentario |
|---|---|---|
| Estructura y routing | 10/10 | Sin fallos |
| Coherencia con sus reglas | 9/10 | Las reglas nuevas de monorepo se cumplen en todos los ejemplos |
| Exactitud técnica | 8/10 | Los hechos de Nx están contrastados; dos detalles quedan marcados como no verificados |
| Cobertura | 9/10 | Los dos tipos de monorepo y el caso fullstack cubiertos |
| Proceso | 7/10 | Había anunciado un cambio en las descripciones y no lo apliqué hasta que la prueba de ambigüedad lo detectó; el banco tenía una debilidad que solo descubrí con las mutaciones |
