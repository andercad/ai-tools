# Testing

Los tests específicos de resolvers GraphQL y de handlers de mensajes están en `nestjs-graphql` y `nestjs-microservices`; siguen las mismas reglas que este documento.

## Reglas

- Usa el runner **instalado**: compruébalo en `package.json` (y, en un monorepo, en la configuración del proyecto). Los proyectos existentes suelen usar **Jest**; NestJS 12 orienta los proyectos nuevos a ESM y **Vitest**. Los ejemplos usan Jest; con Vitest, el equivalente de `jest.fn()`/`jest.Mocked` es `vi.fn()`/`Mocked` de `vitest`. No mezcles APIs en el mismo proyecto.
- Ficheros de test con sufijo `.spec.ts` junto al fichero que testean; tests e2e en `test/*.e2e-spec.ts`.
- Tests unitarios para servicios con mocks de repositorios y dependencias.
- Tests de integración para controladores con `supertest` y base de datos en contenedor Docker (Testcontainers) o la base de datos de test del proyecto.
- `describe`/`it` con descripciones claras, en presente: `'should throw NotFoundException when user does not exist'`.
- **Por defecto, no crees `.spec.ts`** al generar módulos o servicios, salvo que se solicite.
- Prueba **comportamiento** (resultado, excepción lanzada, llamada relevante), no detalles internos.
- Sin `any` en tests: mocks tipados.

## Cobertura

La cobertura exigida la define el `CLAUDE.md` del proyecto (o la petición concreta). **Cuando se pida 100 %** (statements, branches, functions, lines), aplícalo al código nuevo o modificado y ejecuta el suite para validar antes de entregar. La cobertura es un mínimo, no el objetivo: no añadas tests que ejecutan líneas sin comprobar nada.

## Test unitario de servicio

```typescript
describe('UsersService', () => {
  let service: UsersService;
  let repo: jest.Mocked<Pick<Repository<UserEntity>, 'findOne' | 'exists' | 'create' | 'save'>>;

  beforeEach(async () => {
    repo = {
      findOne: jest.fn(),
      exists: jest.fn(),
      create: jest.fn(),
      save: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        { provide: getRepositoryToken(UserEntity), useValue: repo },
        { provide: PasswordHasher, useValue: { hash: jest.fn().mockResolvedValue('hashed') } },
      ],
    }).compile();

    service = module.get(UsersService);
  });

  describe('findOne()', () => {
    it('should return a user by id', async () => {
      const user = { id: 'u-1', email: 'test@example.com', createdAt: new Date() } as UserEntity;
      repo.findOne.mockResolvedValue(user);

      const result = await service.findOne('u-1');

      expect(result).toMatchObject({ id: 'u-1', email: 'test@example.com' });
      expect(result).not.toHaveProperty('passwordHash');
    });

    it('should throw NotFoundException when user does not exist', async () => {
      repo.findOne.mockResolvedValue(null);

      await expect(service.findOne('missing')).rejects.toBeInstanceOf(NotFoundException);
    });
  });

  describe('create()', () => {
    it('should throw ConflictException when email is already registered', async () => {
      repo.exists.mockResolvedValue(true);

      await expect(
        service.create({ email: 'a@b.com', password: 'password123' }),
      ).rejects.toBeInstanceOf(ConflictException);
      expect(repo.save).not.toHaveBeenCalled();
    });
  });
});
```

- `jest.Mocked<Pick<...>>` tipa solo los métodos usados, sin `as any`.
- El cast `as UserEntity` en datos de prueba parciales es aceptable; `as any` no.
- Con Vitest, el equivalente es `vi.fn()` y el tipo `Mocked` de `vitest`.

## Test de guard

