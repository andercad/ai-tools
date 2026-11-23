---
name: angular-performance
description: 'Frontend Angular. Rendimiento Angular: carga diferida, optimización de bundles, detección de cambios, lazy loading de imágenes. Usar cuando: optimizar tiempo de carga inicial, implementar @defer con viewport o interaction, configurar track en @for, optimizar imágenes con NgOptimizedImage, evitar renders innecesarios, perfilar bundle size, registrar providers en componentes lazy. Cubre @defer, track, OnPush, bundle splitting, virtual scroll.'
argument-hint: 'Describe el componente, lista o imagen que necesitas optimizar.'
---

# Rendimiento

## Medir antes y después

Las reglas de esta skill son buenas prácticas preventivas. Cuando la tarea sea **resolver un problema de rendimiento**, no optimices por intuición:

1. Medir la situación inicial (bundle, Lighthouse/Web Vitals, Angular DevTools profiler).
2. Identificar el cuello de botella real.
3. Aplicar un cambio cada vez.
4. Volver a medir y documentar la mejora.

```powershell
# Tamaño de bundles y presupuestos (en un monorepo, indica la aplicación: ng build <app> / nx build <app>)
ng build --configuration production
# Análisis detallado (requiere source maps)
npx source-map-explorer dist/<app>/browser/*.js
```

Si el problema es el tiempo hasta el primer contenido (LCP) en páginas públicas, valora SSR o prerenderizado (ver `angular-ssr`).

## @defer — Carga diferida de componentes

Usar `@defer` para componentes pesados, fuera del viewport inicial o cargados bajo demanda:

```html
<!-- Diferir hasta que el elemento entra en el viewport -->
@defer (on viewport) {
<app-data-chart [data]="chartData()" />
} @placeholder {
<div class="card placeholder-glow" style="height: 300px;">
  <div class="card-body">
    <span class="placeholder col-12 h-100"></span>
  </div>
</div>
} @loading (minimum 300ms) {
<div class="d-flex justify-content-center py-4">
  <div class="spinner-border text-primary" aria-hidden="true"></div>
</div>
} @error {
<div class="alert alert-warning">{{ 'errors.chart-load-failed' | transloco }}</div>
}

<!-- Diferir hasta interacción del usuario -->
@defer (on interaction(triggerRef)) {
<app-detail-panel [item]="selectedItem()" />
} @placeholder {
<button #triggerRef type="button" class="btn btn-outline-primary">
  {{ 'actions.view-details' | transloco }}
</button>
}

<!-- Diferir por condición (idle + when) -->
@defer (on idle; when dataLoaded()) {
<app-secondary-widget />
}
```

**Triggers disponibles**:

- `on viewport` — cuando el placeholder entra en el viewport
- `on interaction(ref)` — al hacer click o focus en el elemento ref
- `on hover(ref)` — al pasar el ratón por el elemento ref
- `on idle` — cuando el navegador está inactivo
- `on timer(2s)` — después de N ms/s
- `when condition` — cuando la expresión se vuelve `true`

Las dependencias de un bloque `@defer` solo se separan en otro chunk si son standalone y no se usan fuera del bloque en el mismo componente. Con SSR, los triggers `hydrate on ...` controlan la hidratación incremental (ver `angular-ssr`).

## track en @for — obligatorio siempre

```html
<!-- ✅ Preferir propiedad única (id) -->
@for (item of items(); track item.id) {
<app-item-card [item]="item" />
}

<!-- ✅ track $index solo cuando no hay id estable y la lista no se reordena -->
@for (tab of tabs(); track $index) {
<li class="nav-item">{{ tab.label }}</li>
}

<!-- ❌ Sin track — no compila en el control flow moderno; y track por objeto completo recrea DOM -->
@for (item of items()) {
<app-item-card [item]="item" />
}
```

## Proveedores en componentes lazy — no en app.config.ts

Registrar librerías pesadas **en el componente lazy** que las consume, no globalmente:

```typescript
// ❌ En app.config.ts — se incluye en el bundle principal
export const appConfig: ApplicationConfig = {
  providers: [
    provideCharts(withDefaultRegisterables()), // Bundle principal inflado
  ],
};

// ✅ En el componente lazy que lo usa
@Component({
  // ...resto de metadatos
  providers: [
    provideCharts(withDefaultRegisterables()), // Solo en el bundle de este componente
  ],
})
export class DataChartComponent { ... }
```

## NgOptimizedImage — imágenes

