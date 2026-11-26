---
name: angular-conventions
description: 'Convenciones de código por defecto del plugin Angular estructura de carpetas por funcionalidad más shared, páginas separadas de componentes reutilizables, un .html por componente (sin template inline), alias de tsconfig por carpeta, tsconfig estricto explícito (strict, strictTemplates) y separadores de sección en clases. Usar cuando se cree o mueva un componente, página, servicio, guard, interceptor, modelo o util, cuando se configuren alias o strictness de tsconfig o se decida dónde ubicar código nuevo. No usar para decisiones de topología (monorepo, microfrontends); para eso, angular-architecture. Define el estilo y la estructura del código (defaults del plugin); la política de calidad del proyecto (tests, a11y, docs) va en angular-project-guidelines.'
---

# Convenciones de código Angular

Aplican por defecto al **código nuevo**. Si el `CLAUDE.md` del proyecto (`## Convenciones Angular`) declara otra `structure` o `templates: inline`, manda el proyecto. No migres código existente sin petición expresa.

## 1. Estructura de carpetas

```
src/app/
  shared/                  ← común a toda la app, sin dominio
    components/            ← componentes reutilizables (layout, botones, diálogos...)
    pipes/  directives/  services/  models/  utils/   ← genéricos, sin lógica de una funcionalidad
  orders/                  ← una carpeta por funcionalidad (antes, un módulo)
    components/            ← reutilizables dentro de la funcionalidad
    pages/                 ← componentes de ruta
    services/  models/  guards/  interceptors/  utils/
    orders.routes.ts
  auth/
    services/  guards/  interceptors/  models/
    auth.routes.ts
```

- Crea solo las subcarpetas que se usen.
- Una carpeta por funcionalidad detectada. Cada pieza va en la funcionalidad a la que pertenece: `AuthService`, `authGuard` o el interceptor del token van en `auth/`; `OrderService` en `orders/`. Solo lo genérico sin dominio (modelo o servicio genérico, layout, pipes, utils) va en `shared/`. No hay `core/`.
- Dependencias permitidas: funcionalidad → `shared`. Una funcionalidad no importa de otra salvo por su API pública (barrel o alias de la funcionalidad dueña); `shared` no importa de ninguna funcionalidad. Si una pieza genérica es necesaria en dos funcionalidades, súbela a `shared`; si es de dominio, expón su API pública desde la funcionalidad dueña.
- Los guards, interceptores y providers que cablea la aplicación (`app.config.ts`, `app.routes.ts`) pueden importar de cualquier funcionalidad: son la capa de composición.
- **Páginas**: todo componente que se enruta (`loadComponent`, `component:` en rutas) va en `pages/`. Lo que se reutiliza va en `components/`. Un componente no es las dos cosas.
- **Páginas con `export default`**: la clase de cada página se exporta `export default class OrderListPage {}` (un solo export por fichero) y las rutas la cargan sin `.then`: `loadComponent: () => import('@orders/pages/order-list/order-list')`. Aplica solo a páginas; los componentes de `components/` usan export con nombre.
- Nombres de fichero: sigue el CLI de la versión instalada (`order-list.ts` en v20+, `order-list.component.ts` antes) y mantén el del repo.

### Rutas

Todas las rutas son lazy. `app.routes.ts` tiene una entrada por funcionalidad y el nivel depende de cuántas páginas tenga:

```typescript
// app.routes.ts
export const routes: Routes = [
	// Funcionalidad con una sola página: se registra aquí, sin <funcionalidad>.routes.ts
	{ path: 'login', loadComponent: () => import('@auth/pages/login/login') },
	// Funcionalidad con varias páginas o rutas hijas: router propio, cargado en bloque
	{ path: 'orders', loadChildren: () => import('@orders/orders.routes').then((m) => m.ORDERS_ROUTES) },
];

// orders/orders.routes.ts
export const ORDERS_ROUTES: Routes = [
	{ path: '', loadComponent: () => import('@orders/pages/order-list/order-list') },
	{ path: ':id', loadComponent: () => import('@orders/pages/order-detail/order-detail') },
];
```

