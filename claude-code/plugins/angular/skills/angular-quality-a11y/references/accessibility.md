
# Accesibilidad

Cumplir WCAG 2.2 nivel AA como base, o el nivel definido en el `CLAUDE.md` del proyecto (`a11y:`). Todo el código debe superar las comprobaciones de **AXE** y las reglas de `angular-eslint/template-accessibility`.

Principio base: **HTML nativo antes que ARIA**. Un `<button>` o `<a>` reales son preferibles a un `<div>` con `role` y listeners. ARIA complementa la semántica, no la sustituye.

## Checklist de verificación

- [ ] Todos los elementos interactivos tienen etiqueta accesible (`aria-label`, `aria-labelledby` o `<label>`)
- [ ] Las imágenes informativas tienen `alt`. Las decorativas tienen `alt=""`
- [ ] Contraste de color mínimo: 4.5:1 para texto normal, 3:1 para texto grande (≥18px o ≥14px bold)
- [ ] La navegación completa es posible solo con teclado (Tab, Shift+Tab, Enter, Space, Escape, flechas)
- [ ] El foco es siempre visible y tiene contraste suficiente
- [ ] Los modales y paneles atrapan el foco y lo restauran al cerrarse
- [ ] Los mensajes de error de formulario están enlazados con `aria-describedby`
- [ ] Las regiones dinámicas usan `aria-live` cuando corresponde
- [ ] La estructura de encabezados (`h1`-`h6`) es semántica y no salta niveles
- [ ] La información no se transmite solo por color
- [ ] No hay roles ARIA redundantes con la semántica nativa (ej. `role="button"` en un `<button>`)

## Atributos ARIA esenciales

```html
<!-- Botón con icono solo — siempre necesita aria-label -->
<button type="button" [attr.aria-label]="'common.close' | transloco">
  <i class="bi bi-x" aria-hidden="true"></i>
</button>

<!-- Estado expandible -->
<button type="button" [attr.aria-expanded]="isOpen()" [attr.aria-controls]="'panel-' + id()">
  {{ t('toggle') }}
</button>
<div [id]="'panel-' + id()" [hidden]="!isOpen()">...</div>

<!-- Elemento de carga -->
<div role="status" aria-live="polite" [attr.aria-busy]="loading()">
  @if (loading()) {
  <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
  <span class="visually-hidden">{{ t('loading') }}</span>
  }
</div>

<!-- Tabla de datos -->
<table [attr.aria-label]="t('table-label')">
  <caption class="visually-hidden">
    {{ t('table-description') }}
  </caption>
  <thead>
    <tr>
      <th scope="col">{{ t('name') }}</th>
      <th scope="col">{{ t('status') }}</th>
    </tr>
  </thead>
  <tbody>
    @for (item of items(); track item.id) {
    <tr>
      <td>{{ item.name }}</td>
      <td>
        <span
          class="badge"
          [class.bg-success]="item.status === 'active'"
          [class.bg-secondary]="item.status !== 'active'"
        >
          {{ t('status.' + item.status) }}
        </span>
      </td>
    </tr>
    }
  </tbody>
</table>

<!-- Barra de progreso -->
<div
  role="progressbar"
  [attr.aria-valuenow]="progress()"
  aria-valuemin="0"
  aria-valuemax="100"
  [attr.aria-label]="t('progress-label')"
>
  <div class="progress-bar" [style.width.%]="progress()"></div>
</div>
```

## Formularios accesibles

```html
<ng-container *transloco="let t; read: 'form'">
  <div class="mb-3">
    <!-- label SIEMPRE asociado con for/id -->
    <label for="customer-name" class="form-label">
      {{ t('customer-name') }}
      <span class="text-danger" aria-hidden="true">*</span>
    </label>
    <input
      id="customer-name"
      type="text"
      class="form-control"
      [class.is-invalid]="nameCtrl.invalid && nameCtrl.touched"
      formControlName="name"
      [attr.aria-required]="'true'"
      [attr.aria-invalid]="nameCtrl.invalid && nameCtrl.touched ? 'true' : null"
      [attr.aria-describedby]="nameCtrl.invalid && nameCtrl.touched ? 'name-error' : 'name-hint'"
    />
    <div id="name-hint" class="form-text">{{ t('name-hint') }}</div>
    @if (nameCtrl.invalid && nameCtrl.touched) {
    <div id="name-error" class="invalid-feedback" role="alert">{{ t('errors.name-required') }}</div>
    }
  </div>
</ng-container>
```

