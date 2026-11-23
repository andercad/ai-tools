# Monorepos con NestJS

Este documento cubre los dos tipos de monorepo con NestJS. Identifica primero cuál usa el repositorio y **no cambies de herramienta ni conviertas el workspace por iniciativa propia**.

| Señal en la raíz | Tipo de workspace |
|---|---|
| `nest-cli.json` sin `"monorepo": true` | Una sola aplicación: este documento no aplica |
| `nest-cli.json` con `"monorepo": true` y `projects`, carpetas `apps/` y `libs/` | **Modo monorepo del Nest CLI** |
| `nx.json` y un `project.json` (o configuración `nx` en `package.json`) por proyecto | Monorepo **Nx** |

## Principios comunes

- **Aplicaciones finas, librerías con el código compartido.** Cada aplicación (un API, un worker, un microservicio) compone módulos; lo que usan varias aplicaciones va a una librería. Lo que solo usa una aplicación vive en ella.
- **Importa solo por el punto de entrada público** de una librería (su alias o nombre de paquete). Nunca rutas relativas que salgan del proyecto (`../../libs/...`) ni imports profundos (`@acme/api/orders/src/lib/...`).
- **Una librería NestJS expone un módulo** (`OrdersModule`) y lo que otros necesitan de él, desde su `index.ts`. Los consumidores importan el módulo, no instancian sus providers (ver `nestjs-modules-services`).
- **Cada servicio es dueño de sus datos.** Una librería compartida no debe dar acceso a la base de datos de otro servicio; si dos aplicaciones necesitan los mismos datos, se comunican por API o mensajería (ver `nestjs-microservices`).
- **Comandos siempre con el proyecto** (o solo lo afectado). Nunca supongas que hay una única aplicación.
- **Reglas por proyecto**: el `CLAUDE.md` de la raíz aplica a todo el repositorio; si un proyecto tiene reglas propias (un `CLAUDE.md` en su carpeta o una sección dedicada), aplícalas en ese proyecto.

### Tipos de librería

| Tipo | Contiene | Puede depender de |
|---|---|---|
| `feature` | Un módulo de dominio completo (controladores, servicios, DTOs, entidades) | `feature` del mismo ámbito, `data-access`, `util` |
| `data-access` | Acceso a datos o a servicios externos de un dominio | `data-access`, `util` |
| `util` | Guards, interceptores, filtros, pipes, decoradores, utilidades | `util` |
| `contract` | Interfaces, tipos y eventos compartidos (con otros servicios o con el frontend) | `contract` |

Ajusta los nombres a los del `CLAUDE.md` del proyecto si son otros.

## Modo monorepo del Nest CLI

```powershell
nest new acme
cd acme
nest generate app billing        # convierte el proyecto a modo monorepo
nest generate library common     # librería compartida en libs/

nest start billing --watch
nest build billing
nest build acme                  # la aplicación original, ahora en apps/acme
```

- Añadir el primer proyecto convierte la estructura: la aplicación original pasa a `apps/<nombre>`, aparecen `apps/` y `libs/` y `nest-cli.json` registra los proyectos en `projects`, con `"monorepo": true`.
- Las librerías solo existen en este modo. `nest generate library` pide un prefijo para el alias y lo registra en los `paths` de `tsconfig.json`; impórtala siempre por ese alias.
- En este modo el CLI compila con webpack por defecto: comprueba `compilerOptions` en `nest-cli.json`. Las `compilerOptions` de un proyecto no se combinan con las de la raíz: si cambias la configuración de compilación de una aplicación, revisa la configuración completa de ese proyecto.
- **Tests**: los aliases de las librerías deben resolverse también en Jest (`moduleNameMapper`). Al generar una librería, comprueba que la configuración de Jest del proyecto los incluye.
- El Nest CLI **no** calcula lo afectado por un cambio, no cachea tareas ni impone límites entre proyectos:
  - En CI, construye y prueba cada aplicación de forma explícita.
  - Impón los límites con lint. Ejemplo con la regla estándar de ESLint:

```javascript
// eslint.config.mjs — billing no puede importar código de la aplicación acme
{
  files: ['apps/billing/**/*.ts'],
  rules: {
    'no-restricted-imports': [
      'error',
      {
        patterns: [
          { group: ['**/apps/acme/**'], message: 'Una aplicación no importa código de otra: usa una librería' },
          { group: ['@app/*/src/**'], message: 'Importa solo por el punto de entrada público' },
        ],
      },
    ],
  },
},
```

  Sustituye `@app` por el prefijo que uses en las librerías.
- Si el monorepo crece (muchas aplicaciones y librerías, CI lento, frontend en el mismo repositorio), plantea Nx como decisión explícita.

## Monorepo Nx

```
apps/
  api/                     ← aplicación NestJS (project.json, src/)
  billing-worker/
libs/
  api/
    orders/                ← librería feature: OrdersModule
    shared-auth/           ← librería util: guards, estrategias
  shared/
    api-contracts/         ← contratos compartidos (solo tipos)
nx.json
tsconfig.base.json         ← aliases, si el workspace los usa (ver Enlace entre proyectos)
```

