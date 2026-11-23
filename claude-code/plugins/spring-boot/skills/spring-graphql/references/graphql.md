
# GraphQL (Spring for GraphQL)

Spring for GraphQL es **schema-first**: el esquema se escribe en ficheros `.graphqls` y los controladores lo implementan. Si el proyecto usa otra librería (p. ej. Netflix DGS), aplica los mismos principios con su API.

## Principios

- Los controladores GraphQL son la capa de transporte: **sin lógica de negocio**, reutilizan los mismos servicios que la API REST (ver `spring-structure-services`).
- Nunca expongas entidades JPA como tipos GraphQL: devuelve DTOs/records.
- Todo argumento de entrada se valida.
- Autorización por operación **y por campo/recurso**: en GraphQL un cliente puede llegar a un dato por varios caminos del grafo.

## Esquema

```graphql
# src/main/resources/graphql/schema.graphqls
type Query {
    user(id: ID!): User
    users(page: Int = 0, size: Int = 20): UserPage!
}

type Mutation {
    createUser(input: CreateUserInput!): User!
}

type User {
    id: ID!
    email: String!
    createdAt: String!
    orders: [Order!]!
}

input CreateUserInput {
    email: String!
    password: String!
}
```

- Nulabilidad deliberada: `!` solo donde el valor nunca falta.
- Mutations con un único argumento `input`.
- Spring for GraphQL comprueba al arrancar el mapeo entre esquema y controladores (inspección del esquema); revisa sus avisos de campos sin implementar.

## Controladores

```java
@Controller
class UserGraphqlController {

    private final UserService userService;
    private final OrderService orderService;

    UserGraphqlController(UserService userService, OrderService orderService) {
        this.userService = userService;
        this.orderService = orderService;
    }

    // --- Queries ---
    @QueryMapping
    UserResponse user(@Argument UUID id) {
        return userService.findById(id);
    }

    @QueryMapping
    @PreAuthorize("hasRole('ADMIN')")
    PagedResponse<UserResponse> users(@Argument @Min(0) int page, @Argument @Min(1) @Max(100) int size) {
        return userService.findAll(PageRequest.of(page, size));
    }

    // --- Mutations ---
    @MutationMapping
    UserResponse createUser(@Argument @Valid CreateUserRequest input) {
        return userService.create(input);
    }

    // --- Campos resueltos (en lote, sin N+1) ---
    @BatchMapping(typeName = "User", field = "orders")
    Map<UserResponse, List<OrderResponse>> orders(List<UserResponse> users) {
        return orderService.findByUsers(users); // una sola consulta para todos los usuarios
    }
}
```

- Orden de miembros: constructor, queries, mutations, campos resueltos.
- Validación de argumentos con Bean Validation (`@Valid`, restricciones en `@Argument`), con límites de paginación.
- `@SchemaMapping` para campos resueltos individuales; **`@BatchMapping`** cuando el campo se resuelve para listas de objetos.

## N+1: @BatchMapping y DataLoader

Sin carga en lote, `users { orders { ... } }` lanza una consulta de pedidos por cada usuario.

- `@BatchMapping` agrupa los objetos padre y resuelve el campo para todos en una llamada; Spring for GraphQL usa DataLoader por debajo, con un registro **por petición** (sin caché compartida entre usuarios).
- El método del servicio que carga en lote aplica las mismas reglas de autorización que el resto.
- El resultado debe contener una entrada para cada objeto padre (lista vacía si no hay datos).

## Seguridad

- El endpoint `/graphql` pasa por la `SecurityFilterChain` (autenticación); la autorización fina, con `@PreAuthorize` en los métodos del controlador o del servicio (ver `spring-security`).
- Protege también los campos resueltos (`@SchemaMapping`/`@BatchMapping`) que exponen datos sensibles: el guard de la query raíz no basta si el tipo es alcanzable desde otra query.
- **Límites de las consultas**: GraphQL permite consultas arbitrariamente profundas y costosas. Registra las instrumentaciones de graphql-java:

```java
@Bean
MaxQueryDepthInstrumentation maxQueryDepthInstrumentation() {
    return new MaxQueryDepthInstrumentation(10);
}

@Bean
MaxQueryComplexityInstrumentation maxQueryComplexityInstrumentation() {
    return new MaxQueryComplexityInstrumentation(200);
}
```

- **Introspección y GraphiQL** solo fuera de producción:

```yaml
# application-prod.yml
spring:
  graphql:
    graphiql:
      enabled: false
    schema:
      introspection:
        enabled: false
```

  Comprueba los nombres de las propiedades en la versión instalada.
- Si el driver lo permite, desactiva o limita el *batching* de operaciones y considera *persisted queries* para clientes propios.
- Rate limiting y CSRF: ver `spring-security` (las peticiones GraphQL con cookies necesitan protección CSRF).

## Errores

- En GraphQL los errores van en el array `errors` (habitualmente con HTTP 200), con una clasificación en `extensions.classification`.
- Traduce las excepciones de negocio con `@GraphQlExceptionHandler` en un `@ControllerAdvice` (versiones recientes) o con un `DataFetcherExceptionResolverAdapter`:

```java
@ControllerAdvice
class GraphqlExceptionHandler {

    @GraphQlExceptionHandler
    GraphQLError handle(NotFoundException ex) {
        return GraphQLError.newError()
                .errorType(ErrorType.NOT_FOUND)
                .message(ex.getMessage())
                .extensions(Map.of("code", ex.getCode()))
                .build();
    }
}
```

- Clasificaciones estables (`NOT_FOUND`, `BAD_REQUEST`, `FORBIDDEN`, `UNAUTHORIZED`, `INTERNAL_ERROR`) y un `code` propio en `extensions`, para que los clientes no dependan del texto.
- Las excepciones no controladas se devuelven como `INTERNAL_ERROR` sin detalles; regístralas en el log.

## Paginación

- Listas siempre paginadas y con tamaño máximo.
- Spring for GraphQL soporta paginación por cursor (*connections*) integrada con el *scroll* de Spring Data; úsala para listas grandes según las convenciones del proyecto.

## Evolución del esquema

- No elimines ni renombres campos usados por clientes: márcalos con `@deprecated(reason: "...")` y retíralos cuando dejen de usarse.
- Añadir campos opcionales y tipos nuevos es compatible; cambiar la nulabilidad puede romper clientes.

## Subscriptions

- Requieren transporte WebSocket (o SSE, según versión) y tipos de retorno `Flux`.
- Autentica en la conexión y vuelve a autorizar por evento. Con varias réplicas, la fuente de eventos debe ser compartida (broker).

## Tests

```java
@GraphQlTest(UserGraphqlController.class)
class UserGraphqlControllerTest {

    @Autowired
    private GraphQlTester graphQlTester;

    @MockitoBean
    private UserService userService;

    @MockitoBean
    private OrderService orderService;

    @Test
    void shouldReturnNotFoundError() {
        given(userService.findById(any())).willThrow(new UserNotFoundException(UUID.randomUUID()));

        graphQlTester.document("query { user(id: \"6f1c0c1e-8a59-4c51-9a8e-0e6f1b2a3c4d\") { id } }")
                .execute()
                .errors()
                .expect(error -> error.getErrorType() == ErrorType.NOT_FOUND);
    }
}
```

- `@GraphQlTest` para la capa GraphQL; `HttpGraphQlTester` con `@SpringBootTest` para probar también la seguridad HTTP.
- Documentos de consulta en `src/test/resources/graphql-test` para consultas largas.

## Checklist

- [ ] Esquema con nulabilidad deliberada; mutations con `input`
- [ ] Controladores sin lógica de negocio, devolviendo DTOs
- [ ] Argumentos validados con límites de paginación
- [ ] `@BatchMapping` en campos de listas (sin N+1)
- [ ] `@PreAuthorize` en operaciones y campos sensibles
- [ ] Límites de profundidad y complejidad
- [ ] Introspección y GraphiQL desactivados en producción
- [ ] Errores con clasificación y `code` estables, sin detalles internos
- [ ] Cambios del esquema compatibles o deprecados
