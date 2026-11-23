
# Monorepos con Angular

Esta skill cubre los dos tipos de monorepo con Angular. Identifica primero cuál usa el repositorio y **no cambies de herramienta ni conviertas el workspace por iniciativa propia**.

| Señal en la raíz | Tipo de workspace |
|---|---|
| `angular.json` con una aplicación en `src/` | Una sola aplicación: esta skill no aplica |
| `angular.json` con varios proyectos (habitualmente en `projects/`) | Workspace multiproyecto de **Angular CLI** |
| `nx.json` y un `project.json` (o configuración `nx` en `package.json`) por proyecto | Monorepo **Nx** |

Migrar de Angular CLI a Nx (`npx nx@latest init`) es una decisión de arquitectura: solo si se pide.

## Principios comunes

- **Aplicaciones finas, librerías con el código.** Una aplicación compone rutas, configuración y funcionalidades que viven en librerías. Lo que solo usa una aplicación puede vivir en ella; lo que se comparte va a una librería.
- **Importa solo por el punto de entrada público** de una librería (su alias o nombre de paquete). Nunca rutas relativas que salgan del proyecto (`../../libs/...`) ni imports profundos (`@acme/shared/ui/src/lib/...`): saltan la API pública y rompen los límites.
- **Cada librería tiene un tipo y un ámbito**, y las dependencias van en una sola dirección (sin ciclos).
- **Comandos siempre con el proyecto** (o solo lo afectado). Nunca supongas que hay una única aplicación.
- **Reglas por proyecto**: las guidelines de la raíz aplican a todo el repositorio; si un proyecto tiene reglas propias (sección de las guidelines o `.github/instructions/*.instructions.md` con `applyTo`), aplícalas en ese proyecto.

### Tipos de librería

| Tipo | Contiene | Puede depender de |
|---|---|---|
| `feature` | Páginas y componentes con lógica de una funcionalidad, sus rutas | `feature`, `ui`, `data-access`, `util` |
| `ui` | Componentes de presentación sin dependencias de datos | `ui`, `util` |
| `data-access` | Servicios HTTP, estado, modelos de la funcionalidad | `data-access`, `util` |
| `util` | Funciones puras, validadores, pipes genéricos | `util` |

Ajusta los nombres a los de las guidelines si son otros. Una librería `feature` suele exportar sus rutas para cargarlas con `loadChildren` desde la aplicación (ver la skill `angular-developer` (oficial)).

## Workspace multiproyecto de Angular CLI

```powershell
ng new acme --no-create-application
cd acme
ng generate application portal
ng generate application admin
ng generate library @acme/ui --prefix=acme

ng serve portal
ng build portal
ng test @acme/ui
ng lint admin
```

- Los proyectos se crean en `projects/` (propiedad `newProjectRoot` de `angular.json`).
- Las librerías se consumen por el alias que `ng generate library` añade a `tsconfig.json`, que apunta a la salida compilada en `dist/`: compila la librería antes que la aplicación, o en modo `--watch` durante el desarrollo (ver `library.md`).
- Angular CLI **no** calcula lo afectado por un cambio, no cachea tareas ni impone límites entre proyectos:
  - En CI, construye y prueba cada proyecto de forma explícita.
  - Impón los límites con lint. Ejemplo con la regla estándar de ESLint:

```javascript
// eslint.config.js — portal no puede importar código de admin
{
  files: ['projects/portal/**/*.ts'],
  rules: {
    'no-restricted-imports': [
      'error',
      {
        patterns: [
          { group: ['**/projects/admin/**'], message: 'portal no puede depender de admin' },
          { group: ['@acme/*/src/**'], message: 'Importa solo por el punto de entrada público' },
        ],
      },
    ],
  },
},
```

- Si el monorepo crece (muchas librerías, CI lento, equipos distintos), plantea Nx como decisión explícita.

## Monorepo Nx

```
apps/
  portal/                  ← aplicación Angular (project.json, src/)
  portal-e2e/
libs/
  portal/
    feature-orders/
    data-access-orders/
    ui/
  shared/
    ui/
    util-formatting/
nx.json
tsconfig.base.json         ← aliases, si el workspace los usa (ver Enlace entre proyectos)
```

### Generar proyectos