Si el formulario tiene `id` fijos y el componente puede instanciarse varias veces en la misma página, genera `id` únicos por instancia (por ejemplo, con un contador o un input `id`) para no romper la asociación `label`/`aria-describedby`.

## Gestión de foco

`afterNextRender()` necesita contexto de inyección. Dentro de un `effect()` no lo hay, por lo que hay que pasar el `Injector` explícitamente:

```typescript
@Component({ ... })
export class ModalComponent {
  // ========== Dependencies ==========
  private readonly el = inject(ElementRef<HTMLElement>);
  private readonly injector = inject(Injector);

  // ========== Inputs ==========
  readonly isOpen = model(false);

  // ========== Effects ==========
  private readonly focusEffect = effect(() => {
    if (this.isOpen()) {
      // Esperar al renderizado antes de mover el foco
      afterNextRender(
        () => {
          const firstFocusable = this.el.nativeElement.querySelector<HTMLElement>(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
          );
          firstFocusable?.focus();
        },
        { injector: this.injector },
      );
    }
  });
}
```

Al cerrar un modal o panel, **devuelve el foco** al elemento que lo abrió (guarda la referencia `document.activeElement` antes de abrir).

## Angular CDK a11y

Para gestión de foco compleja (modales, paneles laterales, trampas de foco):

```typescript
import { FocusTrap, FocusTrapFactory, LiveAnnouncer } from '@angular/cdk/a11y';

@Component({ ... })
export class DialogComponent implements OnDestroy {
  // ========== Dependencies ==========
  private readonly focusTrapFactory = inject(FocusTrapFactory);
  private readonly liveAnnouncer = inject(LiveAnnouncer);
  private readonly transloco = inject(TranslocoService);
  private readonly el = inject(ElementRef<HTMLElement>);
  private readonly injector = inject(Injector);

  // ========== Inputs ==========
  readonly isOpen = model(false);

  // ========== Effects ==========
  private readonly openEffect = effect(() => {
    if (this.isOpen()) {
      this.previouslyFocused = document.activeElement as HTMLElement | null;
      afterNextRender(
        () => {
          this.focusTrap = this.focusTrapFactory.create(this.el.nativeElement);
          this.focusTrap.focusInitialElementWhenReady();
          // Anunciar a lectores de pantalla
          this.liveAnnouncer.announce(this.transloco.translate('dialog.opened'));
        },
        { injector: this.injector },
      );
    } else {
      this.focusTrap?.destroy();
      this.focusTrap = undefined;
      this.previouslyFocused?.focus();
    }
  });

  // ========== Properties ==========
  private focusTrap?: FocusTrap;
  private previouslyFocused: HTMLElement | null = null;

  // ========== Lifecycle ==========
  ngOnDestroy(): void {
    this.focusTrap?.destroy();
  }
}
```

## Bootstrap 5 — consideraciones de accesibilidad

Aplica esta sección cuando el proyecto use Bootstrap (ver el `CLAUDE.md` del proyecto).

- **Modales Bootstrap**: usar `data-bs-dismiss` solo si se usan los modales JS de Bootstrap; en Angular preferir componentes propios con CDK.
- **Dropdowns**: el trigger debe tener `aria-expanded` y `aria-haspopup="listbox"` o `"menu"`. Si el estado lo gestiona el JS de Bootstrap, no dupliques `aria-expanded` con una signal que no se sincroniza.
- **Alerts/Toasts**: añadir `role="alert"` o `role="status"` según urgencia.
- **Spinners**: siempre `aria-hidden="true"` en el elemento visual + texto `visually-hidden`.
- **Cards clicables**: si toda la card es clicable, usar `<a>` o `<button>` como wrapper, no `(click)` en `<div>`.
- **Badges de estado**: no transmitir información solo por color; añadir texto o `aria-label`.

