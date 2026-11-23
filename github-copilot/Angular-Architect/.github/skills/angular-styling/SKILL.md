---
name: angular-styling
description: 'Frontend Angular. Diseño y estilos Angular con el framework CSS del proyecto (por defecto Bootstrap 5, Bootstrap Icons y Sass). Usar cuando: crear estilos para componentes, usar el sistema de grid, aplicar clases de utilidad, usar iconos, personalizar variables CSS/Sass, crear temas o estilos globales, implementar diseño responsive, usar componentes del framework (card, badge, modal, toast, spinner, dropdown).'
argument-hint: 'Describe el componente o patrón visual que necesitas estilizar.'
---

# Diseño y Estilos

Ver `guidelines/coding-guidelines.md` → _Librería de diseño_ para el framework CSS, librería de iconos, colores de marca y componentes habitualmente usados en el proyecto. Los ejemplos de esta skill usan **Bootstrap 5 + Bootstrap Icons + Sass**; si el proyecto usa otro framework, aplica los mismos principios con sus clases y tokens.

## Principio fundamental

**Usar las clases del framework de diseño del proyecto antes de escribir CSS personalizado.** Solo añadir CSS custom cuando las clases del framework no cubran la necesidad.

## Bootstrap 5 — Utilidades y Grid

```html
<!-- Grid responsive -->
<div class="row g-3">
  <div class="col-12 col-md-6 col-xl-4">
    <!-- contenido -->
  </div>
</div>

<!-- Spacing: m-*, p-*, gap-* -->
<div class="d-flex flex-column gap-3 p-4">
  <div class="mb-2">...</div>
</div>

<!-- Texto -->
<p class="text-muted small">Información secundaria</p>
<h5 class="fw-semibold">Título con peso semibold</h5>

<!-- Display y Flex -->
<div class="d-flex align-items-center justify-content-between">
  <span class="text-truncate">Texto largo...</span>
  <button type="button" class="btn btn-sm btn-outline-secondary flex-shrink-0">Acción</button>
</div>
```

## Componentes Bootstrap habituales

### Card — Tarjetas de widgets

```html
<div class="card h-100">
  <div class="card-header d-flex align-items-center justify-content-between">
    <h6 class="card-title mb-0">{{ t('widget-title') }}</h6>
    <span class="badge bg-primary">{{ count() }}</span>
  </div>
  <div class="card-body overflow-auto">
    <!-- contenido -->
  </div>
  <div class="card-footer text-muted small">{{ t('last-updated', { date: lastUpdate() }) }}</div>
</div>
```

### Badge — Indicadores de estado

```html
<!-- ✅ Con texto + color: accesible -->
<span class="badge rounded-pill bg-success">{{ t('status.active') }}</span>
<span class="badge rounded-pill bg-warning text-dark">{{ t('status.pending') }}</span>
<span class="badge rounded-pill bg-danger">{{ t('status.critical') }}</span>
<span class="badge rounded-pill bg-secondary">{{ t('status.inactive') }}</span>

<!-- ✅ Estado dinámico -->
<span
  class="badge rounded-pill"
  [class.bg-success]="item().status === 'active'"
  [class.bg-warning]="item().status === 'pending'"
  [class.bg-danger]="item().status === 'critical'"
  [class.text-dark]="item().status === 'pending'"
>
  {{ t('status.' + item().status) }}
</span>
```

### Toast — Notificaciones (via NotificationService)

```html
<!-- Usar el servicio de notificaciones del proyecto, no implementar toasts directamente -->
<!-- El servicio gestiona el stack de toasts con el framework CSS -->
```

### Spinner — Estados de carga

```html
<!-- Spinner inline en botón -->
<button type="button" class="btn btn-primary" [disabled]="loading()">
  @if (loading()) {
  <span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
  }
  {{ t(loading() ? 'saving' : 'save') }}
</button>

<!-- Spinner de página completa -->
@if (pageLoading()) {
<div class="d-flex justify-content-center align-items-center py-5">
  <div class="spinner-border text-primary" role="status">
    <span class="visually-hidden">{{ 'common.loading' | transloco }}</span>
  </div>
</div>
}
```

### Dropdown — Menús de acción

Si se usa el JavaScript de Bootstrap (`data-bs-toggle`), Bootstrap gestiona `aria-expanded` por sí mismo: no lo enlaces a una signal que no se actualiza. Si el dropdown lo controla Angular (sin el JS de Bootstrap), gestiona tú el estado en la clase y la plantilla solo llama a métodos:

```html
<!-- Dropdown controlado por Angular -->
<div class="dropdown">
  <button
    class="btn btn-outline-secondary btn-sm dropdown-toggle"
    type="button"
    aria-haspopup="menu"
    [attr.aria-expanded]="dropdownOpen()"
    (click)="toggleDropdown()"
  >
    <i class="bi bi-three-dots-vertical" aria-hidden="true"></i>
    <span class="visually-hidden">{{ t('actions') }}</span>
  </button>
  <ul class="dropdown-menu dropdown-menu-end" [class.show]="dropdownOpen()" role="menu">
    <li>
      <button class="dropdown-item" type="button" role="menuitem" (click)="onEdit()">
        <i class="bi bi-pencil me-2" aria-hidden="true"></i>
        {{ t('edit') }}
      </button>
    </li>
    <li><hr class="dropdown-divider" /></li>
    <li>
      <button class="dropdown-item text-danger" type="button" role="menuitem" (click)="onDelete()">
        <i class="bi bi-trash me-2" aria-hidden="true"></i>
        {{ t('delete') }}
      </button>
    </li>
  </ul>
</div>
```