```powershell
nx g @nx/angular:application apps/portal --prefix=portal --tags=scope:portal,type:app
nx g @nx/angular:library libs/portal/feature-orders --tags=scope:portal,type:feature
nx g @nx/angular:library libs/portal/data-access-orders --tags=scope:portal,type:data-access
nx g @nx/angular:library libs/shared/ui --prefix=acme --tags=scope:shared,type:ui
```

- Usa los generadores de `@nx/angular` para aplicaciones, librerías, componentes y servicios: configuran `project.json`, tests y lint. Comprueba la sintaxis de rutas y opciones en la versión de Nx instalada.
- **Etiquetas siempre** (`--tags`): sin ellas no hay límites.
- **Librerías de workspace por defecto**: sin `--buildable` ni `--publishable`, la librería se compila junto con la aplicación que la usa, desde el código fuente. Es la opción recomendada para código interno.
  - `--buildable`: solo para builds incrementales en monorepos grandes. Una librería compilable solo puede depender de otras compilables.
  - `--publishable --import-path=@acme/ui`: para distribuirla fuera del monorepo (ver `library.md`).

### Enlace entre proyectos

Nx admite dos mecanismos; **comprueba cuál usa el workspace y no los mezcles**:

- **Aliases de TypeScript** en `tsconfig.base.json` (`compilerOptions.paths`): el modelo clásico, que el generador mantiene al crear librerías.
- **Workspaces del gestor de paquetes** (npm, pnpm, yarn, bun) con **referencias de proyecto de TypeScript**: cada proyecto tiene su `package.json`, las dependencias internas se declaran en él y `nx sync` mantiene las referencias. Comprueba en la documentación de Nx el soporte de Angular para este modelo en tu versión.

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
            { sourceTag: 'type:app', onlyDependOnLibsWithTags: ['type:feature', 'type:ui', 'type:data-access', 'type:util'] },
            { sourceTag: 'type:feature', onlyDependOnLibsWithTags: ['type:feature', 'type:ui', 'type:data-access', 'type:util'] },
            { sourceTag: 'type:ui', onlyDependOnLibsWithTags: ['type:ui', 'type:util'] },
            { sourceTag: 'type:data-access', onlyDependOnLibsWithTags: ['type:data-access', 'type:util'] },
            { sourceTag: 'type:util', onlyDependOnLibsWithTags: ['type:util'] },
            { sourceTag: 'scope:portal', onlyDependOnLibsWithTags: ['scope:portal', 'scope:shared'] },
            { sourceTag: 'scope:admin', onlyDependOnLibsWithTags: ['scope:admin', 'scope:shared'] },
            { sourceTag: 'scope:shared', onlyDependOnLibsWithTags: ['scope:shared'] },
          ],
        },
      ],
    },
  },
];
```

- Dos dimensiones de etiquetas: **ámbito** (`scope:*`, a qué dominio o aplicación pertenece) y **tipo** (`type:*`, qué capa es). Cada proyecto lleva una de cada.
- La regla también detecta imports profundos y dependencias circulares entre proyectos.
- Si una dependencia viola un límite, no la permitas con `allow` para salir del paso: mueve el código a la librería correcta o crea una nueva.

### Comandos

```powershell
nx serve portal
nx build portal
nx test portal-feature-orders        # nombre del proyecto en su project.json
nx lint shared-ui
nx run-many -t lint test build       # todos los proyectos
nx affected -t lint test build       # solo lo afectado por los cambios
nx graph                             # grafo de proyectos y dependencias
```

- En un workspace Nx usa `nx`, no `ng`.
- `nx affected` compara con la rama base (`defaultBase` en `nx.json`, o `--base`/`--head`).
- Las tareas se cachean: no desactives la caché sin motivo y declara bien `inputs`/`outputs` si añades tareas propias.

### Actualizar Angular en Nx

```powershell
nx migrate latest                 # o una versión concreta de Nx
npm install                       # o el gestor del proyecto
nx migrate --run-migrations
```

- En Nx no se usa `ng update`: `nx migrate` actualiza Nx, Angular y los plugins y aplica las migraciones de todos ellos.
- Con Angular, **una versión mayor cada vez es obligatorio**: los paquetes de Angular solo mantienen las migraciones de la versión mayor anterior. Revisa `migrations.json` y el diff antes de confirmar.
- Proceso de validación tras actualizar: ver `environment.md`.

## Frontend y backend en el mismo monorepo Nx

Cuando el monorepo contiene también una API NestJS:

```javascript
// Ámbitos: el frontend nunca depende del backend
{ sourceTag: 'scope:web', onlyDependOnLibsWithTags: ['scope:web', 'scope:shared'] },
{ sourceTag: 'scope:api', onlyDependOnLibsWithTags: ['scope:api', 'scope:shared'] },
{ sourceTag: 'scope:shared', onlyDependOnLibsWithTags: ['scope:shared'] },
```

- **El frontend nunca importa librerías del backend**: arrastraría NestJS, `class-validator` u ORMs al bundle del navegador y expondría código de servidor.
- **Contrato compartido** en una librería `scope:shared` (por ejemplo `libs/shared/api-contracts`) que contiene **solo** interfaces, tipos y enums: sin decoradores, sin clases con lógica y sin dependencias de runtime. Los DTO de NestJS la implementan y Angular la consume:

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
// libs/web/data-access-orders/src/lib/orders-api.ts
import type { OrderDto } from '@acme/shared/api-contracts';

@Injectable({ providedIn: 'root' })
export class OrdersApi {
  private readonly http = inject(HttpClient);

  getOrder(id: string): Observable<OrderDto> {
    return this.http.get<OrderDto>(`/api/orders/${encodeURIComponent(id)}`);
  }
}
```

