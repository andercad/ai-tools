---
name: angular-forms
description: 'Frontend Angular. Formularios reactivos Angular con FormBuilder, validación y envío. Usar cuando: crear formularios (registro, login, alta, edición), añadir validación a campos, validación cruzada entre campos (contraseña y confirmación, fechas desde/hasta), validadores asíncronos contra la API, gestionar estado de envío, mostrar errores de validación o del backend, manejar valueChanges, decidir entre Reactive Forms y Signal Forms. Cubre nonNullable.group, validators, mensajes de error con Transloco, estado submitting, reset post-envío.'
argument-hint: 'Describe el formulario que necesitas implementar (campos, validaciones, acción de envío).'
---

# Formularios Reactivos

Usar **Reactive Forms** por defecto. No usar Template-driven Forms.

**Signal Forms** (`@angular/forms/signals`): experimentales en Angular 21, estables desde Angular 22. Úsalos solo si la versión instalada es 22+ **y** las guidelines los adoptan; en ese caso consulta la guía oficial de la versión, porque la API cambió durante su fase experimental. En proyectos con Reactive Forms existentes, no mezcles ambos modelos en la misma pantalla sin una estrategia de migración.

La validación en cliente es **experiencia de usuario**. El backend valida siempre de nuevo: nunca trates la validación del formulario como control de seguridad.

## Declaración del formulario

Usar `inject(FormBuilder)` y `fb.nonNullable.group()` para evitar `| null` innecesario:

```typescript
@Component({ ... })
export class UserFormComponent {
  // ========== Dependencies ==========
  private readonly fb = inject(FormBuilder);
  private readonly usersService = inject(UsersService);
  private readonly notificationService = inject(NotificationService);
  private readonly destroyRef = inject(DestroyRef);

  // ========== State ==========
  private readonly _submitting = signal(false);
  protected readonly submitting = this._submitting.asReadonly();

  // ========== Form ==========
  protected readonly form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    phone: ['', [Validators.pattern(/^\+?[0-9]{9,15}$/)]],
    role: ['viewer' as UserRole, Validators.required],
  });

  // ========== Computed ==========
  protected readonly formValues = toSignal(this.form.valueChanges, {
    initialValue: this.form.getRawValue(),
  });

  // ========== Public methods ==========
  protected onSubmit(): void {
    this.form.markAllAsTouched();

    if (this.form.invalid || this.submitting()) {
      return;
    }

    this._submitting.set(true);
    const data = this.form.getRawValue();

    this.usersService
      .createUser(data)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: () => {
          this.form.reset();
          this._submitting.set(false);
          this.notificationService.success('users.create-success');
        },
        error: (error: HttpErrorResponse) => {
          this.applyServerErrors(error);
          this._submitting.set(false);
        },
      });
  }

  // ========== Private methods ==========
  /** Traslada al formulario los errores de validación devueltos por el backend (si el contrato los incluye). */
  private applyServerErrors(error: HttpErrorResponse): void {
    if (error.status !== 400 && error.status !== 422) {
      return; // otros errores los gestiona el interceptor / notificación global
    }
    const fieldErrors = (error.error as { fieldErrors?: Record<string, string> } | null)?.fieldErrors;
    for (const [field, code] of Object.entries(fieldErrors ?? {})) {
      const control = this.form.get(field);
      control?.setErrors({ ...(control.errors ?? {}), server: code });
    }
  }
}
```

El `FormGroup` es `protected readonly` sin envoltura: es mutable por diseño y lo modifican las directivas `formControlName`. La regla de signal privada + `asReadonly()` aplica al resto del estado del componente (`submitting`).

Adapta `applyServerErrors` al contrato de errores real del backend (ver `guidelines/coding-guidelines.md`). Si el backend no devuelve errores por campo, omítelo.

## Template del formulario

