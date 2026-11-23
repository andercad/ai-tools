---
name: angular-http
description: 'Frontend Angular. HTTP Angular: interceptores, manejo de errores, llamadas de API en servicios. Usar cuando: mostrar una notificación global cuando falla cualquier petición, crear servicios con HttpClient, implementar interceptores, manejar errores HTTP, definir estados de carga/error en componentes, gestionar errores 4xx de negocio. Cubre cadena de interceptores del proyecto, responsabilidades por interceptor, patrones catchError, señales de estado.'
argument-hint: 'Describe el servicio o interceptor HTTP que necesitas implementar.'
---

# HTTP y Manejo de Errores

## Cadena de interceptores del proyecto

Ver `guidelines/coding-guidelines.md` → _Cadena de interceptores HTTP_ para el orden obligatorio y la responsabilidad de cada interceptor. No duplicar lógica que ya gestione un interceptor existente (autenticación, errores globales, notificaciones, base URL...).

## Patrón para errores de negocio en servicios

Transformar un código de error en un valor (por ejemplo, `404` → `null`) **solo cuando el contrato de la API lo define como resultado esperado**. El resto de errores se propagan.

```typescript
@Injectable({ providedIn: 'root' })
export class ItemsService {
  private readonly http = inject(HttpClient);

  /** Devuelve null si el elemento no existe (404 es un resultado esperado según el contrato). */
  getItem(id: string): Observable<Item | null> {
    return this.http.get<Item>(`/api/items/${encodeURIComponent(id)}`).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 404) {
          return of(null);
        }
        return throwError(() => error); // Propagar errores no manejados
      }),
    );
  }
}
```

## Estados de carga y error en componentes

Representar los estados mediante señales privadas expuestas en solo lectura:

```typescript
export default class ItemDetailComponent {
  // ========== Dependencies ==========
  private readonly itemsService = inject(ItemsService);
  private readonly destroyRef = inject(DestroyRef);

  // ========== State ==========
  private readonly _loading = signal(false);
  protected readonly loading = this._loading.asReadonly();
  private readonly _error = signal<string | null>(null);
  protected readonly error = this._error.asReadonly();
  private readonly _item = signal<Item | null>(null);
  protected readonly item = this._item.asReadonly();

  // ========== Public methods ==========
  protected loadItem(id: string): void {
    this._loading.set(true);
    this._error.set(null);

    this.itemsService
      .getItem(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (item) => {
          this._item.set(item);
          this._loading.set(false);
        },
        error: () => {
          this._error.set('errors.load-failed');
          this._loading.set(false);
        },
      });
  }
}
```

O usando `toSignal()` con estado derivado (cancela la petición anterior al cambiar el `id` gracias a `switchMap`). Al ser derivado, no necesita signal privada:

```typescript
readonly itemId = input.required<string>();

readonly itemResult = toSignal(
  toObservable(this.itemId).pipe(
    switchMap((id) =>
      this.itemsService.getItem(id).pipe(
        map((item) => ({ status: 'success' as const, item })),
        catchError(() => of({ status: 'error' as const, item: null })),
        startWith({ status: 'loading' as const, item: null }),
      ),
    ),
  ),
  { initialValue: { status: 'loading' as const, item: null } },
);
```

Si la versión instalada ofrece `rxResource`/`httpResource` como API estable, son una alternativa para este caso (ver `angular-state`).

## Patrón de interceptor (función)

```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  if (!token) {
    return next(req);
  }

  const authReq = req.clone({
    setHeaders: { Authorization: `Bearer ${token}` },
  });

  return next(authReq);
};
```

### Interceptor de errores global

Para notificar al usuario de forma centralizada, un interceptor dedicado (no mezclar con el de autenticación):

```typescript
export const errorNotificationInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Los 4xx de negocio los gestiona cada servicio/pantalla; aquí solo lo inesperado
      if (error.status === 0 || error.status >= 500) {
        notifications.error(error.status === 0 ? 'errors.network' : 'errors.server');
      }
      return throwError(() => error); // propagar siempre: el llamante decide su estado de UI
    }),
  );
};
```

- El interceptor **notifica y propaga**; nunca se traga el error ni devuelve un valor por defecto.
- 401: delega en el flujo de sesión (refresh o login), no en un toast genérico.
- Con SSR, los interceptores también se ejecutan en el servidor: no muestres notificaciones de UI allí (ver `angular-ssr`).

- Declarar siempre como **funciones** (`HttpInterceptorFn`). No usar clases.
- Cada interceptor tiene **una única responsabilidad**.
- Usar `req.clone({ ... })` para modificar la petición (son inmutables).
- Registrar con `withInterceptors([...])` en `app.config.ts` en el orden definido en las guidelines.
- El token solo se adjunta a peticiones dirigidas a la API propia, nunca a dominios de terceros (ver `angular-security`).

## Llamadas HTTP en servicios

- Los métodos HTTP devuelven `Observable<T>`. La conversión a señal la hace el componente con `toSignal()`.
- Tipar **siempre** el genérico de `HttpClient` con la interfaz exacta:

```typescript
// ✅ Correcto
this.http.get<Item[]>('/api/items');
this.http.post<CreatedItem>('/api/items', body);

// ❌ Evitar — sin tipo o con any
this.http.get('/api/items');
this.http.get<any>('/api/items');
```

- Codificar los valores dinámicos de la URL (`encodeURIComponent`) o usar `HttpParams` para query params.
- Si el DTO de la API difiere semánticamente del modelo de la UI, mapear en el servicio con `map()`.
- En un monorepo con el backend, tipa las respuestas con los contratos de la librería compartida en lugar de duplicarlos (ver `angular-monorepo`).

## Reintentos

No implementar reintentos automáticos en servicios de negocio. Si un caso concreto lo requiere:

- Solo para operaciones **idempotentes** (GET, PUT/DELETE idempotentes). **Nunca** reintentar POST de creación sin una clave de idempotencia acordada con el backend.
- Solo ante fallos transitorios (red, 502/503/504), no ante 4xx.
- Documentar la justificación.

```typescript
// Solo con justificación documentada
this.http.get<Item>('/api/items/critical').pipe(
  // Reintento para operación de lectura crítica propensa a fallos transitorios de red
  retry({
    count: 2,
    delay: (error: HttpErrorResponse) =>
      [0, 502, 503, 504].includes(error.status) ? timer(1000) : throwError(() => error),
  }),
);
```