- Alternativa al contrato escrito a mano: generar el cliente Angular a partir del OpenAPI de la API. Elige una de las dos según las guidelines, no ambas.
- Un cambio incompatible en el contrato rompe frontend y backend a la vez: `nx affected` los detecta a los dos, pero si el frontend y la API se despliegan por separado, versiona el contrato y mantén la compatibilidad durante la transición.
- **Proxy de desarrollo**: `nx g @nx/angular:application ... --backendProject=api` configura el proxy de la aplicación hacia la API.
- **Qué agente usar**: Angular Architect para `apps/web` y `libs/web`; el agente de backend para la API. Para que Copilot aplique las reglas correctas al editar cada carpeta, añade instrucciones por ruta:

```markdown
---
applyTo: 'apps/web/**,libs/web/**'
---
Código Angular del frontend. Aplica las convenciones del agente Angular Architect y las skills `angular-*`.
No importes librerías con etiqueta `scope:api`.
```

Comprueba en la documentación de VS Code/GitHub Copilot la sintaxis de `applyTo` de tu versión.

## Configuración por aplicación

- **Entorno**: cada aplicación tiene su configuración (ver `environment.md`); no compartas un único `environment.ts` entre aplicaciones.
- **Traducciones**: los ficheros de idioma de cada aplicación en sus `assets`/`public`; las traducciones comunes, en una librería cuyos assets se copian a cada aplicación (ver `angular-i18n`).
- **Estilos**: tema y variables comunes en una librería; cada aplicación importa lo que necesita (ver la skill `angular-developer` (oficial)).

## CI

```yaml
# GitHub Actions — solo lo afectado por el PR (Nx)
- uses: actions/checkout@v4
  with:
    fetch-depth: 0          # nx affected necesita el historial para comparar con la base
- run: npm ci
- run: npx nx affected -t lint test build --base=origin/main --head=HEAD
```

- Con Angular CLI, construye y prueba cada proyecto de forma explícita (no hay `affected`).
- Con Nx, la caché remota (Nx Cloud u otra) acelera el CI; su uso lo deciden las guidelines.

## Checklist

- [ ] Tipo de workspace identificado (Angular CLI o Nx) y respetado
- [ ] Código compartido en librerías con tipo y ámbito
- [ ] Imports entre proyectos solo por el punto de entrada público; sin rutas relativas entre proyectos ni imports profundos
- [ ] Etiquetas en todos los proyectos y límites aplicados en lint (Nx) o reglas equivalentes (Angular CLI)
- [ ] Sin dependencias circulares entre proyectos
- [ ] Mecanismo de enlace del workspace respetado (aliases o workspaces)
- [ ] Comandos por proyecto o `nx affected`, nunca suponiendo una sola aplicación
- [ ] Actualizaciones con `nx migrate` en Nx, una versión mayor de Angular cada vez
- [ ] El frontend no importa nada con ámbito de backend; contratos solo con tipos
- [ ] Configuración, traducciones y estilos por aplicación
