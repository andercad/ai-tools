---
name: angular-testing
description: 'Frontend Angular. Tests unitarios Angular con Vitest (o Jest) y TestBed. Usar cuando: crear tests para componentes, servicios, guards, pipes o utilidades; alcanzar la cobertura exigida; mockear dependencias con TestBed; testear signals y observables; testear formularios reactivos. Cubre estructura describe/it, TestBed.configureTestingModule, mocks de servicios, ComponentFixture, cobertura de branches.'
argument-hint: 'Describe qué necesitas testear: componente, servicio, guard, pipe o utilidad.'
---

# Tests Unitarios con Vitest y TestBed

El proyecto usa **Vitest** como framework de tests con **TestBed** de Angular para tests de componentes y servicios. Comprueba en `package.json` y en la configuración de test cuál es el runner real: si es Jest, usa la API de Jest (`jest.fn`, `jest.Mocked`) de forma coherente. **Nunca mezcles APIs de Vitest y Jest en el mismo fichero.**

En un monorepo, el runner puede configurarse por proyecto: comprueba el del proyecto en el que trabajas (`angular.json` o su `project.json`).

Estrategia: usa la prueba de menor alcance que demuestre el comportamiento (función pura → servicio → componente → integración). Prueba **comportamiento observable** (lo que se renderiza, lo que se emite, lo que se llama), no detalles internos de implementación. Con el estado en signals privadas, el test actúa igual que el usuario: dispara el evento o llama al método y comprueba el resultado.

## Mocks tipados sin `any`

La restricción "no `any`" aplica también a los tests. Para mocks parciales:

```typescript
import { vi, type Mocked } from 'vitest';

// Mock parcial tipado: se declara solo lo que el test usa
const itemsServiceMock = {
  selectedItem: signal<Item | null>(null),
  hasSelection: signal(false),
  selectItem: vi.fn(),
  clearSelection: vi.fn(),
} satisfies Partial<ItemsService>;

// Cuando hay que pasar un objeto que la API tipa como el servicio completo,
// convertir explícitamente desde unknown (nunca as any):
const asService = itemsServiceMock as unknown as ItemsService;
```

## Estructura base de un test

```typescript
// item-card.component.spec.ts
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { vi } from 'vitest';
import { ItemCardComponent } from './item-card.component';
import { ItemsService } from '@services/.';
// Importar desde el paquete de Transloco instalado (@jsverse/transloco o @ngneat/transloco)
import { TranslocoTestingModule } from '@jsverse/transloco';

describe('ItemCardComponent', () => {
  let component: ItemCardComponent;
  let fixture: ComponentFixture<ItemCardComponent>;

  const itemsServiceMock = {
    selectedItem: signal<Item | null>(null),
    hasSelection: signal(false),
    selectItem: vi.fn(),
    clearSelection: vi.fn(),
  } satisfies Partial<ItemsService>;

  const item: Item = { id: '1', name: 'Test Item', description: '', status: 'active' };

  beforeEach(async () => {
    vi.clearAllMocks();

    await TestBed.configureTestingModule({
      imports: [ItemCardComponent, TranslocoTestingModule.forRoot({ langs: { es: {} } })],
      providers: [{ provide: ItemsService, useValue: itemsServiceMock }],
    }).compileComponents();

    fixture = TestBed.createComponent(ItemCardComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('item', item);
  });

  describe('initialization', () => {
    it('should create', () => {
      fixture.detectChanges();
      expect(component).toBeTruthy();
    });
  });

  describe('item display', () => {
    it('should render item name', () => {
      fixture.detectChanges();

      const nameEl: HTMLElement = fixture.nativeElement.querySelector('.card-title');
      expect(nameEl.textContent).toContain('Test Item');
    });
  });

  describe('interaction', () => {
    it('should emit itemSelected when clicking the button', () => {
      fixture.detectChanges();

      const emitSpy = vi.spyOn(component.itemSelected, 'emit');
      const button: HTMLButtonElement = fixture.nativeElement.querySelector('button');
      button.click();

      expect(emitSpy).toHaveBeenCalledWith(item);
    });

    it('should not emit when disabled', () => {
      fixture.componentRef.setInput('disabled', true);
      fixture.detectChanges();

      const emitSpy = vi.spyOn(component.itemSelected, 'emit');
      const button: HTMLButtonElement = fixture.nativeElement.querySelector('button');
      button.click();

      expect(emitSpy).not.toHaveBeenCalled();
    });
  });
});
```

