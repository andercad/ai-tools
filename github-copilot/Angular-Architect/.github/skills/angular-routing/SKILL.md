---
name: angular-routing
description: 'Frontend Angular. Rutas Angular, lazy loading, guards y configuración de navegación. Usar cuando: añadir nuevas rutas, crear guards de acceso, configurar lazy loading de componentes o módulos de rutas, proteger rutas con canMatch, definir títulos de página, organizar ficheros de rutas por funcionalidad, configurar la ruta comodín o redirecciones. Cubre *.routes.ts, loadComponent, loadChildren, canMatchFn, withTranslocoScope.'
argument-hint: 'Describe la ruta o guard que necesitas implementar.'
---

# Routing, Guards y Lazy Loading

## Estructura de ficheros de rutas

- Sufijo `*.routes.ts` y exportar como `export default`.
- Agrupar rutas de una funcionalidad en su propio `*.routes.ts`.
- No definir lógica de negocio en ficheros de rutas.

```
src/app/
├── app.routes.ts          ← rutas raíz
└── pages/
    ├── home/
    │   └── home.routes.ts
    └── products/
        └── products.routes.ts
```

Con SSR existe además `app.routes.server.ts`, que asigna un modo de renderizado a cada ruta y debe corresponderse con estas rutas (ver `angular-ssr`).

En un monorepo, las rutas de una funcionalidad viven en su librería `feature` y la aplicación las carga por el punto de entrada público de la librería (ver `angular-monorepo`):

```typescript
// apps/portal/src/app/app.routes.ts
{
  path: 'orders',
  loadChildren: () => import('@acme/portal/feature-orders').then((m) => m.ordersRoutes),
}
```

## Rutas raíz — app.routes.ts

```typescript
import type { Routes } from '@angular/router';

export default [
  {
    path: '',
    canMatch: [authenticatedGuard],
    loadChildren: () => import('@pages/home/home.routes'),
  },
  {
    path: 'init',
    loadChildren: () => import('@pages/init-page/init-page.routes'),
  },
  {
    path: '**',
    redirectTo: '',
  },
] satisfies Routes;
```

## Rutas de funcionalidad

```typescript
// pages/home/home.routes.ts
import type { Routes } from '@angular/router';
import { withTranslocoScope } from '@utils/shared';

export default [
  withTranslocoScope(['home', 'widgets'], {
    path: '',
    title: 'home.page-title',
    loadComponent: () => import('@pages/home/home/home'),
  }),
  withTranslocoScope(['home'], {
    path: 'detail/:id',
    title: 'home.detail-title',
    loadComponent: () => import('@pages/home/detail/detail'),
  }),
] satisfies Routes;
```

**Reglas**:

- Usar **siempre** `loadComponent` y `loadChildren`. **No importar componentes de página estáticamente**.
- Definir `title` en cada ruta para la estrategia de títulos.
- Usar `canMatch` en lugar de `canActivate` para rutas lazy protegidas.
- Registrar scopes Transloco con `withTranslocoScope()` de `@utils/shared` cuando el proyecto disponga de ese helper. No usar `provideTranslocoScope` directamente.
- Para leer parámetros de ruta en componentes, preferir `withComponentInputBinding()` + `input()` frente a suscribirse a `ActivatedRoute`, si el proyecto lo tiene habilitado.

## Guards — canMatchFn (preferido)

Usar **exclusivamente funciones** (`CanMatchFn`, `CanActivateFn`, `CanDeactivateFn`). No usar clases.

**Un guard controla la navegación, no la seguridad.** Ocultar una ruta en el cliente no protege los datos: el backend debe autorizar cada petición.

```typescript
// guards/authenticated-guard.ts
export const authenticatedGuard: CanMatchFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    return router.createUrlTree(['/login']);
  }

  return true;
};
```

```typescript
// guards/role-guard.ts — con parámetro
export const roleGuard = (requiredRole: UserRole): CanMatchFn =>
  () => {
    const authService = inject(AuthService);
    const router = inject(Router);

    if (!authService.hasRole(requiredRole)) {
      return router.createUrlTree(['/forbidden']);
    }

    return true;
  };

// Uso en rutas:
{
  path: 'admin',
  canMatch: [roleGuard('admin')],
  loadComponent: () => import('@pages/admin/admin'),
}
```

**Reglas**:

- `CanMatchFn` sobre `CanActivateFn`: se ejecuta antes de cargar el bundle lazy.
- Inyectar servicios con `inject()` dentro del cuerpo de la función.
- Devolver `true`, `false` o `UrlTree`. Si es asíncrono, usar `Observable<boolean | UrlTree>` con `take(1)`.
- Sufijo `-guard` en fichero: `auth-guard.ts`.
- Exportar desde `guards/index.ts`.
- Con SSR, los guards también se ejecutan en el servidor, donde no hay sesión del navegador (token en memoria): decide qué hacen allí (ver `angular-ssr`).

## Guard asíncrono

```typescript
export const permissionsGuard: CanMatchFn = () => {
  const permissionsService = inject(PermissionsService);
  const router = inject(Router);

  return permissionsService.loadPermissions().pipe(
    map((permissions) => (permissions.canAccess ? true : router.createUrlTree(['/forbidden']))),
    catchError(() => of(router.createUrlTree(['/error']))),
    take(1),
  );
};
```

Gestiona el error del observable: un guard que falla sin `catchError` deja la navegación cancelada sin feedback.

## CanDeactivate — confirmación al salir

```typescript
export const unsavedChangesGuard: CanDeactivateFn<{ hasUnsavedChanges: () => boolean }> = (
  component,
) => {
  if (!component.hasUnsavedChanges()) {
    return true;
  }

  const transloco = inject(TranslocoService);
  const message = transloco.translate('common.unsaved-changes-confirm');
  return window.confirm(message);
};
```

Si el proyecto usa SSR, no accedas a `window` sin comprobar que se ejecuta en el navegador; en ese caso, usa un diálogo propio.

## Navegación programática

```typescript
private readonly router = inject(Router);

navigateToDetail(id: string): void {
  this.router.navigate(['/items', id]);
}

navigateWithState(id: string): void {
  this.router.navigate(['/items', id], {
    queryParams: { from: 'list' },
  });
}
```

No incluyas datos sensibles o identificativos en path params ni query params (ver `angular-security`).

## Deep links y despliegue

- **Sin SSR**: el servidor web (nginx, etc.) debe devolver `index.html` para las rutas desconocidas, para que funcionen los deep links y la ruta comodín `**`.
- **Con SSR**: las redirecciones y la ruta comodín se resuelven también en el servidor; si en producción no redirigen, el problema suele estar en qué servidor atiende la petición y en `app.routes.server.ts`, no en `app.routes.ts`. Sigue el diagnóstico de `angular-ssr`.
