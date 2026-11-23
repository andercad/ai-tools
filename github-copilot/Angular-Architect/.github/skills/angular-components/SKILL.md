---
name: angular-components
description: 'Frontend Angular. Patrones Angular para componentes, directivas, pipes, servicios, tokens de inyección e inicializadores. Usar cuando: crear o modificar componentes, directivas, pipes, servicios; definir interfaces y tipos; configurar InjectionToken; implementar provideAppInitializer; definir inputs/outputs/model/viewChild. Cubre plantillas completas con OnPush, host bindings, API de señales de Angular v21+.'
argument-hint: 'Describe el componente, directiva, pipe o servicio que necesitas implementar.'
---

# Patrones de Componentes, Directivas, Pipes y Servicios

Esta skill define **cómo se estructura cada artefacto**. Para el diseño del estado reactivo usa `angular-state`; para llamadas HTTP, interceptores y errores, `angular-http`.

## Componentes

```typescript
@Component({
  selector: 'app-item-card',
  changeDetection: ChangeDetectionStrategy.OnPush, // ver regla de OnPush más abajo
  imports: [TranslocoDirective],
  template: `
    <ng-container *transloco="let t; read: 'items'">
      <div class="card">
        <div class="card-body">
          <h5 class="card-title">{{ item().name }}</h5>
          <p class="card-text">{{ item().description }}</p>
          <button type="button" class="btn btn-primary" (click)="onSelect()">
            {{ t('select') }}
          </button>
        </div>
      </div>
    </ng-container>
  `,
})
export class ItemCardComponent {
  // ========== Dependencies ==========
  private readonly analyticsService = inject(AnalyticsService);

  // ========== Inputs ==========
  readonly item = input.required<Item>();
  readonly disabled = input(false, { transform: booleanAttribute });

  // ========== Outputs ==========
  readonly itemSelected = output<Item>();

  // ========== Public methods ==========
  protected onSelect(): void {
    if (!this.disabled()) {
      this.itemSelected.emit(this.item());
    }
  }
}
```

**Reglas**:

- `changeDetection: ChangeDetectionStrategy.OnPush` **siempre** mientras la versión instalada de Angular no lo aplique por defecto. En versiones donde `OnPush` es el valor por defecto, no lo declares salvo que `guidelines/coding-guidelines.md` lo exija.
- No incluir `standalone: true` (es el valor por defecto en Angular v20+).
- Selectores con prefijo `app-` en kebab-case.
- `input()` y `output()` — no `@Input()`/`@Output()`.
- Componentes de página (`loadComponent`): `export default class`.
- Componentes reutilizables: `export class` con nombre.
- Botones siempre con `type` explícito (`type="button"` salvo submit de formulario).
- Estado local: signal `private` escribible + vista `protected readonly` con `asReadonly()`. La plantilla solo lee la vista y llama a métodos `protected` (ver *Estado y visibilidad* en el agente).

## Directivas

```typescript
@Directive({
  selector: '[appHighlight]',
  host: {
    '[class.highlighted]': 'active()',
    '[attr.aria-pressed]': 'active()',
    '(click)': 'onClick()',
    '(keydown.enter)': 'onClick()',
  },
})
export class HighlightDirective {
  // ========== Dependencies ==========
  private readonly el = inject(ElementRef);

  // ========== Inputs ==========
  readonly active = input(false, { transform: booleanAttribute });

  // ========== Public methods ==========
  onClick(): void {
    // lógica
  }
}
```

**Reglas**:

- Propiedad `host` del decorador para todos los bindings y listeners. **Nunca `@HostBinding`/`@HostListener`**.
- Selectores con prefijo `app` en camelCase: `appTooltip`, `appHighlight`.
- Crear una directiva cuando encapsulas comportamiento reutilizable del DOM **sin template propio**. Si necesitas template → componente.
- Si la directiva se aplica sobre un `ng-template`, inyectar `TemplateRef` con `inject(TemplateRef)`.

## Pipes

```typescript
@Pipe({ name: 'appFormatDate', pure: true })
export class FormatDatePipe implements PipeTransform {
  private readonly localeService = inject(LocaleService);

  transform(date: Date | string, format?: string): string {
    const locale = this.localeService.current();
    return formatDate(date, format ?? 'dd/MM/yyyy', locale);
  }
}
```

**Reglas**:

- Sufijo `Pipe` en clase y fichero: `FormatDatePipe`, `format-date.pipe.ts`.
- Prefijo `app` en el nombre para evitar colisiones: `appFormatDate`.
- `pure: true` por defecto. Usar `pure: false` solo si depende de estado externo mutable y se puede justificar.
- Si solo se usa en un componente, considerar `computed()` en su lugar.
- Un pipe que usa `inject()` debe testearse dentro de un contexto de inyección (ver `angular-testing`).

## Servicios

