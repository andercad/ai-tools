---
name: angular-state
description: 'Frontend Angular. Gestión de estado Angular con signals, computed, effects, resources y RxJS. Usar cuando: implementar estado reactivo en componentes o servicios, buscadores y autocompletados que consultan la API mientras se escribe (debounce, cancelar peticiones anteriores), usar toSignal/toObservable, usar resource/rxResource/httpResource, manejar suscripciones con takeUntilDestroyed, combinar observables, crear derived state. Cubre signal/computed/effect, integración RxJS, operadores declarativos, patrones de limpieza de suscripciones.'
argument-hint: 'Describe el estado o flujo reactivo que necesitas implementar.'
---

# Estado Reactivo: Signals, Computed, Effects, Resources y RxJS

## Cuándo usar signals vs observables

| Caso de uso                                        | Herramienta                                    |
| -------------------------------------------------- | ---------------------------------------------- |
| Estado local de componente o servicio              | `signal()`                                     |
| Estado derivado (computado)                        | `computed()`                                   |
| Estado derivado que también se puede sobrescribir  | `linkedSignal()` (si es estable en la versión) |
| Side-effects (DOM, almacenamiento, libs externas)  | `effect()`                                     |
| Llamadas HTTP, eventos del DOM, streams            | `Observable`                                   |
| Consumir observable en template/señal              | `toSignal()`                                   |
| Integrar señal en pipeline RxJS                    | `toObservable()`                               |
| Carga asíncrona dependiente de signals             | `rxResource()` / `httpResource()` / `resource()` — ver sección propia |

Regla general: **signals para estado, RxJS para flujos asíncronos** con cancelación, concurrencia o composición temporal (debounce, reintentos, combinación de fuentes).

## signal()

Estado local mutable. Inicializar con un valor coherente; evitar `undefined` salvo que el tipo lo requiera.

```typescript
// ✅ Estado mutable privado + vista de solo lectura
private readonly _items = signal<Item[]>([]);
readonly items = this._items.asReadonly(); // protected en componentes, public en servicios

private readonly _loading = signal(false);
readonly loading = this._loading.asReadonly();

// Modificar — solo dentro de la clase, desde métodos con intención
addItem(item: Item): void {
  this._items.update((list) => [...list, item]); // basado en valor anterior
}

clear(): void {
  this._items.set([]); // valor completo
}
```

**Reglas**:

- `set()` para valor completo; `update()` cuando el nuevo valor depende del anterior.
- **Signals escribibles siempre `private`**, con vista de solo lectura vía `asReadonly()`: `public` en servicios, `protected` en componentes. Ni otros componentes ni la plantilla pueden escribirlas; cada transición de estado pasa por un método de la clase (ver *Estado y visibilidad* en el agente).
- `readonly` en la declaración no basta: impide reasignar la propiedad, no llamar a `.set()`.
- Tratar los valores como inmutables: crear un nuevo array/objeto en lugar de mutar el existente (si mutas en sitio, la signal no notifica el cambio).
- **No usar `mutate()`** — no existe en Angular v17+.

```html
<!-- ❌ La plantilla modifica el estado directamente -->
<button type="button" (click)="count.set(0)">Reset</button>

<!-- ✅ La plantilla llama a un método; la transición vive en la clase -->
<button type="button" (click)="reset()">Reset</button>
```

## computed()

Estado derivado **puro**. Sin side-effects, sin llamadas HTTP, sin modificar otras señales.

```typescript
readonly total = computed(() => this._items().length);
readonly isEmpty = computed(() => this._items().length === 0);
readonly activeItems = computed(() =>
  this._items().filter((item) => item.status === 'active')
);

// ✅ Extraer lógica costosa a función privada para mantener computed() legible
readonly processedData = computed(() => this.buildProcessedData());

private buildProcessedData(): ProcessedData {
  const items = this._items();
  // lógica compleja...
}
```

**Reglas**:

- No anidar `computed()` innecesariamente.
- No derivar estado con `effect()` — usar `computed()`.
- No duplicar en una signal propia un estado que ya existe en otro sitio (por ejemplo, copiar la respuesta HTTP en un servicio y además en el componente). Una única fuente de verdad y el resto derivado.
- Un `computed()` ya es de solo lectura: no necesita `asReadonly()`.

## effect()

Solo para **side-effects**: DOM, almacenamiento, librerías externas, logging. Declarar siempre como **campo de clase**.

```typescript
// ✅ Correcto — campo de clase
readonly syncThemeEffect = effect(() => {
  document.documentElement.setAttribute('data-theme', this.theme());
});

// ✅ Persistir SOLO preferencias no sensibles (tema, idioma, tamaño de página...).
// Nunca tokens, datos personales, datos protegidos ni información de sesión (ver angular-security).
readonly persistEffect = effect(() => {
  localStorage.setItem('ui-prefs', JSON.stringify(this.uiPreferences()));
});

// ✅ untracked() para leer señales sin crear dependencias reactivas
readonly logEffect = effect(() => {
  const action = this.lastAction();
  const userId = untracked(() => this.authService.userId());
  this.logger.debug(`User ${userId} performed: ${action}`); // logger del proyecto, no console.log
});

// ❌ Evitar — no derivar estado en effect()
readonly badEffect = effect(() => {
  this._count.set(this._items().length); // usar computed() en su lugar
});

// ❌ Evitar — constructor solo para alojar un effect
constructor() {
  effect(() => { ... });
}
```

Los `effect()` se ejecutan también en el servidor con SSR. Protege los accesos a `document`, `window` o `localStorage` (con `afterNextRender()` o un servicio abstraído; ver `angular-ssr`).

## toSignal() — Observables en componentes

