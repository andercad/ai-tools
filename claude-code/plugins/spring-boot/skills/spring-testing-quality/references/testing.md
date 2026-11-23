
# Testing

## Reglas

- **JUnit 5**, **AssertJ** para aserciones y **Mockito** para dobles. No mezcles JUnit 4 ni Hamcrest si el proyecto usa AssertJ.
- Tests junto al paquete de la clase probada (`src/test/java/.../user/UserServiceTest.java`).
- Nombres descriptivos: `shouldThrowNotFoundWhenUserDoesNotExist()` o `@DisplayName`, según convenciones del proyecto.
- Prueba **comportamiento** (resultado, excepción, interacción relevante), no detalles internos.
- Usa el **test de menor alcance** que demuestre el comportamiento: unitario → slice → integración.
- **Por defecto, no crees tests** al generar código, salvo que se solicite o `tests` sea `required` en `## Convenciones Spring Boot` del `CLAUDE.md`.

## Cobertura

La cobertura exigida la define la clave `coverage` de `## Convenciones Spring Boot` en el `CLAUDE.md` (o la petición concreta), medida con JaCoCo u otra herramienta del proyecto. Si se pide 100 %, aplícalo al código nuevo o modificado sin tests triviales que solo ejecutan líneas.

## Elegir el tipo de test

| Qué pruebas                                  | Tipo                                   | Arranca                         |
| -------------------------------------------- | -------------------------------------- | ------------------------------- |
| Lógica de servicio, mappers, utilidades      | Unitario (sin Spring)                  | Nada                            |
| Controlador: rutas, validación, JSON, errores, seguridad | `@WebMvcTest`              | Solo la capa web                |
| Repositorio: consultas, mapeo, restricciones | `@DataJpaTest` + Testcontainers        | Solo JPA                        |
| Serialización JSON                           | `@JsonTest`                            | Solo Jackson                    |
| Flujo completo                               | `@SpringBootTest` + Testcontainers     | Todo el contexto                |

Las anotaciones de los slices cambiaron de módulo/paquete con la modularización de Spring Boot 4; usa las del proyecto y la versión instalada.

## Test unitario de servicio (sin Spring)

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private PasswordEncoder passwordEncoder;

    private UserService userService;

    @BeforeEach
    void setUp() {
        userService = new UserService(userRepository, passwordEncoder, new UserMapper());
    }

    @Test
    void shouldThrowNotFoundWhenUserDoesNotExist() {
        UUID id = UUID.randomUUID();
        given(userRepository.findById(id)).willReturn(Optional.empty());

        assertThatThrownBy(() -> userService.findById(id))
                .isInstanceOf(UserNotFoundException.class);
    }

    @Test
    void shouldRejectDuplicatedEmail() {
        given(userRepository.existsByEmail("a@b.com")).willReturn(true);

        assertThatThrownBy(() -> userService.create(new CreateUserRequest("a@b.com", "password123", ...)))
                .isInstanceOf(EmailAlreadyRegisteredException.class);
        then(userRepository).should(never()).save(any());
    }
}
```

- Con inyección por constructor, el servicio se instancia directamente: rápido y sin contexto de Spring.
- `@Transactional`, `@PreAuthorize` y otras anotaciones por proxy **no** actúan en tests unitarios; se prueban en slices o integración.
- Evita `@InjectMocks` si oculta qué dependencias recibe la clase; el constructor explícito es más claro.

## Test de controlador (@WebMvcTest)

```java
@WebMvcTest(UserController.class)
@Import(SecurityConfig.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UserService userService;

    @Test
    void shouldReturn400WhenEmailIsInvalid() throws Exception {
        mockMvc.perform(post("/api/users")
                        .with(jwt())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"email": "not-an-email", "password": "password123"}
                                """))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }

    @Test
    void shouldReturn401WithoutToken() throws Exception {
        mockMvc.perform(get("/api/users/{id}", UUID.randomUUID()))
                .andExpect(status().isUnauthorized());
    }
}
```

- **`@MockitoBean`** sustituye a `@MockBean` (deprecado en Spring Boot 3.4 y eliminado en Spring Boot 4). Usa la anotación disponible en la versión instalada.
- Importa la configuración de seguridad real para probar 401/403; `jwt()`/`@WithMockUser` de `spring-security-test` simulan el usuario.
- En versiones recientes existe `MockMvcTester` (aserciones AssertJ) y `RestTestClient`; úsalos si el proyecto los adopta.
- Prueba en el controlador lo que es suyo: rutas, códigos de estado, validación, formato JSON y de error, seguridad. La lógica de negocio va en los tests del servicio.

## Test de repositorio (@DataJpaTest + Testcontainers)

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class UserRepositoryTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldRejectDuplicatedEmail() {
        userRepository.saveAndFlush(new UserEntity("a@b.com", "hash"));

        assertThatThrownBy(() -> userRepository.saveAndFlush(new UserEntity("a@b.com", "hash")))
                .isInstanceOf(DataIntegrityViolationException.class);
    }
}
```

- **Base de datos real del mismo motor** que producción (Testcontainers), no H2: dialecto, restricciones, tipos y SQL nativo se comportan distinto.
- `@ServiceConnection` configura la conexión automáticamente; las migraciones de Flyway/Liquibase se ejecutan, validando también el esquema.
- `saveAndFlush` (o `flush`) para que las restricciones se comprueben dentro del test.
- `@DataJpaTest` es transaccional y hace rollback al final de cada test.
- Reutiliza contenedores entre clases de test (contenedor estático compartido o configuración de Testcontainers) para que la suite sea rápida.

## Integración completa (@SpringBootTest)

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class OrderFlowIT {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired
    private TestRestTemplate restTemplate; // o RestTestClient / WebTestClient según versión

    @Test
    void shouldCreateAndRetrieveOrder() { ... }
}
```

- Pocos tests de este tipo, para flujos críticos: son lentos.
- No uses `@Transactional` en estos tests si quieres probar el comportamiento transaccional real; limpia los datos en su lugar.
- Cada `@MockitoBean` distinto crea un contexto de Spring nuevo y ralentiza la suite: agrupa la configuración de mocks.
- Servicios externos simulados con WireMock o MockWebServer, no con mocks del cliente HTTP (ver `spring-integration`).

## Seguridad en tests

- Casos mínimos por endpoint protegido: 401 sin credenciales, 403 sin permisos, 404 ante un recurso ajeno, éxito con permisos.
- Prueba las reglas de `@PreAuthorize` con un test que cargue la seguridad de método (slice o integración), no solo el servicio aislado.

## Checklist

- [ ] JUnit 5 + AssertJ + Mockito, sin mezclar librerías antiguas
- [ ] Tipo de test de menor alcance suficiente
- [ ] Unitarios sin contexto de Spring
- [ ] `@MockitoBean` (no `@MockBean`) en la versión que corresponda
- [ ] Repositorios con base de datos real (Testcontainers + `@ServiceConnection`)
- [ ] Casos de éxito, error, validación y seguridad (401/403/404)
- [ ] Contextos reutilizados; pocos tests `@SpringBootTest`
- [ ] Cobertura según convenciones del proyecto o petición
