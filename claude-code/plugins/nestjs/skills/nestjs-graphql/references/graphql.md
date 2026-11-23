# GraphQL

Comprueba en `package.json` y en el `CLAUDE.md` del proyecto:

- **Driver**: `@nestjs/apollo` (Apollo Server) o `@nestjs/mercurius` (Fastify). Los ejemplos usan Apollo; las opciones de configuración difieren entre drivers y versiones.
- **Enfoque**: **code-first** (el esquema se genera a partir de clases TypeScript) o **schema-first** (se escribe el SDL `.graphql` y se generan los tipos). Por defecto, code-first; respeta el que use el proyecto.

## Principios

- Los resolvers son la capa de transporte, igual que los controladores: **no contienen lógica de negocio**, delegan en los mismos servicios que usa la API REST (ver `nestjs-modules-services`).
- Los tipos GraphQL (`@ObjectType`) son el contrato público: nunca expongas entidades de base de datos como tipos GraphQL.
- Todo argumento de entrada se valida (`@InputType`/`@ArgsType` con `class-validator`, ver `nestjs-api`).
- La autorización se aplica por operación **y por campo/recurso**: en GraphQL un cliente puede llegar a un dato por varios caminos del grafo.

## Estructura

```
src/
  users/
    dto/
      create-user.input.ts
      users.args.ts
    models/
      user.model.ts
    users.resolver.ts
    users.service.ts
    users.module.ts
  graphql/
    loaders/
      loaders.factory.ts
    schema.gql            ← generado (code-first); se versiona para revisar cambios del contrato
```

En un monorepo, cada aplicación que expone GraphQL genera su propio esquema; los resolvers de un dominio pueden vivir en su librería `feature` (ver `nestjs-workspace`).

## Configuración del módulo

```typescript
@Module({
  imports: [
    GraphQLModule.forRootAsync<ApolloDriverConfig>({
      driver: ApolloDriver,
      imports: [LoadersModule],
      inject: [ConfigService, LoadersFactory],
      useFactory: (config: ConfigService, loaders: LoadersFactory): ApolloDriverConfig => {
        const isProduction = config.get<string>('NODE_ENV') === 'production';
        return {
          autoSchemaFile: join(process.cwd(), 'src/graphql/schema.gql'),
          sortSchema: true,
          // Exploración del esquema solo fuera de producción (o según el `CLAUDE.md` del proyecto)
          introspection: !isProduction,
          playground: !isProduction,
          includeStacktraceInErrorResponses: !isProduction,
          // Un juego de DataLoaders NUEVO por petición
          context: ({ req, res }: { req: Request; res: Response }) => ({
            req,
            res,
            loaders: loaders.create(),
          }),
          validationRules: [depthLimit(8)], // límite de profundidad de las consultas
        };
      },
    }),
  ],
})
export class AppGraphqlModule {}
```

- La opción de la interfaz de exploración (`playground`, `graphiql`, plugins de landing page de Apollo) depende de la versión de `@nestjs/apollo`: comprueba la documentación de la versión instalada.
- Desactiva la introspección en producción salvo que el esquema sea público por diseño.

## Tipos (code-first)

```typescript
// models/user.model.ts
@ObjectType('User')
export class UserModel {
  @Field(() => ID)
  readonly id!: string;

  @Field()
  readonly email!: string;

  @Field()
  readonly createdAt!: Date;
}
```

```typescript
// dto/create-user.input.ts
@InputType()
export class CreateUserInput {
  @Field()
  @IsEmail()
  email!: string;

  @Field()
  @IsString()
  @MinLength(8)
  @MaxLength(128)
  password!: string;
}

// dto/users.args.ts
@ArgsType()
export class UsersArgs {
  @Field(() => Int, { defaultValue: 1 })
  @IsInt()
  @Min(1)
  page = 1;

  @Field(() => Int, { defaultValue: 20 })
  @IsInt()
  @Min(1)
  @Max(100)
  limit = 20;
}
```

**Reglas de tipos**:

- En code-first los campos son **no nulos por defecto**. Marca `nullable: true` solo donde el valor puede faltar de verdad.
- Usa `ID` para identificadores, `Int`/`Float` explícitos para números (por defecto `number` se mapea a `Float`).
- Si el DTO de respuesta REST y el tipo GraphQL tienen la misma forma, una misma clase puede llevar `@ObjectType`/`@Field` y `@ApiProperty`. Sepáralos en cuanto los contratos diverjan.
- `PartialType`/`PickType`/`OmitType` para inputs: impórtalos desde `@nestjs/graphql` (no desde `@nestjs/swagger` ni `@nestjs/mapped-types`).

## Resolvers

```typescript
@Resolver(() => UserModel)
export class UsersResolver {
  constructor(private readonly usersService: UsersService) {}

  // --- Queries ---
  @Query(() => UserModel, { name: 'user' })
  user(@Args('id', { type: () => ID }, ParseUUIDPipe) id: string): Promise<UserModel> {
    return this.usersService.findOne(id);
  }

  @Query(() => [UserModel], { name: 'users' })
  @Roles(Role.Admin)
  users(@Args() args: UsersArgs): Promise<UserModel[]> {
    return this.usersService.findAll(args);
  }

  @Query(() => UserModel)
  me(@CurrentUser() user: AuthenticatedUser): Promise<UserModel> {
    return this.usersService.findOne(user.id);
  }

  // --- Mutations ---
  @Public()
  @Mutation(() => UserModel)
  createUser(@Args('input') input: CreateUserInput): Promise<UserModel> {
    return this.usersService.create(input);
  }

  // --- Campos resueltos ---
  @ResolveField(() => [OrderModel])
  orders(
    @Parent() user: UserModel,
    @Context('loaders') loaders: Loaders,
  ): Promise<OrderModel[]> {
    return loaders.ordersByUserId.load(user.id);
  }
}
```

- Orden de miembros: constructor, queries, mutations, campos resueltos.
- Mutations con un único argumento `input` de tipo `@InputType` (más fácil de evolucionar que muchos argumentos sueltos).
- Los resolvers se registran como `providers` del módulo, no como `controllers`.

## DataLoader — evitar N+1

Sin DataLoader, `users { orders { ... } }` lanza una consulta de pedidos **por cada usuario**. DataLoader agrupa todas las claves pedidas en la misma ejecución en una sola consulta.

```typescript
export interface Loaders {
  readonly ordersByUserId: DataLoader<string, OrderModel[]>;
}

@Injectable()
export class LoadersFactory {
  constructor(private readonly ordersService: OrdersService) {}

  create(): Loaders {
    return {
      ordersByUserId: new DataLoader<string, OrderModel[]>(async (userIds) => {
        const orders = await this.ordersService.findByUserIds([...userIds]);
        const byUser = new Map<string, OrderModel[]>();
        for (const order of orders) {
          byUser.set(order.userId, [...(byUser.get(order.userId) ?? []), order]);
        }
        // El resultado debe tener el mismo orden y longitud que las claves
        return userIds.map((id) => byUser.get(id) ?? []);
      }),
    };
  }
}
```

**Reglas**:

- **Un juego de loaders por petición** (creado en `context`). Un DataLoader singleton cachea datos entre peticiones de usuarios distintos: fuga de datos.
- La función batch devuelve los resultados **en el mismo orden y con la misma longitud** que las claves.
- Los métodos de servicio que usan los loaders aplican las mismas reglas de autorización que el resto (filtrar por propietario o permisos).

## Autenticación y autorización

Los guards y `@CurrentUser()` de `nestjs-security` y el throttler de `nestjs-security` leen la petición con `switchToHttp()`, que en GraphQL no devuelve la petición. Usa un helper que funcione en ambos contextos y aplícalo en esos componentes:

```typescript
// common/utils/get-request.ts
export interface RequestWithUser {
  user?: AuthenticatedUser;
}

export function getRequest(context: ExecutionContext): RequestWithUser {
  if (context.getType<GqlContextType>() === 'graphql') {
    return GqlExecutionContext.create(context).getContext<{ req: RequestWithUser }>().req;
  }
  return context.switchToHttp().getRequest<RequestWithUser>();
}
```

```typescript
// JwtAuthGuard: Passport necesita saber dónde está la petición
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
  // ... canActivate con @Public() (ver nestjs-auth)

  getRequest(context: ExecutionContext): RequestWithUser {
    return getRequest(context);
  }
}

// RolesGuard: sustituir switchToHttp().getRequest() por getRequest(context)
// CurrentUser: idem
export const CurrentUser = createParamDecorator(
  (_data: unknown, ctx: ExecutionContext): AuthenticatedUser | undefined => getRequest(ctx).user,
);
```