```typescript
// Básico
readonly items = toSignal(this.itemsService.getItems(), { initialValue: [] });

// Con estado de carga
readonly itemsResult = toSignal(
  this.itemsService.getItems().pipe(
    map((items) => ({ status: 'success' as const, items })),
    startWith({ status: 'loading' as const, items: [] as Item[] }),
    catchError(() => of({ status: 'error' as const, items: [] as Item[] })),
  ),
  { initialValue: { status: 'loading' as const, items: [] as Item[] } },
);

// Reactivo a un input signal
readonly id = input.required<string>();

readonly item = toSignal(
  toObservable(this.id).pipe(
    switchMap((id) => this.itemsService.getItem(id)),
  ),
  { initialValue: null },
);
```

`toSignal()` se suscribe en el momento de crearse y se desuscribe al destruirse el contexto de inyección: declárala como campo de clase.

## toObservable() — Señales en pipelines RxJS

```typescript
// Integrar una señal en un pipeline RxJS
readonly results = toSignal(
  toObservable(this.searchTerm).pipe(
    debounceTime(300),
    distinctUntilChanged(),
    filter((term) => term.length >= 2),
    switchMap((term) =>
      this.searchService.search(term).pipe(
        catchError(() => of([])), // el error no rompe el stream de búsqueda
      ),
    ),
  ),
  { initialValue: [] },
);
```

Coloca `catchError` **dentro** del `switchMap`: si está fuera, el primer error completa el stream y la búsqueda deja de funcionar.

## Resources — rxResource, httpResource y resource

Las APIs de resource permiten cargar datos asíncronos que dependen de signals, con estado de carga, error y cancelación integrados.

**Antes de usarlas**: comprueba en la documentación de la versión instalada si son estables, preview o experimentales, y cuál es su firma. Los nombres de las opciones cambiaron entre versiones (por ejemplo, `request`/`loader` en v19 frente a `params`/`stream` en versiones posteriores). `rxResource` es estable desde Angular 22. Respeta la restricción del agente de no usar APIs experimentales salvo petición explícita.

```typescript
// rxResource — el stream es un Observable (encaja con servicios HttpClient existentes)
readonly userId = input.required<string>();

readonly userResource = rxResource({
  params: () => ({ id: this.userId() }),
  stream: ({ params }) => this.usersService.getUser(params.id),
});

// httpResource — petición HTTP declarativa basada en signals
readonly userHttp = httpResource<User>(() => `/api/users/${this.userId()}`);
```

```html
@if (userResource.isLoading()) {
  <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
} @else if (userResource.error()) {
  <div class="alert alert-danger" role="alert">{{ 'errors.load-failed' | transloco }}</div>
} @else if (userResource.hasValue()) {
  <app-user-card [user]="userResource.value()" />
}
```

Un `ResourceRef` expone métodos de escritura (`set`, `reload`). En componentes, declara el resource `private` y expón a la plantilla solo lo que necesita (`protected readonly user = computed(() => this.userResource.value())`) si quieres impedir que la plantilla lo modifique.

**Cuándo usarlas**:

- Lectura de datos que depende de inputs/signals → resource.
- Escrituras (POST/PUT/DELETE) → no usar resource; usar el servicio HTTP con `subscribe` y `takeUntilDestroyed`, o el patrón del proyecto.
- Flujos complejos (debounce, combinación de varias fuentes, reintentos) → RxJS con `toSignal()`.

## takeUntilDestroyed() — Limpieza de suscripciones

Preferir `takeUntilDestroyed()` sobre `ngOnDestroy` manual:

```typescript
// ✅ En contexto de inyección (constructor / campo de clase)
readonly sub = this.eventService.events$.pipe(
  takeUntilDestroyed(),
).subscribe((event) => this.handleEvent(event));

// ✅ Fuera del contexto de inyección (dentro de métodos)
private readonly destroyRef = inject(DestroyRef);

loadData(): void {
  this.dataService.getData().pipe(
    takeUntilDestroyed(this.destroyRef),
  ).subscribe((data) => this._data.set(data));
}
```

## Operadores RxJS declarativos

Usar operadores declarativos. Pipelines cortos y legibles:

```typescript
// ✅ Pipeline declarativo
this.searchService.search(term).pipe(
  map((results) => results.filter((r) => r.active)),
  catchError(() => of([])),
);

// ✅ Combinar múltiples fuentes
readonly dashboardData = toSignal(
  combineLatest({
    items: this.itemsService.getItems(),
    user: this.authService.currentUser$,
  }).pipe(
    map(({ items, user }) => ({ items, userName: user.name })),
  ),
  { initialValue: null },
);

// ❌ Evitar subscribe() anidado
this.http.get<Parent>('/api').subscribe((data) => {
  this.http.get<Child>(`/api/${data.id}`).subscribe((nested) => { // ❌ anidado
    ...
  });
});

// ✅ Encadenar con un operador de aplanado
this.http.get<Parent>('/api').pipe(
  switchMap((data) => this.http.get<Child>(`/api/${data.id}`)),
);
```

**Operadores preferidos**: `map`, `filter`, `switchMap`, `mergeMap`, `concatMap`, `exhaustMap`, `combineLatest`, `forkJoin`, `startWith`, `catchError`, `debounceTime`, `distinctUntilChanged`, `take`, `takeUntil`.

Elegir el operador de aplanado según la semántica:

| Operador     | Úsalo cuando                                                    |
| ------------ | --------------------------------------------------------------- |
| `switchMap`  | Solo importa la última petición (búsquedas, cambio de id)       |
| `concatMap`  | El orden importa y no se deben solapar (guardados secuenciales) |
| `mergeMap`   | Las peticiones son independientes y pueden ir en paralelo       |
| `exhaustMap` | Ignorar nuevas peticiones mientras hay una en curso (doble clic en submit) |