```typescript
// ========== State ==========
private readonly _dropdownOpen = signal(false);
protected readonly dropdownOpen = this._dropdownOpen.asReadonly();

// ========== Public methods ==========
protected toggleDropdown(): void {
  this._dropdownOpen.update((open) => !open);
}
```

Para menús complejos (navegación con flechas, cierre al hacer clic fuera, Escape), preferir CDK Menu o el componente del proyecto (ver `angular-accessibility`).

## Bootstrap Icons

```html
<!-- Usar solo la librería de iconos definida en las guidelines (por defecto Bootstrap Icons: bi bi-*) -->

<!-- Icono decorativo — aria-hidden siempre -->
<i class="bi bi-heart-pulse text-danger" aria-hidden="true"></i>

<!-- Icono con significado — añadir texto para lectores -->
<i class="bi bi-check-circle-fill text-success" aria-hidden="true"></i>
<span class="visually-hidden">{{ t('validated') }}</span>

<!-- Icono en botón solo -->
<button type="button" [attr.aria-label]="t('refresh')">
  <i class="bi bi-arrow-clockwise" aria-hidden="true"></i>
</button>

<!-- Tamaños: fs-1 (mayor) a fs-6 (menor) o font-size personalizado -->
<i class="bi bi-person fs-3" aria-hidden="true"></i>
```

## Sass — Estilos de componente

```scss
// item-card.component.scss

// Para usar variables y mixins de Bootstrap en un componente hay que importarlos
// (funciones, variables y mixins), sin volver a importar todo Bootstrap.
// La forma exacta depende de la versión de Bootstrap/Sass del proyecto.

// ✅ Usar variables CSS de Bootstrap (no requieren import Sass)
:host {
  --card-min-height: 200px;
}

.widget-card {
  min-height: var(--card-min-height);
  border-radius: var(--bs-border-radius-lg);
  box-shadow: var(--bs-box-shadow-sm);

  // ✅ Usar breakpoints de Bootstrap (requiere los mixins importados)
  @include media-breakpoint-up(md) {
    min-height: calc(var(--card-min-height) * 1.5);
  }
}

// ✅ Usar colores del tema
.status-indicator {
  color: var(--bs-success);

  &.is-warning {
    color: var(--bs-warning);
  }

  &.is-danger {
    color: var(--bs-danger);
  }
}
```

Preferir las **variables CSS** (`var(--bs-*)`) en componentes: funcionan con temas en runtime (incluido modo oscuro) y no obligan a importar Sass de Bootstrap en cada componente.

**Reglas de estilos**:

- Estilos **encapsulados** por componente (view encapsulation por defecto Angular).
- No generar estilos globales salvo en `styles.scss` con justificación.
- **No usar `!important`**; resolver conflictos de especificidad con encapsulación o selectores más específicos.
- No usar `ngClass` ni `ngStyle` → usar `[class.*]` y `[style.*]` o bindings de clase directos.
- No transmitir información solo por color (ver `angular-accessibility`).
- En librerías de componentes, exponer la personalización mediante variables CSS propias (ver `angular-library`).
- En un monorepo, el tema y las variables comunes viven en una librería compartida y cada aplicación importa lo que necesita; no copies estilos globales entre aplicaciones (ver `angular-monorepo`).

## Responsive design

```html
<!-- Ocultar en móvil -->
<div class="d-none d-md-block">Solo desktop</div>

<!-- Stack en móvil, row en desktop -->
<div class="d-flex flex-column flex-md-row gap-3">
  <div class="flex-md-grow-1">...</div>
  <div class="flex-shrink-0">...</div>
</div>

<!-- Texto responsive: Bootstrap 5 escala los títulos automáticamente (RFS) -->
<h1 class="fs-4">Título</h1>
```

Comprueba también el comportamiento con zoom del navegador al 200 % y con anchos de 320 px.

## Estilos globales — `styles.scss`

Solo para:

- Importar Bootstrap y su configuración custom
- Variables Sass globales del proyecto
- Reset o normalización que no puede encapsularse
- Estilos de utilidad muy reutilizados que el framework no cubre

```scss
// styles.scss
// Personalizar Bootstrap ANTES de importarlo.
// Los valores de marca (colores, tipografía) se toman de guidelines/coding-guidelines.md.
$primary: #0d6efd; // ← sustituir por el color de marca del proyecto
$font-family-sans-serif: 'Roboto', sans-serif; // ← tipografía del proyecto

@import 'bootstrap/scss/bootstrap';
@import 'bootstrap-icons/font/bootstrap-icons';
```

Dart Sass marca `@import` como deprecado. Bootstrap 5 todavía se distribuye pensado para `@import`; mantén el mecanismo que use el proyecto y no migres a `@use` sin comprobar la compatibilidad con la versión de Bootstrap instalada.
