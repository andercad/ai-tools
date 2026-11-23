# Convenciones estándar

Valores por defecto de estructura, nombres y estilo. Si el `CLAUDE.md` del proyecto define otra organización, prevalece.

## Estructura de paquetes

Por defecto, **paquetes por funcionalidad** (no por capa técnica global):

```
src/main/java/com/example/app/
  Application.java
  user/
    UserController.java
    UserService.java
    UserRepository.java
    UserEntity.java
    UserMapper.java
    dto/
      CreateUserRequest.java
      UpdateUserRequest.java
      UserResponse.java
  order/
    ...
  common/
    config/
    error/
    security/
    web/
src/main/resources/
  application.yml
  application-{perfil}.yml
  db/migration/          ← Flyway (o db/changelog para Liquibase)
src/test/java/com/example/app/
  user/
    UserServiceTest.java
    UserControllerTest.java
    UserRepositoryTest.java
```

Reglas independientes de la estructura concreta:

- La clase `@SpringBootApplication` en el paquete raíz, para que el escaneo de componentes cubra todos los subpaquetes.
- Visibilidad mínima: las clases internas de una funcionalidad pueden ser *package-private*; solo es `public` lo que usan otras funcionalidades (ver [structure.md](structure.md)).
- Sin dependencias cíclicas entre paquetes de funcionalidad.

## Nombres

- **Paquetes**: minúsculas, sin guiones bajos (`com.example.app.orderitem`).
- **Clases**: PascalCase con sufijo descriptivo:
  - Controladores: `UserController`
  - Servicios: `UserService`
  - Repositorios: `UserRepository`
  - Entidades: `UserEntity` (o el nombre de dominio, según el proyecto)
  - DTOs: `CreateUserRequest`, `UpdateUserRequest`, `UserResponse`
  - Mappers: `UserMapper`
  - Configuración: `SecurityConfig`, `UserProperties`
  - Excepciones: `UserNotFoundException`
  - Manejadores de errores: `GlobalExceptionHandler`
  - Filtros: `CorrelationIdFilter`
  - GraphQL: `UserGraphqlController`
  - Mensajería: `OrderEventsListener`, `OrderCreatedEvent`
- **Interfaces**: sin prefijo `I` ni sufijo `Impl` salvo necesidad real; si hay varias implementaciones, nómbralas por su diferencia (`JpaUserRepository`, `StripePaymentGateway`).
- **Métodos y variables**: camelCase. **Constantes**: `UPPER_SNAKE_CASE`.
- **Tests**: `<Clase>Test` (unitarios y slices), `<Clase>IT` (integración, si el proyecto los separa).

## Orden de miembros en clases

```java
public class UserService {

    // 1. Constantes (static final)
    private static final int MAX_PAGE_SIZE = 100;

    // 2. Logger
    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    // 3. Dependencias (final) — inyectadas por constructor
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    // 4. Constructor
    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    // 5. Métodos públicos de lectura
    // 6. Métodos públicos de escritura
    // 7. Métodos privados
}
```

En controladores: constructor, endpoints de lectura (`GET`) y después los de escritura (`POST`, `PUT`, `PATCH`, `DELETE`).

## Records, tipos y nulos

- **Records** para DTOs, eventos, configuración (`@ConfigurationProperties`) y valores inmutables. **No** para entidades JPA.
- Usa `Optional` solo como tipo de retorno de búsquedas; no como campo, parámetro ni en colecciones.
- Si el proyecto usa anotaciones de nulabilidad (JSpecify en Spring Boot 4, u otras), aplícalas de forma consistente.
- Colecciones vacías en lugar de `null`.
- Tipos explícitos en APIs públicas; `var` solo cuando el tipo es evidente en la propia línea.

## Lombok y MapStruct

Su uso lo decide el proyecto:

- **Lombok**: si se usa, evita `@Data` y `@EqualsAndHashCode`/`@ToString` sin configurar en entidades JPA (rompen `equals`/`hashCode` y provocan cargas perezosas en `toString`). Prefiere records a `@Value`.
- **MapStruct**: si se usa, para mapeos repetitivos; para mapeos sencillos, un método explícito es suficiente (ver [services.md](services.md)).

## Documentación del código

- **Javadoc** conciso en clases públicas, métodos públicos no triviales y contratos (interfaces, DTOs de API), si `docs: javadoc`.
- No documentes lo evidente ni repitas el nombre del método.
- `@throws` para las excepciones de negocio que el método lanza intencionadamente.
