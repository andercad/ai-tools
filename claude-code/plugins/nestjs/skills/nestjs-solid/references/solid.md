# Principios SOLID

SOLID es una herramienta para reducir acoplamiento y facilitar el cambio, no un fin en sí mismo. Aplica cada principio cuando resuelva un problema real; evita capas, interfaces y tokens que no aportan nada. Un CRUD sencillo no necesita arquitectura hexagonal.

## S — Single Responsibility Principle

Cada módulo, servicio, controlador o función tiene **una única razón para cambiar**.

- Un servicio gestiona una sola entidad o preocupación. No mezcles responsabilidades de dominio.
- Un controlador gestiona un solo recurso REST. Si acumula demasiada lógica, extrae a servicios.
- Las funciones en `utils/` o `helpers/` hacen una sola cosa sin side-effects.

```typescript
// ❌ Un servicio que hace de todo
@Injectable()
export class UsersService {
  create(dto: CreateUserDto): Promise<UserResponseDto> { ... }
  login(dto: LoginDto): Promise<TokenResponseDto> { ... }       // ← autenticación
  sendWelcomeEmail(email: string): Promise<void> { ... }        // ← notificaciones
  exportCsv(): Promise<Buffer> { ... }                          // ← informes
}

// ✅ Separado por razón de cambio
@Injectable() export class UsersService { create(...) { ... } }
@Injectable() export class AuthService { login(...) { ... } }
@Injectable() export class NotificationsService { sendWelcomeEmail(...) { ... } }
@Injectable() export class UserReportsService { exportCsv(...) { ... } }
```

El mismo servicio debe poder usarse desde un controlador REST, un resolver GraphQL o un handler de mensajes: si un servicio conoce detalles del transporte, tiene dos razones para cambiar.

## O — Open/Closed Principle

**Abiertos a extensión, cerrados a modificación**.

- Extiende con nuevos guards, interceptores o pipes en lugar de modificar los existentes.
- Usa tokens de inyección y DI para parametrizar comportamiento.
- Controla variantes de comportamiento con estrategias (`Strategy pattern`) o configuración, cuando existan variantes reales:

```typescript
export interface PaymentGateway {
  charge(amountCents: number, reference: string): Promise<PaymentResult>;
}

export const PAYMENT_GATEWAYS = Symbol('PAYMENT_GATEWAYS');

@Module({
  providers: [
    StripeGateway,
    RedsysGateway,
    {
      provide: PAYMENT_GATEWAYS,
      inject: [StripeGateway, RedsysGateway],
      useFactory: (stripe: StripeGateway, redsys: RedsysGateway): Record<string, PaymentGateway> => ({
        stripe,
        redsys,
      }),
    },
  ],
})
export class PaymentsModule {}
```

Añadir una pasarela nueva es registrar otra implementación, sin tocar el servicio que las usa.

## L — Liskov Substitution Principle

Las implementaciones concretas deben ser **sustituibles** por su abstracción.

- Cualquier implementación de un repositorio (real o mock) debe cumplir el mismo contrato.
- Un `MockUsersService` debe ser intercambiable con `UsersService` sin alterar el comportamiento del consumidor.
- Sustituible significa también **mismo comportamiento esperado**: una implementación que lanza excepciones donde la abstracción no lo prevé, o que devuelve `null` donde el contrato promete un valor, rompe el principio aunque compile.

## I — Interface Segregation Principle

**Interfaces pequeñas y específicas**.

- Define interfaces separadas para distintos roles (ej. `UserSummary` para listados, `UserDetail` para detalle).
- Si un servicio solo necesita `id` y `email`, declara un tipo con solo esas propiedades.

```typescript
export interface UserReader {
  findById(id: string): Promise<User | null>;
}

export interface UserWriter {
  save(user: User): Promise<User>;
}

// Un caso de uso de solo lectura depende solo de UserReader
```

## D — Dependency Inversion Principle

**Depender de abstracciones, no de implementaciones**.

- **Nunca instancies servicios con `new`**; usa siempre el sistema DI de NestJS.
- Usa **tokens de inyección personalizados** para desacoplar implementaciones concretas. En NestJS un token es un `string`, un `symbol` o una clase (a menudo abstracta). Las `interface` de TypeScript no existen en runtime y **no** sirven como token.
- Sustituye dependencias por mocks en tests a través de DI sin modificar el código bajo prueba.

```typescript
// Opción 1: clase abstracta como contrato y token a la vez
export abstract class UserRepository {
  abstract findById(id: string): Promise<User | null>;
  abstract save(user: User): Promise<User>;
}

@Injectable()
export class TypeOrmUserRepository extends UserRepository { ... }

@Module({
  providers: [{ provide: UserRepository, useClass: TypeOrmUserRepository }],
  exports: [UserRepository],
})
export class UsersModule {}

// Consumidor: depende de la abstracción
@Injectable()
export class RegisterUserUseCase {
  constructor(private readonly users: UserRepository) {}
}
```

```typescript
// Opción 2: interface + token symbol
export interface Clock {
  now(): Date;
}
export const CLOCK = Symbol('CLOCK');

@Module({ providers: [{ provide: CLOCK, useValue: { now: () => new Date() } satisfies Clock }] })
export class CommonModule {}

@Injectable()
export class InvoicesService {
  constructor(@Inject(CLOCK) private readonly clock: Clock) {}
}
```

La DI de Nest ya permite sustituir cualquier provider concreto en tests (`overrideProvider`). Introduce una abstracción explícita cuando haya **más de una implementación real**, una frontera que quieras aislar (persistencia, proveedor externo, transporte de mensajería, reloj) o una necesidad de test que no se cubra de otra forma; no para cada servicio.

En un monorepo, los límites entre librerías (tipos `feature`, `data-access`, `util`, `contract`) son la versión a gran escala de estos principios: dependencias en una sola dirección y contratos pequeños entre capas (ver `nestjs-workspace`).

## Checklist de diseño

- [ ] Cada clase tiene una razón de cambio identificable
- [ ] Las variantes reales se añaden sin modificar el código que las consume
- [ ] Las implementaciones intercambiables respetan contrato y comportamiento
- [ ] Los consumidores dependen solo de lo que usan
- [ ] Sin `new` de providers; tokens como clase abstracta, `symbol` o `string`
- [ ] Sin abstracciones sin beneficio concreto