```typescript
import { NgOptimizedImage } from '@angular/common';

@Component({
  imports: [NgOptimizedImage],
  template: `
    <!-- ✅ LCP image — siempre priority -->
    <img
      ngSrc="assets/logo.png"
      alt="Logo de la aplicación"
      width="200"
      height="60"
      priority
    />

    <!-- ✅ Imagen below the fold — sin priority -->
    <img
      ngSrc="assets/user-avatar.png"
      [alt]="user().name"
      width="48"
      height="48"
    />

    <!-- ❌ NgOptimizedImage no funciona con base64 inline -->
    <!-- usar <img> normal para base64 -->
  `,
})
```

**Nota**: `NgOptimizedImage` no funciona con imágenes base64 inline. Usar `<img>` nativo para esas. Siempre definir `width`/`height` (o `fill`) para evitar layout shift.

## OnPush — detección de cambios

Mientras la versión instalada no lo aplique por defecto, `ChangeDetectionStrategy.OnPush` es obligatorio en **todos** los componentes. En versiones donde ya es el valor por defecto, no lo declares salvo que las guidelines lo exijan. Con signals es automático — solo se redibuja cuando una signal leída en el template cambia.

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush, // si la versión no lo aplica por defecto
  // ...
})
```

## Virtual scroll para listas largas

Para listas largas (orientativo: más de 50 elementos complejos, o cuando el profiler muestre coste de render apreciable):

```typescript
import { ScrollingModule } from '@angular/cdk/scrolling';

@Component({
  selector: 'app-item-list',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ScrollingModule],
  template: `
    <cdk-virtual-scroll-viewport itemSize="72" class="list-viewport">
      <app-item-row *cdkVirtualFor="let item of items(); trackBy: trackById" [item]="item" />
    </cdk-virtual-scroll-viewport>
  `,
  styles: [`
    .list-viewport {
      height: 400px;
    }
  `],
})
export class ItemListComponent {
  readonly items = input.required<Item[]>();
  protected readonly trackById = (_: number, item: Item): string => item.id;
}
```

`cdk-virtual-scroll-viewport` virtualiza con `*cdkVirtualFor`; un `@for` normal dentro del viewport **no** se virtualiza. Comprueba en la documentación del CDK instalado si existe soporte de control flow para virtualización.

## Optimizar computed() y effect()

La semántica de signals (cuándo usar `computed`, `effect`, `untracked`) está en `angular-state`. Desde el punto de vista de rendimiento:

```typescript
// ❌ Operación costosa directamente en computed()
readonly processedData = computed(() => {
  return this._rawData()
    .flatMap(item => item.details)
    .filter(detail => complexFilter(detail))
    .reduce(heavyAggregation, {});
});

// ✅ Extraer lógica a método privado — más legible y testeable
readonly processedData = computed(() => this.processRawData(this._rawData()));

private processRawData(data: RawItem[]): ProcessedData {
  return data
    .flatMap(item => item.details)
    .filter(detail => complexFilter(detail))
    .reduce(heavyAggregation, {});
}

// ❌ effect() con dependencias innecesarias: se re-ejecuta al cambiar cualquiera
readonly badEffect = effect(() => {
  const allData = this.allItems();
  const config = this.config();       // no se usa realmente
  const prefs = this.preferences();   // no se usa realmente
  this.cache.save(allData);
});

// ✅ untracked() para leer señales sin crear dependencia
readonly saveEffect = effect(() => {
  const data = this.allItems(); // dependencia real
  const userId = untracked(() => this.authService.userId()); // solo para contexto
  this.cache.save(`cache-${userId}`, data);
});
```

Recuerda que `computed()` ya memoiza: el coste solo importa si sus dependencias cambian con frecuencia o el cálculo es realmente pesado.

## Lazy loading de rutas

```typescript
// ✅ Siempre loadComponent / loadChildren — nunca imports estáticos de páginas
export default [
  {
    path: 'dashboard',
    loadComponent: () => import('@pages/dashboard/dashboard'),
    // El bundle de dashboard se carga solo cuando se navega a /dashboard
  },
  {
    path: 'reports',
    loadChildren: () => import('@pages/reports/reports.routes'),
    // Toda la funcionalidad de informes en un bundle separado
  },
] satisfies Routes;
```

## Checklist de rendimiento

- [ ] `@defer` en componentes pesados o bajo el fold
- [ ] `track item.id` (o propiedad estable) en todos los `@for`
- [ ] Providers de librerías pesadas en componentes lazy, no en `app.config.ts`
- [ ] `NgOptimizedImage` en todas las imágenes estáticas (excepto base64)
- [ ] Listas largas con virtual scroll cuando el render lo justifique
- [ ] `untracked()` cuando un `effect()` lee señales solo para contexto
- [ ] No hay operaciones costosas síncronas en `computed()`
- [ ] Presupuestos (`budgets`) de `angular.json` (o del `project.json` de la aplicación) sin superar
- [ ] Si se optimizó un problema concreto: medición antes/después documentada
