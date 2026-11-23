---
name: angular-solid
description: 'Frontend Angular. Principios SOLID aplicados a Angular. Usar cuando: diseñar arquitectura de componentes o servicios, evaluar si una clase tiene demasiadas responsabilidades, decidir cómo extender funcionalidad sin modificar código existente, definir contratos de servicio para testing, segregar interfaces por casos de uso, aplicar inversión de dependencias con InjectionToken. Cubre SRP, OCP, LSP, ISP y DIP con ejemplos Angular reales.'
argument-hint: 'Describe el componente, servicio o arquitectura que necesitas diseñar o refactorizar.'
---

# Principios SOLID en Angular

SOLID es una herramienta para reducir acoplamiento y facilitar el cambio, no un fin en sí mismo. Aplica cada principio cuando resuelva un problema real del código; evita capas, interfaces y tokens que no aportan nada (arquitectura ceremonial).

## S — Single Responsibility Principle

**Cada clase tiene una única razón para cambiar.**

### Síntomas de violación

- Un componente con mucha lógica de negocio (orientativo: más de 200 líneas de lógica) mezclada con presentación
- Un servicio que gestiona autenticación, datos de usuario Y preferencias UI
- Una función con más de 3 niveles de anidamiento

El número de líneas es una señal, no una regla: divide por **razones de cambio**, no por tamaño.

### Aplicación en Angular

```typescript
// ❌ Servicio con múltiples responsabilidades
@Injectable({ providedIn: 'root' })
export class UserService {
  getUser(id: string): Observable<User> { ... }
  updateUser(user: User): Observable<User> { ... }
  login(credentials: Credentials): Observable<Token> { ... }   // ← auth
  logout(): void { ... }                                         // ← auth
  getPreferences(): Observable<Preferences> { ... }             // ← prefs
  updateTheme(theme: string): void { ... }                      // ← UI
}

// ✅ Responsabilidades separadas
@Injectable({ providedIn: 'root' })
export class UserService {
  getUser(id: string): Observable<User> { ... }
  updateUser(user: User): Observable<User> { ... }
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  login(credentials: Credentials): Observable<Token> { ... }
  logout(): void { ... }
}

@Injectable({ providedIn: 'root' })
export class UserPreferencesService {
  getPreferences(): Observable<Preferences> { ... }
  updateTheme(theme: string): void { ... }
}
```

```typescript
// ❌ Componente con lógica de negocio mezclada con lógica de presentación
@Component({ ... })
export class CustomerListComponent {
  // Lógica de filtrado compleja en el componente
  readonly filteredCustomers = computed(() => {
    const customers = this._customers();
    return customers
      .filter(c => c.age >= this.minAge() && c.age <= this.maxAge())
      .filter(c => this.selectedTags().every(t => c.tags.includes(t)))
      .sort((a, b) => this.sortFn(a, b))
      .slice(this.page() * this.pageSize(), (this.page() + 1) * this.pageSize());
  });
}

// ✅ Lógica de filtrado/paginación extraída a una función o servicio testeable
@Injectable({ providedIn: 'root' })
export class CustomerFilterService {
  filterAndPaginate(
    customers: Customer[],
    filters: CustomerFilters,
    pagination: Pagination,
  ): PaginatedResult<Customer> { ... }
}
```

Si la lógica es pura y sin dependencias, una **función exportada** en `utils/` suele ser suficiente; no hace falta un servicio.

## O — Open/Closed Principle

**Abierto a extensión, cerrado a modificación.**