```typescript
// Throttler en GraphQL
@Injectable()
export class GqlThrottlerGuard extends ThrottlerGuard {
  protected getRequestResponse(context: ExecutionContext) {
    const ctx = GqlExecutionContext.create(context).getContext<{ req: Request; res: Response }>();
    return { req: ctx.req, res: ctx.res };
  }
}
```

- Protege también los `@ResolveField` que exponen datos sensibles: el guard de la query raíz no basta si el mismo tipo se alcanza desde otra query.
- Para autorización por campo, aplica el guard o un field middleware al `@ResolveField`/`@Field` correspondiente.

## Límites de las consultas

GraphQL permite consultas arbitrariamente profundas y costosas. Aplica al menos:

- **Límite de profundidad** (regla de validación, p. ej. `depthLimit(8)`).
- **Límite de complejidad** (plugin de complejidad de consultas) cuando hay listas anidadas.
- **Límite de tamaño de página** en todos los argumentos de paginación (`@Max(100)`).
- Si el driver lo permite, desactiva o limita el *batching* de operaciones y considera *persisted queries* para clientes propios.

## Errores

- En GraphQL los errores van en el array `errors` de la respuesta (habitualmente con HTTP 200); el código está en `extensions.code`.
- Las excepciones lanzadas en servicios (`NotFoundException`, `ConflictException`, errores de dominio) se traducen con el **filtro global multicontexto** (ver `nestjs-api`). El filtro solo-HTTP no sirve en GraphQL.
- Usa códigos estables en `extensions.code` (`NOT_FOUND`, `CONFLICT`, `BAD_REQUEST`...) para que los clientes no dependan del texto del mensaje.
- En producción, sin stack traces ni detalles internos: `includeStacktraceInErrorResponses: false` y un `formatError` que oculte el mensaje de los errores internos si hace falta.

## Paginación

- Listas siempre paginadas y con tamaño máximo.
- Para listas grandes o que cambian a menudo, paginación por cursor (patrón *connection*: `edges`, `node`, `pageInfo`) según el `CLAUDE.md` del proyecto.

## Evolución del esquema

- No elimines ni renombres campos usados por clientes: márcalos con `deprecationReason` y retíralos cuando dejen de usarse.
- Añadir campos opcionales y tipos nuevos es compatible; convertir un campo nullable en no nullable en un *input*, o al revés en un tipo de salida, rompe clientes.
- Versiona `schema.gql` (code-first) para revisar los cambios del contrato en los PR.

## Subscriptions

- Usa el protocolo `graphql-ws`. Autentica en la conexión (`connectionParams`) y vuelve a autorizar por evento.
- El `PubSub` en memoria solo sirve con una instancia; con varias réplicas usa un PubSub distribuido (Redis u otro broker).

## Tests

- Resolvers: tests unitarios como los de controladores, mockeando el servicio (ver `nestjs-testing-quality`).
- E2E: `POST /graphql` con `supertest`, comprobando `data` y `errors[].extensions.code`:

```typescript
it('user query should return NOT_FOUND for unknown id', async () => {
  const response = await request(app.getHttpServer())
    .post('/graphql')
    .set('Authorization', `Bearer ${token}`)
    .send({ query: 'query { user(id: "6f1c0c1e-8a59-4c51-9a8e-0e6f1b2a3c4d") { id } }' })
    .expect(200);

  expect(response.body.errors[0].extensions.code).toBe('NOT_FOUND');
});
```

## Checklist

- [ ] Resolvers sin lógica de negocio, reutilizando servicios
- [ ] Tipos GraphQL propios, sin entidades expuestas
- [ ] Inputs y args validados, con límites de paginación
- [ ] Nullability explícita
- [ ] DataLoader para relaciones, un juego por petición
- [ ] Guards, `@CurrentUser` y throttler adaptados al contexto GraphQL
- [ ] Autorización también en campos resueltos sensibles
- [ ] Límite de profundidad (y de complejidad si hay listas anidadas)
- [ ] Introspección y stack traces desactivados en producción
- [ ] Errores con `extensions.code` estable mediante el filtro multicontexto
- [ ] Cambios del esquema compatibles o deprecados