```html
<!-- ✅ Toast accesible -->
<div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
  <div class="toast-body">{{ message }}</div>
</div>

<!-- ✅ Spinner con texto para lectores -->
<div class="d-flex align-items-center gap-2">
  <div class="spinner-border spinner-border-sm" aria-hidden="true"></div>
  <span class="visually-hidden">{{ 'common.loading' | transloco }}</span>
</div>
```

## Navegación por teclado — patrones comunes

| Patrón              | Teclas esperadas                                                 |
| ------------------- | ---------------------------------------------------------------- |
| Modal               | Tab/Shift+Tab dentro del modal, Escape para cerrar               |
| Dropdown menu       | Enter/Space para abrir, flechas para navegar, Escape para cerrar |
| Tabs (pestañas)     | Tab para llegar, flechas izquierda/derecha para cambiar tab      |
| Lista seleccionable | Flechas para navegar, Home/End, Enter/Space para seleccionar     |
| Accordion           | Enter/Space para expandir/colapsar                               |
| Combobox (autocompletado) | Escribir filtra; flechas recorren sugerencias; Enter selecciona; Escape cierra |

Para un autocompletado, el foco permanece en el `<input role="combobox">` con `aria-autocomplete="list"`, `aria-expanded`, `aria-controls` apuntando al `listbox` y `aria-activedescendant` con la opción activa. Anuncia el número de resultados con una región `aria-live="polite"`.

Sigue el patrón correspondiente de WAI-ARIA Authoring Practices. Si existe un componente del CDK o de la librería del proyecto que ya lo implementa, úsalo antes de crear uno propio.

```typescript
// Gestión de teclado para lista seleccionable
@Component({
  selector: 'app-selectable-list',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    role: 'listbox',
    tabindex: '0',
    '(keydown)': 'onKeydown($event)',
    '[attr.aria-activedescendant]': 'activeId()',
  },
  templateUrl: './selectable-list.html', // ver el .html tras la clase
})
export class SelectableListComponent {
  // ========== Inputs ==========
  readonly items = input.required<Item[]>();

  // ========== Outputs ==========
  readonly itemSelected = output<Item>();

  // ========== State ==========
  private readonly _activeIndex = signal(0);
  protected readonly activeIndex = this._activeIndex.asReadonly();

  // ========== Computed ==========
  protected readonly activeId = computed(() => {
    const item = this.items()[this.activeIndex()];
    return item ? `item-${item.id}` : null;
  });

  // ========== Public methods ==========
  protected onKeydown(event: KeyboardEvent): void {
    const lastIndex = this.items().length - 1;
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this._activeIndex.update((i) => Math.min(i + 1, lastIndex));
        break;
      case 'ArrowUp':
        event.preventDefault();
        this._activeIndex.update((i) => Math.max(i - 1, 0));
        break;
      case 'Home':
        event.preventDefault();
        this._activeIndex.set(0);
        break;
      case 'End':
        event.preventDefault();
        this._activeIndex.set(lastIndex);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        this.itemSelected.emit(this.items()[this.activeIndex()]);
        break;
    }
  }
}
```

```html
<!-- selectable-list.html -->
@for (item of items(); track item.id; let i = $index) {
  <div
    role="option"
    [id]="'item-' + item.id"
    [attr.aria-selected]="i === activeIndex()"
  >
    {{ item.name }}
  </div>
}
```

## Verificación

- Ejecutar `ng lint` con las reglas `template-accessibility` activas.
- Revisar con AXE (extensión del navegador o integración en tests E2E).
- Revisión manual mínima: recorrer la funcionalidad solo con teclado y comprobar el foco visible.
