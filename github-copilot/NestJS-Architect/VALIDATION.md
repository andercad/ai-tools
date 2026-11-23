# Validación del agente NestJS Architect — v5 (monorepos)

## Cambios de esta versión

1. **Nueva skill `nestjs-monorepo`**, que cubre:
   - **Modo monorepo del Nest CLI**: `nest generate app` y `nest generate library`, `nest-cli.json` con `"monorepo": true`, compilación con webpack, aliases en Jest y límites con `no-restricted-imports`.
   - **Monorepo Nx**: generadores de `@nx/nest` con `--project`, librerías de workspace, compilables o publicables, los dos modelos de enlace, etiquetas y `@nx/enforce-module-boundaries`, `nx affected` y `nx migrate`.
   - **Por aplicación**: configuración, migraciones y Docker (`generatePackageJson` o el flujo de poda, según el modelo de enlace).
   - **Backend y frontend en el mismo Nx**: el contrato solo contiene tipos y los DTO lo implementan; proxy de desarrollo e instrucciones por ruta.
   - Contratos entre microservicios y CI.
2. **Agente**: detecta el tipo de workspace, cambia las reglas de estructura en un monorepo, valida por proyecto o con lo afectado, y añade una restricción crítica de límites del monorepo.
3. **Skills ajustadas**:
   - `nestjs-config`: esquema y `.env` por aplicación, y `envFilePath`.
   - `nestjs-persistence`: cada servicio es dueño de sus datos y tiene sus propias migraciones.
   - `nestjs-testing` y `nestjs-quality`: comandos por proyecto o afectados, y `moduleNameMapper` de Jest.
   - `nestjs-modules`: cada librería expone su módulo.
   - `nestjs-dto-validation`: los DTO no se comparten con el frontend.
   - `nestjs-microservices`: contratos en una librería `type:contract`.
   - Referencias puntuales en el resto.
4. **Todas las descripciones empiezan por "Backend NestJS (API)."**, para que Copilot no confunda estas skills con las del agente de Angular cuando conviven en el mismo repositorio.

## Pruebas

| Nivel | v4 | v5 |
|---|---|---|
| 1. Estructura (incluido el prefijo de lado) | 78/78 | 115/115 |
| 2. Coherencia (incluidas las reglas de monorepo: imports profundos, rutas relativas entre proyectos, contratos sin dependencias de servidor) | OK | OK |
| 3. Sintaxis (TypeScript y YAML) | 84 TS | 90 TS + 2 YAML |
| 4. Hechos | 3/3 | 6/6 |
| 5. Escenarios | 20/20 | 25/25 |
| 6. Ambigüedad con las skills de Angular (prueba conjunta) | — | 12/12 skill y 12/12 lado |
| 7. Mutaciones detectadas | 7/7 | 4/4 en NestJS |

Para repetir las pruebas:

```
python3 validation/run_tests.py nestjs .
python3 validation/scenarios.py nestjs .
python3 validation/scenarios.py combined <ruta-angular> <ruta-nestjs>
```

Requiere Node, el paquete `typescript` (variable `TS_PATH` si no está en la ruta de módulos) y PyYAML.

## Defectos encontrados en esta iteración

| # | Defecto | Origen | Corrección |
|---|---|---|---|
| 1 | No había instrucciones para monorepos | Hueco de diseño | Skill nueva y skills ajustadas |
| 2 | En la prueba conjunta, "endpoint REST de la API NestJS", "tests del servicio de la API" y "lo afectado de la API" se iban al lado de Angular | Descripciones sin señal de lado; **promesa mía sin cumplir** | Prefijo de lado, y descripciones de `nestjs-controllers` y `nestjs-testing` ampliadas |
| 3 | Al añadir la skill de monorepo, "migración de una columna" y "N+1" dejaron de encontrar `nestjs-persistence` | Regresión de esta iteración | Descripción ampliada |
| 4 | El banco marcaba `nestjs-pino` y `nestjs-cls` como referencias rotas: son paquetes npm, no skills | **Falso positivo del banco** | Excluidos |

## Afirmaciones contrastadas con la documentación

- Modo monorepo del Nest CLI:
  - Añadir un proyecto convierte la estructura.
  - Las librerías solo existen en este modo.
  - Las `compilerOptions` de un proyecto no se combinan con las de la raíz.
- `@nx/nest`:
  - Generadores `app` y `lib`, con `--buildable`, `--publishable --importPath` y `--frontendProject`.
  - Los generadores de Nest requieren `--project`.
  - Versiones de NestJS soportadas por cada versión de Nx.
- Despliegue en Nx: `generatePackageJson` en workspaces sin referencias de proyecto, y flujo de poda en los que las usan (el modelo por defecto en Nx 20+, según la documentación).
- Etiquetas y `@nx/enforce-module-boundaries`.

**Sin verificar**:
- Que el Nest CLI compile siempre con webpack en modo monorepo. La fuente es de 2020; la skill dice que se compruebe en `nest-cli.json`.
- Que `nest generate library` actualice siempre el `moduleNameMapper` de Jest. La skill dice que se compruebe.

## Limitaciones

- **No se ha ejecutado nada contra NestJS ni Nx reales**: el registro de npm no está accesible en el entorno de prueba.
- **La selección de skills es una simulación**. En el repositorio real, lo más fiable son las instrucciones por ruta (`applyTo`) y elegir el agente adecuado en el chat.
- **La ruta de `envFilePath`** depende del directorio de trabajo con el que se arranca la aplicación. La skill lo advierte, pero no lo he probado con `nest start` ni con `nx serve`.

## Autoevaluación

| Dimensión | Nota | Comentario |
|---|---|---|
| Estructura y routing | 10/10 | Sin fallos en el agente |
| Coherencia | 9/10 | Las reglas nuevas se cumplen |
| Exactitud técnica | 8/10 | Dos detalles del Nest CLI quedan marcados como no verificados |
| Cobertura | 9/10 | Nest CLI, Nx, despliegue por aplicación y caso fullstack |
| Proceso | 7/10 | La desambiguación prometida no estaba aplicada; el banco tenía un falso positivo |
