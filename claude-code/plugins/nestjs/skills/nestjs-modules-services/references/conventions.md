# Convenciones estándar de código NestJS

Valores por defecto: si el `CLAUDE.md` del proyecto define estructura, alias o naming distintos, prevalece el del proyecto.

Estructura de referencia para un módulo de dominio:

```
src/
  app.module.ts
  main.ts
  <dominio>/
    dto/
      create-<dominio>.dto.ts
      update-<dominio>.dto.ts
      <dominio>-response.dto.ts
      index.ts
    entities/
      <dominio>.entity.ts
      index.ts
    interfaces/
      <dominio>.interface.ts
      index.ts
    <dominio>.controller.ts
    <dominio>.controller.spec.ts
    <dominio>.service.ts
    <dominio>.service.spec.ts
    <dominio>.module.ts
  common/
    decorators/
    filters/
    guards/
    interceptors/
    pipes/
    middleware/
  config/
    env.validation.ts
test/
  <dominio>.e2e-spec.ts
```

Si el proyecto usa GraphQL o microservicios, cada dominio añade `models/` y `<dominio>.resolver.ts`, o los controladores de mensajes (ver `nestjs-graphql` y `nestjs-microservices`).

Reglas independientes de la estructura concreta:

- Crea **barrel files** (`index.ts`) en cada carpeta para agrupar exportaciones.
- Usa **siempre los alias de `tsconfig.json`** para imports. No uses imports relativos (`../`) salvo dependencia cíclica documentada con un comentario explicativo.
- Cuando crees una nueva carpeta de primer nivel en `src/`, añade su alias en `tsconfig.json` → `compilerOptions.paths` antes de usarla. Comprueba que el build (`nest build`, `tsc`, bundler) y el test runner resuelven los alias; si no, configúralos también allí.
- Evita barrels que reexporten módulos entre sí de forma circular: es una causa habitual de dependencias circulares y de providers `undefined` en tiempo de arranque.

**En un monorepo** (ver `nestjs-workspace`) estas reglas cambian:

- Cada aplicación (`apps/<app>`) tiene la estructura anterior; el código compartido entre aplicaciones vive en **librerías** (`libs/`), no se copia.
- Los aliases identifican **librerías**, no carpetas: en el Nest CLI los registra `nest generate library` en `tsconfig.json`; en Nx están en `tsconfig.base.json` o los resuelven los *workspaces* del gestor de paquetes. No crees aliases por carpeta.
- Entre proyectos, importa **solo** por el punto de entrada público de la librería (`@acme/api/orders`); nunca con rutas relativas que salgan del proyecto ni con imports profundos (`@acme/api/orders/src/lib/...`).
- Respeta los límites entre librerías definidos por etiquetas o reglas de lint.

## Naming conventions

- **Ficheros**: kebab-case siempre (ej. `users.service.ts`, `create-user.dto.ts`).
- **Clases**: PascalCase con sufijo descriptivo:
  - Módulos: `UsersModule`
  - Controladores: `UsersController`
  - Servicios: `UsersService`
  - DTOs: `CreateUserDto`, `UpdateUserDto`, `UserResponseDto`
  - Entidades: `UserEntity`
  - Guards: `JwtAuthGuard`, `RolesGuard`
  - Interceptores: `LoggingInterceptor`, `TransformInterceptor`
  - Filtros: `HttpExceptionFilter`, `AllExceptionsFilter`
  - Pipes: `ParsePositiveIntPipe`
  - GraphQL: `UsersResolver`, `UserModel`, `CreateUserInput`, `UsersArgs`
  - Mensajería: `OrderEventsController`, `OrderCreatedEvent`
- **Interfaces/tipos**: sin prefijo `I`; usa `User`, no `IUser`.
- **Decorators personalizados**: PascalCase (ej. `@CurrentUser()`).
- **Tokens de inyección**: constantes en UPPER_SNAKE_CASE (ej. `USER_REPOSITORY`).

## Orden de miembros en clases

### Controladores

```typescript
// 1. Constructor — inyección de dependencias
constructor(private readonly usersService: UsersService) {}

// 2. Endpoints GET (lectura)
@Get()
findAll(): Promise<UserResponseDto[]> { ... }

// 3. Endpoints de escritura (POST, PUT, PATCH, DELETE)
@Post()
create(@Body() dto: CreateUserDto): Promise<UserResponseDto> { ... }
```

### Resolvers GraphQL

```typescript
// 1. Constructor
// 2. Queries
// 3. Mutations
// 4. Campos resueltos (@ResolveField)
```

### Servicios

```typescript
// 1. Propiedades (logger, constantes)
private readonly logger = new Logger(UsersService.name);

// 2. Constructor — inyección de dependencias
constructor(
  @InjectRepository(UserEntity)
  private readonly repo: Repository<UserEntity>,
) {}

// 3. Métodos públicos de lectura
async findOne(id: string): Promise<UserResponseDto> { ... }

// 4. Métodos públicos de escritura
async create(dto: CreateUserDto): Promise<UserResponseDto> { ... }

// 5. Métodos privados
private toDto(entity: UserEntity): UserResponseDto { ... }
```

### Módulos

```typescript
@Module({
  // 1. imports
  // 2. controllers
  // 3. providers
  // 4. exports
})
```

## Interfaces y tipos

- Declara en `interfaces/` organizado por dominio.
- **Sin prefijo `I`**: usa `User`, no `IUser`.
- `interface` para objetos; `type` para uniones, intersecciones y alias de primitivos.
- Exporta desde barrel `interfaces/index.ts`.
- `readonly` en propiedades que no deban mutarse.
- Define siempre la interfaz para respuestas de API conocidas; no uses `unknown` u `object` para contratos conocidos. Reserva `unknown` para datos realmente no tipados (entrada externa antes de validar, errores capturados).
- Las interfaces no existen en runtime: no pueden usarse como tokens de inyección ni para validación (ver `nestjs-solid` y `nestjs-api`).
- En un monorepo con el frontend, los contratos de la API se definen como interfaces en una librería compartida de solo tipos, que los DTO implementan (ver `nestjs-workspace`).

## Documentación del código

- **JSDoc** conciso en clases, propiedades públicas y métodos.
- Bloque `@example` en servicios reutilizables complejos; no en controladores simples.
- Comentarios de bloque para separar secciones lógicas:

  ```typescript
  // --- Dependencies ---
  // --- Public methods ---
  // --- Private methods ---
  ```

- **No sobre-documentes**: no añadas comentarios a código cuya intención sea evidente.