### Generar proyectos

```powershell
nx add @nx/nest
nx g @nx/nest:app apps/api --tags=scope:api,type:app
nx g @nx/nest:lib libs/api/orders --tags=scope:api,type:feature
nx g @nx/nest:lib libs/api/shared-auth --tags=scope:api,type:util
```

- `@nx/nest` extiende los generadores del Nest CLI (controladores, servicios, módulos...); con Nx, indica siempre `--project` para que los genere en el proyecto correcto. Comprueba la sintaxis en la versión de Nx instalada y la versión de NestJS que soporta.
- **Etiquetas siempre** (`--tags`): sin ellas no hay límites.
- **Librerías de workspace por defecto**: sin `--buildable` ni `--publishable`, la librería se compila junto con la aplicación que la usa. Es la opción recomendada para código interno.
  - `--buildable`: solo para builds incrementales en monorepos grandes. Una librería compilable solo puede depender de otras compilables.
  - `--publishable --importPath=@acme/nest-audit`: para distribuirla fuera del monorepo como paquete npm.

### Enlace entre proyectos

Nx admite dos mecanismos; **comprueba cuál usa el workspace y no los mezcles**:

- **Aliases de TypeScript** en `tsconfig.base.json` (`compilerOptions.paths`): el modelo clásico, que el generador mantiene al crear librerías.
- **Workspaces del gestor de paquetes** (npm, pnpm, yarn, bun) con **referencias de proyecto de TypeScript**: cada proyecto tiene su `package.json`, las dependencias internas se declaran en él y `nx sync` mantiene las referencias.

### Límites entre librerías

```javascript
// eslint.config.mjs
import nx from '@nx/eslint-plugin';

export default [
  ...nx.configs['flat/base'],
  ...nx.configs['flat/typescript'],
  {
    files: ['**/*.ts'],
    rules: {
      '@nx/enforce-module-boundaries': [
        'error',
        {
          enforceBuildableLibDependency: true,
          allow: [],
          depConstraints: [
            { sourceTag: 'type:app', onlyDependOnLibsWithTags: ['type:feature', 'type:data-access', 'type:util', 'type:contract'] },
            { sourceTag: 'type:feature', onlyDependOnLibsWithTags: ['type:feature', 'type:data-access', 'type:util', 'type:contract'] },
            { sourceTag: 'type:data-access', onlyDependOnLibsWithTags: ['type:data-access', 'type:util', 'type:contract'] },
            { sourceTag: 'type:util', onlyDependOnLibsWithTags: ['type:util', 'type:contract'] },
            { sourceTag: 'type:contract', onlyDependOnLibsWithTags: ['type:contract'] },
            { sourceTag: 'scope:api', onlyDependOnLibsWithTags: ['scope:api', 'scope:shared'] },
            { sourceTag: 'scope:shared', onlyDependOnLibsWithTags: ['scope:shared'] },
          ],
        },
      ],
    },
  },
];
```

- Dos dimensiones de etiquetas: **ámbito** (`scope:*`) y **tipo** (`type:*`). Cada proyecto lleva una de cada.
- La regla también detecta imports profundos y dependencias circulares entre proyectos.
- Si una dependencia viola un límite, no la permitas con `allow` para salir del paso: mueve el código a la librería correcta o crea una nueva.

### Comandos

```powershell
nx serve api
nx build api
nx test api-orders                   # nombre del proyecto en su project.json
nx lint api-shared-auth
nx run-many -t lint test build       # todos los proyectos
nx affected -t lint test build       # solo lo afectado por los cambios
nx graph                             # grafo de proyectos y dependencias
```

- En un workspace Nx usa `nx`, no `nest`, para compilar, servir y probar.
- `nx affected` compara con la rama base (`defaultBase` en `nx.json`, o `--base`/`--head`).
- Las tareas se cachean: no desactives la caché sin motivo y declara bien `inputs`/`outputs` si añades tareas propias.
- Actualizaciones: `nx migrate latest` (o una versión concreta), instalar y `nx migrate --run-migrations`; actualiza una versión mayor cada vez y revisa `migrations.json` antes de confirmar.

## Configuración, persistencia y despliegue por aplicación

- **Configuración**: cada aplicación valida su propio esquema de variables de entorno y tiene su `.env.template` (ver `nestjs-workspace`). Lo común (por ejemplo, la validación de la conexión a la base de datos) puede vivir en una librería `util` de configuración que cada aplicación usa con sus valores. Una librería no lee `process.env`: recibe la configuración por su `forRoot`/`forRootAsync` o un token.
- **Persistencia**: cada aplicación tiene su `DataSource`/esquema de Prisma y **sus migraciones**, en su propia carpeta. No compartas tablas entre servicios a través de una librería (ver `nestjs-persistence`).
- **Docker**: un Dockerfile por aplicación, que copia solo la salida compilada de esa aplicación e instala solo sus dependencias de producción.
  - **Nx**: genera el `package.json` de la aplicación en el build (`generatePackageJson` del plugin o executor de webpack) en workspaces con aliases; en workspaces con referencias de proyecto de TypeScript, usa el flujo de poda (*prune*) de la documentación de Nx para tu versión.
  - **Nest CLI**: la salida queda en `dist/apps/<app>`; el `package.json` es el de la raíz, así que la imagen instala las dependencias de todo el monorepo salvo que generes una lista propia.