- **Primer nivel** (`app.routes.ts`): un `path` por funcionalidad. Una sola página → `loadComponent` directo. Varias → `loadChildren` hacia `<funcionalidad>.routes.ts`.
- **Segundo nivel** (`<funcionalidad>.routes.ts`): solo si la funcionalidad tiene 2+ rutas (páginas, detalle, rutas hijas con `children`). Un router de segundo nivel con una sola ruta es sobreingeniería: súbela a `app.routes.ts`.
- Si una funcionalidad con router propio se queda con una sola ruta, súbela y elimina el fichero; si una de página única crece, crea su `<funcionalidad>.routes.ts` y cambia a `loadChildren`.
- Nunca `component:` (eager) ni `children:` con un array importado estáticamente. Siempre `loadComponent` / `loadChildren`.
- `loadComponent` apunta a `pages/` y sin `.then` (ver "Páginas con `export default`").
- Redirects (`redirectTo`), comodines (`**`) y guards se declaran junto a la ruta que los usa.
- El hook `Stop` (`check-routes.mjs`) lo hace cumplir: bloquea `component:`, `loadComponent` fuera de `pages/` o con `.then`, `children:` estático, `*.routes.ts` de una sola ruta y páginas sin `export default class`. Se desactiva con `routes: free` en el `CLAUDE.md`.

## 2. Un `.html` por componente

Todo componente declara `templateUrl` (y `styleUrl` si tiene estilos). **Nunca `template:` inline**, tampoco para componentes de una línea.

```typescript
@Component({
	selector: 'app-order-card',
	templateUrl: './order-card.html',
	styleUrl: './order-card.css',
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class OrderCard {
	/* ... */
}
```

El hook `Stop` del plugin bloquea el cierre si un componente nuevo o modificado usa `template:`.

## 3. Alias de `tsconfig.json`

Un alias por funcionalidad y uno para `shared`:

```json
"paths": {
  "@shared/*": ["src/app/shared/*"],
  "@orders/*": ["src/app/orders/*"]
}
```

- Crea el alias **antes** de usarlo, al crear la carpeta. En monorepo, en el `tsconfig.base.json`.
- Importa siempre por alias; imports relativos solo dentro de la misma carpeta de funcionalidad o por dependencia cíclica documentada.
- No uses nombres que choquen con paquetes npm (`@angular`, `@ngrx`...).
- Si la versión de TypeScript exige `baseUrl` para `paths`, compruébalo en la documentación y respeta lo que ya haga el repo.

```typescript
// ✅
import { OrderService } from '@orders/services/order-service';
import { Button } from '@shared/components/button/button';
// ❌
import { OrderService } from '../../services/order-service';
```

## 4. TypeScript y templates estrictos

`strict` depende de la versión de TypeScript (`npx tsc -v`):

- **TS ≥ 6**: el default ya es `strict: true`; no hace falta escribirlo y su ausencia no es un fallo. Nunca pongas `strict: false`.
- **TS < 6**: el default es `false`; `strict: true` es obligatorio y explícito.

El resto va explícito en el `tsconfig.json` (en monorepo, en `tsconfig.base.json`); `strictTemplates` es de Angular y no lo cubre TS:

```json
{
  "compilerOptions": {
    "strict": true, // solo necesario en TS < 6
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  },
  "angularCompilerOptions": {
    "strictInjectionParameters": true,
    "strictInputAccessModifiers": true,
    "strictTemplates": true
  }
}
```

- Si falta alguna clave en un proyecto nuevo, añádela. No uses `any` para esquivar errores de strict.
- En proyecto existente sin strict, no lo actives en bloque ni cambies el `tsconfig`: propónlo como paso aparte, flag a flag.

## 5. Separadores de sección en clases

Delimita los bloques con este orden canónico (componentes, servicios, directivas y guards de clase):

```typescript
// ========== Dependencies ==========
// ========== Inputs ==========
// ========== Outputs ==========
// ========== State ==========
// ========== Computed ==========
// ========== Lifecycle ==========
// ========== Public methods ==========
// ========== Private methods ==========
```

- Incluye solo los bloques con al menos un miembro.
- Puedes renombrar un bloque cuando aclare (p. ej. `// ========== HTTP ==========` en un servicio con muchas llamadas).
- No uses separadores en clases de pocas líneas sin bloques que distinguir.

## 6. Documentación (con `docs: jsdoc`)

- Componentes **reutilizables** (`components/`): JSDoc con `@example` de uso.
- Componentes de **página** (`pages/`): JSDoc sin `@example`.
- Servicios y utils: propósito y parámetros no obvios.