```typescript
describe('RolesGuard', () => {
  const reflector = { getAllAndOverride: jest.fn() } as unknown as Reflector;
  const guard = new RolesGuard(reflector);

  const contextFor = (user?: AuthenticatedUser): ExecutionContext =>
    ({
      getType: () => 'http',
      getHandler: () => undefined,
      getClass: () => undefined,
      switchToHttp: () => ({ getRequest: () => ({ user }) }),
    }) as unknown as ExecutionContext;

  it('should allow when no roles are required', () => {
    jest.mocked(reflector.getAllAndOverride).mockReturnValue(undefined);
    expect(guard.canActivate(contextFor())).toBe(true);
  });

  it('should deny when there is no authenticated user', () => {
    jest.mocked(reflector.getAllAndOverride).mockReturnValue(['admin']);
    expect(guard.canActivate(contextFor(undefined))).toBe(false);
  });

  it('should allow when user has a required role', () => {
    jest.mocked(reflector.getAllAndOverride).mockReturnValue(['admin']);
    expect(guard.canActivate(contextFor({ id: 'u-1', roles: ['admin'] }))).toBe(true);
  });
});
```

Instanciar con `new` en un test unitario de una clase sin dependencias de framework es correcto; la regla de "no `new`" aplica al código de producción. Si el guard distingue contextos (`http`, `graphql`, `rpc`), añade un caso por contexto.

## Test e2e

```typescript
// test/users.e2e-spec.ts
describe('Users (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleRef.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('POST /users should reject unknown properties', async () => {
    await request(app.getHttpServer())
      .post('/users')
      .send({ email: 'a@b.com', password: 'password123', isAdmin: true })
      .expect(400);
  });

  it('GET /users/:id should reject non-UUID ids', async () => {
    await request(app.getHttpServer()).get('/users/123').expect(400);
  });
});
```

- `createNestApplication()` **no ejecuta `main.ts`**: lo registrado con `app.useGlobalPipes/Guards/Filters` no se aplica. Por eso se recomienda registrar pipes, guards y filtros globales con `APP_PIPE`, `APP_GUARD` y `APP_FILTER`; si el proyecto usa `useGlobal*`, repítelos en el `beforeAll`.
- Prueba en e2e lo que los unitarios no cubren: validación real, guards, serialización, códigos de estado, formato de error.

## Base de datos en tests

- Para lógica que depende del motor (constraints, índices únicos, transacciones, SQL nativo), usa una base de datos real en contenedor (Testcontainers) en lugar de mocks o SQLite en memoria, que se comporta distinto.
- Cada test deja la base de datos en un estado conocido (transacción revertida o limpieza en `afterEach`).
- No dependas del orden de ejecución de los tests.

## Sustituir providers

```typescript
const moduleRef = await Test.createTestingModule({ imports: [AppModule] })
  .overrideProvider(EmailService)
  .useValue({ send: jest.fn().mockResolvedValue(undefined) })
  .overrideGuard(JwtAuthGuard)
  .useValue({ canActivate: () => true })
  .compile();
```

## Ejecutar los tests

```powershell
# Una sola aplicación
npm test
npm run test:e2e

# Modo monorepo del Nest CLI: por aplicación o librería (según los scripts y la configuración de Jest del proyecto)
npx jest apps/billing
npx jest libs/common

# Nx: por proyecto o solo lo afectado
nx test api-orders
nx affected -t test
```

- **Nest CLI en modo monorepo**: los aliases de las librerías deben estar en el `moduleNameMapper` de Jest; si un test falla con `Cannot find module '@app/...'`, revisa ese mapeo antes de tocar el código.
- Los tests de una librería se ejecutan en su propio proyecto; los e2e, en el de la aplicación.
- En un monorepo, ejecuta los tests de **todos** los proyectos afectados por el cambio: una librería compartida afecta a todas las aplicaciones que la usan (ver `nestjs-workspace`).

## Checklist

- [ ] Runner y API coherentes (Jest o Vitest, no ambos)
- [ ] Mocks tipados, sin `as any`
- [ ] Casos de éxito y de error (excepciones esperadas)
- [ ] Guards y pipes con sus ramas cubiertas, incluidos los contextos que soportan (ver `nestjs-security`)
- [ ] Casos de seguridad: campos no permitidos rechazados, 401/403/404 en accesos indebidos
- [ ] E2E con la configuración global equivalente a producción
- [ ] Base de datos real para lógica dependiente del motor
- [ ] Tests de todos los proyectos afectados (monorepo)
- [ ] Cobertura según el `CLAUDE.md` del proyecto o petición