- **Puertos y nombres**: cada aplicación con su puerto y su nombre de servicio en logs, métricas y trazas, para distinguirlas en producción.

## Backend y frontend en el mismo monorepo Nx

Cuando el monorepo contiene también una aplicación Angular:

```javascript
// Ámbitos: el frontend nunca depende del backend
{ sourceTag: 'scope:web', onlyDependOnLibsWithTags: ['scope:web', 'scope:shared'] },
{ sourceTag: 'scope:api', onlyDependOnLibsWithTags: ['scope:api', 'scope:shared'] },
{ sourceTag: 'scope:shared', onlyDependOnLibsWithTags: ['scope:shared'] },
```

- **Las librerías del backend nunca se importan desde el frontend**: arrastrarían NestJS, `class-validator` u ORMs al bundle del navegador y expondrían código de servidor.
- **Contrato compartido** en una librería `scope:shared`, `type:contract` (por ejemplo `libs/shared/api-contracts`) con **solo** interfaces, tipos y enums: sin decoradores, sin clases con lógica y sin dependencias de runtime. Los DTO de NestJS siguen siendo clases del backend y **implementan** el contrato:

```typescript
// libs/shared/api-contracts/src/lib/orders.ts
export interface OrderDto {
  readonly id: string;
  readonly status: OrderStatus;
  readonly totalCents: number;
}

export type OrderStatus = 'pending' | 'paid' | 'shipped';
```

```typescript
// libs/api/orders/src/lib/dto/order-response.dto.ts
import type { OrderDto, OrderStatus } from '@acme/shared/api-contracts';

export class OrderResponseDto implements OrderDto {
  @ApiProperty()
  readonly id!: string;

  @ApiProperty({ enum: ['pending', 'paid', 'shipped'] })
  readonly status!: OrderStatus;

  @ApiProperty()
  readonly totalCents!: number;
}
```

- `implements` obliga al DTO a cumplir el contrato: si el contrato cambia, el backend deja de compilar hasta adaptarse. No detecta campos **extra** del DTO: revisa que el DTO no exponga más de lo que el contrato declara.
- Los DTO de **entrada** (con `class-validator`) también pueden implementar una interfaz del contrato; la validación sigue siendo del backend.
- Alternativa al contrato escrito a mano: publicar el OpenAPI de la API y generar el cliente del frontend. Elige una de las dos según el `CLAUDE.md` del proyecto, no ambas.
- Un cambio incompatible en el contrato rompe backend y frontend a la vez: `nx affected` detecta los dos, pero si se despliegan por separado, versiona la API y mantén la compatibilidad durante la transición.
- **Proxy de desarrollo**: `nx g @nx/nest:app ... --frontendProject=web` configura el proxy de la aplicación web hacia la API.
- **Contratos entre microservicios**: los eventos y mensajes compartidos entre servicios del monorepo siguen la misma regla: librería `type:contract` versionada (ver `nestjs-microservices`).
- **Qué agente usar**: `nestjs-dev` para `apps/api` y `libs/api`; el agente de frontend para la web. Para reglas distintas por carpeta, coloca un `CLAUDE.md` en `apps/api/` y `libs/api/` (Claude Code lo carga al trabajar en esa ruta); los contratos compartidos con el frontend van en `libs/shared/api-contracts` y solo contienen tipos.

## CI

```yaml
# GitHub Actions — solo lo afectado por el PR (Nx)
- uses: actions/checkout@v4
  with:
    fetch-depth: 0          # nx affected necesita el historial para comparar con la base
- run: npm ci
- run: npx nx affected -t lint test build --base=origin/main --head=HEAD
```

- Con el Nest CLI, construye y prueba cada aplicación de forma explícita (no hay `affected`).
- Construye las imágenes Docker solo de las aplicaciones afectadas.

## Checklist

- [ ] Tipo de workspace identificado (Nest CLI o Nx) y respetado
- [ ] Código compartido en librerías con tipo y ámbito; cada librería expone su módulo
- [ ] Imports entre proyectos solo por el punto de entrada público; sin rutas relativas entre proyectos ni imports profundos
- [ ] Etiquetas en todos los proyectos y límites aplicados en lint (Nx) o reglas equivalentes (Nest CLI)
- [ ] Sin dependencias circulares entre proyectos
- [ ] Mecanismo de enlace del workspace respetado (aliases o workspaces)
- [ ] Comandos por proyecto o `nx affected`, nunca suponiendo una sola aplicación
- [ ] Configuración, migraciones y Docker por aplicación; ninguna librería da acceso a los datos de otro servicio
- [ ] El frontend no importa nada con ámbito de backend; contratos solo con tipos y DTO que los implementan