```html
<ng-container *transloco="let t; read: 'users.form'">
  <form [formGroup]="form" (ngSubmit)="onSubmit()" novalidate>
    <!-- Campo con validación -->
    <div class="mb-3">
      <label for="name" class="form-label">
        {{ t('name-label') }} <span class="text-danger" aria-hidden="true">*</span>
      </label>
      <input
        id="name"
        type="text"
        class="form-control"
        [class.is-invalid]="form.controls.name.invalid && form.controls.name.touched"
        formControlName="name"
        [attr.aria-describedby]="form.controls.name.invalid && form.controls.name.touched ? 'name-error' : null"
        [attr.aria-invalid]="form.controls.name.invalid && form.controls.name.touched ? 'true' : null"
        [attr.aria-required]="'true'"
      />
      @if (form.controls.name.invalid && form.controls.name.touched) {
      <div id="name-error" class="invalid-feedback" role="alert">
        @if (form.controls.name.errors?.['required']) {
          {{ t('errors.name-required') }}
        } @else if (form.controls.name.errors?.['minlength']) {
          {{ t('errors.name-min-length', { min: 2 }) }}
        } @else if (form.controls.name.errors?.['server']) {
          {{ t('errors.' + form.controls.name.errors?.['server']) }}
        }
      </div>
      }
    </div>

    <!-- Botón de envío -->
    <button
      type="submit"
      class="btn btn-primary"
      [disabled]="submitting()"
      [attr.aria-busy]="submitting() ? 'true' : null"
    >
      @if (submitting()) {
      <span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
      }
      {{ t(submitting() ? 'submitting' : 'submit') }}
    </button>
  </form>
</ng-container>
```

## Validadores personalizados

Definir en `utils/` con tipado estricto:

```typescript
// utils/shared/validators.ts
export function noWhitespaceValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const value = control.value as string;
    const hasWhitespace = value && value.trim().length !== value.length;
    return hasWhitespace ? { noWhitespace: true } : null;
  };
}
```

### Validación cruzada entre campos

Un validador de grupo **devuelve el error en el grupo**. No llames a `setErrors()` sobre los controles hijos: `setErrors(null)` borra también los errores de otros validadores del control (por ejemplo `required`).

```typescript
export function matchFieldsValidator(
  controlName: string,
  matchingControlName: string,
): ValidatorFn {
  return (group: AbstractControl): ValidationErrors | null => {
    const control = group.get(controlName);
    const matching = group.get(matchingControlName);

    if (!control || !matching) return null;

    return control.value === matching.value ? null : { fieldsMismatch: true };
  };
}

// Registro en el grupo
readonly form = this.fb.nonNullable.group(
  {
    password: ['', Validators.required],
    confirmPassword: ['', Validators.required],
  },
  { validators: matchFieldsValidator('password', 'confirmPassword') },
);
```

```html
<!-- Mostrar el error de grupo junto al campo de confirmación -->
@if (form.errors?.['fieldsMismatch'] && form.controls.confirmPassword.touched) {
<div id="confirm-error" class="invalid-feedback d-block" role="alert">
  {{ t('errors.fields-mismatch') }}
</div>
}
```

## Validadores asíncronos

El retardo debe aplicarse **antes** de llamar al backend. Un `debounceTime` colocado después de la llamada HTTP no evita la petición. Angular cancela la ejecución anterior cuando el valor cambia, así que `timer()` + `switchMap()` hace de debounce real:

```typescript
export function uniqueEmailValidator(usersService: UsersService): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> =>
    timer(300).pipe(
      switchMap(() => usersService.checkEmailExists(control.value as string)),
      map((exists) => (exists ? { emailTaken: true } : null)),
      // Decisión explícita ante fallo remoto: aquí NO se bloquea el envío,
      // porque el backend volverá a validar la unicidad al crear.
      // Si el negocio exige bloquear, devolver { validationUnavailable: true }.
      catchError(() => of(null)),
      take(1),
    );
}

// Registro: updateOn 'blur' reduce aún más las llamadas
email: this.fb.nonNullable.control('', {
  validators: [Validators.required, Validators.email],
  asyncValidators: [uniqueEmailValidator(this.usersService)],
  updateOn: 'blur',
}),
```

## Reglas de validación y UX

- Mostrar errores: `control.invalid && control.touched`.
- Mensajes con **claves de traducción**. Nunca hardcodear mensajes.
- `form.markAllAsTouched()` antes de validar al enviar.
- Señal `submitting` (privada + `asReadonly()`) para el estado de carga. Deshabilitar el botón durante el envío.
- `form.reset()` tras envío exitoso si corresponde.
- **No hacer `subscribe()` en `form.valueChanges`** sin limpieza; usar `toSignal(form.valueChanges)` o `takeUntilDestroyed()`.
- Los mensajes de error deben ser accesibles: `role="alert"` y `aria-describedby` enlazando campo con error.
- Tras un envío fallido por validación, mover el foco al primer campo inválido.
- Los errores devueltos por el backend se muestran en el campo correspondiente cuando el contrato lo permite.
