---
name: angular-conventions
description: 'Convenciones de código por defecto del plugin Angular estructura de carpetas por funcionalidad más shared, páginas separadas de componentes reutilizables, un .html por componente (sin template inline), alias de tsconfig por carpeta y separadores de sección en clases. Usar cuando se cree o mueva un componente, página, servicio, guard, interceptor, modelo o util, cuando se configuren alias de tsconfig o se decida dónde ubicar código nuevo. No usar para decisiones de topología (monorepo, microfrontends); para eso, angular-architecture.'
---

# Convenciones de código Angular

Aplican por defecto al **código nuevo**. Si el `CLAUDE.md` del proyecto (`## Convenciones Angular`) declara otra `structure` o `templates: inline`, manda el proyecto. No migres código existente sin petición expresa.

## 1. Estructura de carpetas

```
src/app/
  shared/                  ← común a toda la app, incluido lo global
    components/            ← componentes reutilizables (layout, botones, diálogos...)
    pipes/  directives/  services/  models/  guards/  interceptors/  utils/
  functionality1/                  ← una carpeta por funcionalidad (antes, un módulo)
    components/            ← reutilizables dentro de la funcionalidad
    pages/                 ← componentes de ruta
    services/  models/  guards/  interceptors/  utils/
    functionality1.routes.ts
```

- Crea solo las subcarpetas que se usen.
- Una carpeta por funcionalidad detectada. No hay `core/`: lo global (interceptores, guards, servicios, layout) va en la subcarpeta correspondiente de `shared/`.
- Dependencias permitidas: funcionalidad → `shared`. Una funcionalidad no importa de otra; `shared` no importa de ninguna funcionalidad. Si dos funcionalidades necesitan lo mismo, súbelo a `shared`.
- **Páginas**: todo componente que se enruta (`loadComponent`, `component:` en rutas) va en `pages/`. Lo que se reutiliza va en `components/`. Un componente no es las dos cosas.
- Nombres de fichero: sigue el CLI de la versión instalada (`order-list.ts` en v20+, `order-list.component.ts` antes) y mantén el del repo.

## 2. Un `.html` por componente

Todo componente declara `templateUrl` (y `styleUrl` si tiene estilos). **Nunca `template:` inline**, tampoco para componentes de una línea.

```typescript
@Component({
	selector: 'app-xxx-card',
	templateUrl: './xxx-card.html',
	styleUrl: './xxx-card.css',
	changeDetection: ChangeDetectionStrategy.OnPush,
})
export class XxxCard {
	/* ... */
}
```

El hook `Stop` del plugin bloquea el cierre si un componente nuevo o modificado usa `template:`.

## 3. Alias de `tsconfig.json`

Un alias por funcionalidad y uno para `shared`:

```json
"paths": {
  "@shared/*": ["src/app/shared/*"],
  "@functionality1/*": ["src/app/functionality1/*"]
}
```

- Crea el alias **antes** de usarlo, al crear la carpeta. En monorepo, en el `tsconfig.base.json`.
- Importa siempre por alias; imports relativos solo dentro de la misma carpeta de funcionalidad o por dependencia cíclica documentada.
- No uses nombres que choquen con paquetes npm (`@angular`, `@ngrx`...).
- Si la versión de TypeScript exige `baseUrl` para `paths`, compruébalo en la documentación y respeta lo que ya haga el repo.

```typescript
// ✅
import { XxxService } from '@functionality1/services/xxx-service';
import { Button } from '@shared/components/button/button';
// ❌
import { XxxService } from '../../services/xxx-service';
```

## 4. Separadores de sección en clases

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

## 5. Documentación (con `docs: jsdoc`)

- Componentes **reutilizables** (`components/`): JSDoc con `@example` de uso.
- Componentes de **página** (`pages/`): JSDoc sin `@example`.
- Servicios y utils: propósito y parámetros no obvios.