```typescript
// ❌ Componente que hay que modificar para añadir variantes
@Component({
  // ...resto de metadatos
  template: `
    @if (type() === 'primary') {
      <button type="button" class="btn btn-primary">...</button>
    } @else if (type() === 'danger') {
      <button type="button" class="btn btn-danger">...</button>
    } @else if (type() === 'outline') {
      <!-- ← modificar para añadir -->
      <button type="button" class="btn btn-outline-secondary">...</button>
    }
  `,
})
export class ActionButtonComponent {
  readonly type = input<'primary' | 'danger' | 'outline'>('primary');
}

// ✅ Extensible mediante inputs, sin modificar el componente base
@Component({
  selector: 'app-action-button',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <button
      type="button"
      class="btn"
      [class]="'btn btn-' + variant()"
      [class.btn-sm]="size() === 'sm'"
      [class.btn-lg]="size() === 'lg'"
    >
      <ng-content />
    </button>
  `,
})
export class ActionButtonComponent {
  readonly variant = input<ButtonVariant>('primary'); // unión de variantes del framework CSS
  readonly size = input<'sm' | 'md' | 'lg'>('md');
}
```

Tipa las variantes con una unión (`ButtonVariant`) en lugar de `string` para no perder comprobación de tipos.

```typescript
// ✅ InjectionToken para extender comportamiento sin modificar el servicio
export const EXPORT_STRATEGY = new InjectionToken<ExportStrategy>('EXPORT_STRATEGY');

@Injectable({ providedIn: 'root' })
export class ReportService {
  private readonly exportStrategy = inject(EXPORT_STRATEGY);

  export(data: ReportData): void {
    this.exportStrategy.export(data);  // Comportamiento inyectable
  }
}

// Implementaciones alternativas sin tocar ReportService
export class PdfExportStrategy implements ExportStrategy { ... }
export class ExcelExportStrategy implements ExportStrategy { ... }
```

Usa el patrón Strategy cuando haya **variantes reales** (hoy o planificadas). Con una sola implementación, un servicio directo es más simple.

## L — Liskov Substitution Principle

**Las implementaciones concretas deben ser sustituibles por su abstracción.**

En TypeScript una `interface` no existe en runtime y no puede usarse como token de DI. Para inyectar una abstracción, usa una clase abstracta o un `InjectionToken`:

```typescript
// Contrato explícito como clase abstracta (sirve como token de DI)
export abstract class NotificationService {
  abstract success(messageKey: string): void;
  abstract error(messageKey: string): void;
  abstract warn(messageKey: string): void;
}

// Implementación real
@Injectable()
export class ToastNotificationService extends NotificationService {
  success(messageKey: string): void {
    /* muestra toast verde */
  }
  error(messageKey: string): void {
    /* muestra toast rojo */
  }
  warn(messageKey: string): void {
    /* muestra toast amarillo */
  }
}

// Registro
{ provide: NotificationService, useClass: ToastNotificationService }

// Mock para tests — cumple el mismo contrato
export class MockNotificationService extends NotificationService {
  readonly messages: string[] = [];
  success(messageKey: string): void {
    this.messages.push(`success:${messageKey}`);
  }
  error(messageKey: string): void {
    this.messages.push(`error:${messageKey}`);
  }
  warn(messageKey: string): void {
    this.messages.push(`warn:${messageKey}`);
  }
}

// En tests — intercambiable sin cambiar el componente bajo prueba
TestBed.configureTestingModule({
  providers: [{ provide: NotificationService, useClass: MockNotificationService }],
});
```

Sustituible significa también **mismo comportamiento esperado**: una implementación que lanza excepciones donde la abstracción no lo prevé, o que ignora llamadas, rompe LSP aunque compile.

## I — Interface Segregation Principle

**Interfaces pequeñas y específicas. No forzar la implementación de métodos que no se usan.**

```typescript
// ❌ Interfaz monolítica — los consumidores de solo lectura dependen también de la escritura
export interface CustomerRepository {
  getCustomer(id: string): Observable<Customer>;
  getCustomers(): Observable<Customer[]>;
  createCustomer(data: CreateCustomerDto): Observable<Customer>;
  updateCustomer(id: string, data: UpdateCustomerDto): Observable<Customer>;
  deleteCustomer(id: string): Observable<void>;
}