En aplicaciones zoneless, si el test cambia estado y necesita que el DOM se actualice de forma asíncrona, usa `await fixture.whenStable()` además de (o en lugar de) `fixture.detectChanges()`, según la configuración de TestBed del proyecto.

## Tests de servicios

Vitest **no soporta el callback `done`**. Para observables, convertir a promesa con `firstValueFrom` (o `lastValueFrom`) y usar `async/await`:

```typescript
// items-service.spec.ts
import { TestBed } from '@angular/core/testing';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { ItemsService } from './items-service';
import { API_BASE_URL } from '@tokens/.';

describe('ItemsService', () => {
  let service: ItemsService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: API_BASE_URL, useValue: 'http://api.test' },
      ],
    });

    service = TestBed.inject(ItemsService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify(); // Verificar que no haya peticiones pendientes
  });

  describe('getItems()', () => {
    it('should return items from API', async () => {
      const mockItems: Item[] = [{ id: '1', name: 'Item 1', description: '', status: 'active' }];

      const result = firstValueFrom(service.getItems());

      const req = httpMock.expectOne('/api/items');
      expect(req.request.method).toBe('GET');
      req.flush(mockItems);

      expect(await result).toEqual(mockItems);
    });
  });

  describe('getItem()', () => {
    it('should return null on 404', async () => {
      const result = firstValueFrom(service.getItem('not-found'));

      const req = httpMock.expectOne('/api/items/not-found');
      req.flush('Not found', { status: 404, statusText: 'Not Found' });

      expect(await result).toBeNull();
    });

    it('should propagate other errors', async () => {
      const result = firstValueFrom(service.getItem('1'));

      httpMock.expectOne('/api/items/1').flush('Error', { status: 500, statusText: 'Server Error' });

      await expect(result).rejects.toMatchObject({ status: 500 });
    });
  });

  describe('selectItem()', () => {
    it('should update selectedItem signal', () => {
      const item: Item = { id: '1', name: 'Test', description: '', status: 'active' };
      service.selectItem(item);

      expect(service.selectedItem()).toEqual(item);
      expect(service.hasSelection()).toBe(true);
    });
  });
});
```

Crea la promesa (`firstValueFrom`) **antes** de hacer `flush`, porque la suscripción es la que dispara la petición.

## Tests de guards

```typescript
// authenticated-guard.spec.ts
import { TestBed } from '@angular/core/testing';
import { Router, UrlTree, type Route, type UrlSegment } from '@angular/router';
import { vi } from 'vitest';
import { authenticatedGuard } from './authenticated-guard';
import { AuthService } from '@services/.';

describe('authenticatedGuard', () => {
  const loginTree = {} as UrlTree;
  const authServiceMock = { isAuthenticated: vi.fn<() => boolean>() } satisfies Partial<AuthService>;
  const routerMock = { createUrlTree: vi.fn(() => loginTree) } satisfies Partial<Router>;

  // Argumentos mínimos tipados en lugar de {} as any
  const route: Route = {};
  const segments: UrlSegment[] = [];

  const runGuard = () =>
    TestBed.runInInjectionContext(() => authenticatedGuard(route, segments));

  beforeEach(() => {
    vi.clearAllMocks();
    TestBed.configureTestingModule({
      providers: [
        { provide: AuthService, useValue: authServiceMock },
        { provide: Router, useValue: routerMock },
      ],
    });
  });

  it('should return true when authenticated', () => {
    authServiceMock.isAuthenticated.mockReturnValue(true);

    expect(runGuard()).toBe(true);
  });

  it('should redirect to /login when not authenticated', () => {
    authServiceMock.isAuthenticated.mockReturnValue(false);

    const result = runGuard();

    expect(routerMock.createUrlTree).toHaveBeenCalledWith(['/login']);
    expect(result).toBe(loginTree);
  });
});
```

## Tests de pipes

Si el pipe usa `inject()`, no puede instanciarse con `new` fuera de un contexto de inyección. Crea el pipe dentro de `TestBed.runInInjectionContext` y provee sus dependencias:

```typescript
// format-date.pipe.spec.ts
import { TestBed } from '@angular/core/testing';
import { signal } from '@angular/core';
import { FormatDatePipe } from './format-date.pipe';
import { LocaleService } from '@services/.';

describe('FormatDatePipe', () => {
  let pipe: FormatDatePipe;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [{ provide: LocaleService, useValue: { current: signal('es') } }],
    });
    pipe = TestBed.runInInjectionContext(() => new FormatDatePipe());
  });

  it('should format date with default format', () => {
    const date = new Date(2024, 0, 15);
    expect(pipe.transform(date)).toBe('15/01/2024');
  });

  it('should format date with custom format', () => {
    const date = new Date(2024, 0, 15);
    expect(pipe.transform(date, 'yyyy-MM-dd')).toBe('2024-01-15');
  });

  it('should handle string input', () => {
    expect(pipe.transform('2024-01-15')).toBe('15/01/2024');
  });
});
```

Usa `new Date(año, mes, día)` (hora local) en lugar de `new Date('2024-01-15')` (UTC) para evitar fallos por zona horaria en el CI. Registra los datos de locale (`registerLocaleData`) si el pipe formatea con un locale distinto de `en-US`.

## Tests de funciones puras (utils)

```typescript
// validators.spec.ts
import { FormControl, FormGroup } from '@angular/forms';
import { noWhitespaceValidator, matchFieldsValidator } from './validators';

describe('noWhitespaceValidator', () => {
  const validator = noWhitespaceValidator();

  it('should return null for valid input', () => {
    const control = new FormControl('valid-value');
    expect(validator(control)).toBeNull();
  });

  it('should return error for leading whitespace', () => {
    const control = new FormControl(' invalid');
    expect(validator(control)).toEqual({ noWhitespace: true });
  });
});

describe('matchFieldsValidator', () => {
  const validator = matchFieldsValidator('password', 'confirm');

  it('should return null when fields match', () => {
    const group = new FormGroup({ password: new FormControl('a'), confirm: new FormControl('a') });
    expect(validator(group)).toBeNull();
  });

  it('should return error on the group when fields differ', () => {
    const group = new FormGroup({ password: new FormControl('a'), confirm: new FormControl('b') });
    expect(validator(group)).toEqual({ fieldsMismatch: true });
  });
});
```

## Ejecutar los tests

```powershell
# Una sola aplicación
ng test

# Workspace multiproyecto de Angular CLI: por proyecto
ng test portal
ng test @acme/ui

# Nx: por proyecto o solo lo afectado
nx test portal-feature-orders
nx affected -t test
```

- Los tests de una librería se ejecutan en su propio proyecto, no desde la aplicación que la usa.
- En un monorepo, ejecuta los tests de **todos** los proyectos afectados por el cambio, no solo los del proyecto que editaste: una librería compartida afecta a sus consumidores (ver `angular-monorepo`).

## Objetivo de cobertura

La cobertura exigida la define `guidelines/coding-guidelines.md` (o la petición concreta). Si el proyecto exige **100 %** (statements, branches, functions, lines), aplícalo al código nuevo o modificado.

- Cubrir todos los branches de `@if`, `@switch`, `computed()` con condiciones, y `catchError`.
- Testear tanto el happy path como los casos de error.
- Verificar comportamiento con `null` / `undefined` cuando el tipo lo permite.
- La cobertura es un mínimo, no el objetivo: no añadas tests triviales que solo ejecutan líneas sin comprobar comportamiento.

## Convenciones

- Ficheros `.spec.ts` junto al fichero que testean.
- `describe` para la clase/función; `describe` anidado para método/caso.
- `it` con descripción en presente: `'should return null when item not found'`.
- `vi.clearAllMocks()` en `beforeEach` (o `restoreMocks` en la configuración) para que los tests no dependan del orden.
- Usar `vi.fn()` (Vitest) para spies y mocks, no `jasmine.createSpy`.
- Sin `any` en tests: mocks con `satisfies Partial<T>` y conversiones explícitas desde `unknown`.
- **Por defecto, no crear `.spec.ts`** al generar componentes o servicios, salvo que se solicite explícitamente o las guidelines lo exijan.
- Tests de código SSR y de librerías: ver `angular-ssr` y `angular-library`.