```typescript
@Injectable({ providedIn: 'root' })
export class ItemsService {
  // ========== Dependencies ==========
  private readonly http = inject(HttpClient);

  // ========== State ==========
  private readonly _selectedItem = signal<Item | null>(null);
  readonly selectedItem = this._selectedItem.asReadonly();

  // ========== Computed ==========
  readonly hasSelection = computed(() => this._selectedItem() !== null);

  // ========== HTTP ==========
  getItems(): Observable<Item[]> {
    return this.http.get<Item[]>('/api/items');
  }

  getItem(id: string): Observable<Item> {
    return this.http.get<Item>(`/api/items/${encodeURIComponent(id)}`);
  }

  // ========== Public methods ==========
  selectItem(item: Item): void {
    this._selectedItem.set(item);
  }

  clearSelection(): void {
    this._selectedItem.set(null);
  }
}
```

**Reglas**:

- `@Injectable({ providedIn: 'root' })` para singletons. Justificar explícitamente cualquier otro `providedIn` o provider a nivel de componente/ruta.
- Sufijo `-service` en fichero: `items-service.ts`.
- Estado interno: signals privadas mutables, expuestas en solo lectura con `asReadonly()`. Los cambios solo se hacen a través de métodos del servicio.
- Los métodos HTTP devuelven `Observable<T>`. La conversión a señal la hace el componente (ver `angular-http` y `angular-state`).
- Una única responsabilidad por servicio (ver `angular-solid`).

## Interfaces y Tipos

```typescript
// interfaces/items/index.ts
export interface Item {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly status: ItemStatus;
}

export type ItemStatus = 'active' | 'inactive' | 'pending';

// Para listados vs detalle (Interface Segregation)
export interface ItemSummary {
  readonly id: string;
  readonly name: string;
}
```

**Reglas**:

- Declarar en `interfaces/` organizado por dominio (o donde indiquen las guidelines).
- Sin prefijo `I`: `User`, no `IUser`.
- `interface` para objetos; `type` para uniones, intersecciones y alias de primitivos.
- `readonly` en propiedades que no deban mutarse.
- Definir siempre la interfaz para respuestas de API conocidas; no usar `unknown` u `object` para respuestas cuyo contrato se conoce.
- Exportar desde barrel `interfaces/<dominio>/index.ts`.
- En un monorepo con backend, los contratos de la API viven en una librería compartida de solo tipos (ver `angular-monorepo`).

## Tokens de Inyección

```typescript
// tokens/api-base-url-token.ts
export const API_BASE_URL = new InjectionToken<string>('API_BASE_URL');

// Proporcionar en app.config.ts
{
  provide: API_BASE_URL,
  useValue: environment.apiBaseUrl,
}
```

Usar `InjectionToken` para valores de configuración y cuando exista una abstracción con más de una implementación real (ver `angular-solid`). No crear tokens para servicios que solo tendrán una implementación.

## Inicializadores de Aplicación

```typescript
export const authInitializer = provideAppInitializer((): Promise<boolean> => {
  const authService = inject(AuthService);
  return firstValueFrom(authService.checkAuthStatus());
});
```

**Reglas**:

- `provideAppInitializer()` para tareas previas al primer render.
- Simples y rápidos; delegar la lógica en servicios.
- Si puede fallar de forma recuperable, capturar el error internamente para no bloquear el arranque de la aplicación.
- Con SSR, el inicializador también se ejecuta en el servidor en cada petición: no hagas en él trabajo que solo tenga sentido en el navegador (ver `angular-ssr`).

## API de Inputs, Outputs, Model y Queries

```typescript
// input() — solo lectura
readonly id = input.required<string>();
readonly label = input('Sin etiqueta');
readonly disabled = input(false, { transform: booleanAttribute });

// output() — sin prefijo "on", verbo en pasado
readonly itemSelected = output<Item>();
readonly formSubmitted = output<FormData>();

// model() — two-way binding genuino
readonly value = model<string>('');
readonly isOpen = model(false);

// viewChild / viewChildren
readonly listRef = viewChild.required<ElementRef>('list');
readonly items = viewChildren<ItemComponent>('items');

// contentChild / contentChildren
readonly header = contentChild<HeaderComponent>(HeaderComponent);
```

## Lifecycle Hooks en Zoneless

- **`ngAfterViewInit`/`ngAfterContentInit`**: usar `afterNextRender()` para código que necesita el DOM.
- **`afterEveryRender()`** (antes `afterRender()`, según versión): solo para sincronizar con el DOM en cada ciclo. Preferir `afterNextRender()`.
- **`ngOnDestroy`**: preferir `takeUntilDestroyed()` con `DestroyRef`.
- **`ngOnChanges`**: **evitar** con `input()`. Los inputs son señales; usar `computed()` o `effect()`.
- `afterNextRender()` necesita contexto de inyección: como campo de clase o en el constructor. Fuera de él (por ejemplo dentro de un `effect()` o un método), pasar `{ injector }`.
- `afterNextRender()` solo se ejecuta en el navegador: es el sitio correcto para código que usa el DOM real en aplicaciones con SSR.

```typescript
// ✅ Usar afterNextRender() en lugar de ngAfterViewInit
readonly chartInit = afterNextRender(() => {
  this.chart = chartLib.init(this.chartRef().nativeElement);
});

// ✅ DestroyRef en lugar de ngOnDestroy
private readonly destroyRef = inject(DestroyRef);
```