// ✅ Interfaces segregadas por rol
export interface CustomerReader {
  getCustomer(id: string): Observable<Customer>;
  getCustomers(): Observable<Customer[]>;
}

export interface CustomerWriter {
  createCustomer(data: CreateCustomerDto): Observable<Customer>;
  updateCustomer(id: string, data: UpdateCustomerDto): Observable<Customer>;
  deleteCustomer(id: string): Observable<void>;
}

export const CUSTOMER_READER = new InjectionToken<CustomerReader>('CUSTOMER_READER');
export const CUSTOMER_WRITER = new InjectionToken<CustomerWriter>('CUSTOMER_WRITER');

// El componente de detalle solo necesita leer
export class CustomerDetailComponent {
  private readonly customerReader = inject(CUSTOMER_READER);
}

// El componente de administración necesita ambos
export class CustomerAdminComponent {
  private readonly customerReader = inject(CUSTOMER_READER);
  private readonly customerWriter = inject(CUSTOMER_WRITER);
}
```

```typescript
// ✅ Tipos específicos para contextos diferentes
// En lugar de pasar el objeto completo siempre
export interface CustomerSummary {
  readonly id: string;
  readonly name: string;
  readonly code: string;
}

export interface CustomerDetail extends CustomerSummary {
  readonly birthDate: Date;
  readonly addresses: Address[];
  readonly orders: OrderSummary[];
  readonly tags: string[];
}

// El listado solo necesita CustomerSummary — menos datos, menos acoplamiento
export class CustomerListComponent {
  readonly customers = input.required<CustomerSummary[]>();
}
```

La segregación de tipos (`Summary`/`Detail`) casi siempre compensa. La segregación de servicios en varios tokens solo compensa cuando hay consumidores con necesidades realmente distintas.

## D — Dependency Inversion Principle

**Depender de abstracciones, no de implementaciones.**

```typescript
// ❌ Dependencia directa de implementación concreta
@Component({ ... })
export class CustomerCardComponent {
  // Instanciación manual — nunca hacer esto
  private readonly service = new CustomerService(new HttpClient(...));
}

// ✅ Dependencia inyectada
@Component({ ... })
export class CustomerCardComponent {
  private readonly service = inject(CustomerService);  // DI resuelve la implementación
}
```

```typescript
// ✅ InjectionToken para desacoplar de implementaciones concretas
export const CUSTOMER_REPOSITORY = new InjectionToken<CustomerRepository>(
  'CUSTOMER_REPOSITORY',
);

// En app.config.ts o el provider de la ruta
{
  provide: CUSTOMER_REPOSITORY,
  useClass: HttpCustomerRepository,
}

// En tests
{
  provide: CUSTOMER_REPOSITORY,
  useClass: InMemoryCustomerRepository,
}

// El componente depende de la abstracción, no de la implementación HTTP
@Component({ ... })
export class CustomerListComponent {
  private readonly repository = inject(CUSTOMER_REPOSITORY);
}
```

La DI de Angular ya permite sustituir cualquier servicio concreto en tests (`{ provide: CustomerService, useValue: mock }`). Introduce una abstracción explícita cuando haya **más de una implementación real** o una frontera que quieras aislar (por ejemplo, el origen de datos, o el acceso a APIs del navegador en aplicaciones con SSR), no para cada servicio.

En un monorepo, los límites entre librerías (tipos `feature`, `ui`, `data-access`, `util`) son la versión a gran escala de estos principios: una dependencia en una sola dirección y contratos pequeños entre capas (ver `angular-monorepo`).

## Checklist de diseño

- [ ] Cada clase tiene una razón de cambio identificable
- [ ] Las variantes se extienden sin modificar el código base cuando existen variantes reales
- [ ] Las implementaciones intercambiables respetan el contrato y su comportamiento
- [ ] Los consumidores dependen solo de lo que usan
- [ ] Ninguna clase instancia dependencias con `new`
- [ ] No se han creado interfaces, tokens o capas sin un beneficio concreto
