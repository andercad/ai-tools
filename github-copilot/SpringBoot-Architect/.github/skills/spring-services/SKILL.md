---
name: spring-services
description: 'Servicios Spring: lógica de negocio, @Transactional (límites, readOnly, rollback, propagación, auto-invocación), mapeo entidad → DTO (manual o MapStruct), excepciones de negocio, estado y concurrencia en beans singleton, @Async. Usar cuando: crear o refactorizar un servicio, decidir dónde va una transacción, mapear entidades, lanzar errores de negocio.'
argument-hint: 'Describe el servicio o la lógica de negocio que necesitas implementar.'
---

# Servicios y transacciones

## Reglas

- `@Service` para la lógica de negocio; una única responsabilidad por servicio (ver `spring-solid`).
- Dependencias `private final` por constructor.
- El servicio contiene la lógica; controladores REST, controladores GraphQL y listeners de mensajes la reutilizan.
- Entrada y salida con DTOs (o tipos de dominio); el servicio no devuelve entidades a la capa web.

```java
/**
 * Gestión de usuarios: alta, consulta y actualización.
 */
@Service
@Transactional(readOnly = true)
public class UserService {

    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final UserMapper userMapper;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder, UserMapper userMapper) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.userMapper = userMapper;
    }

    // --- Lectura ---
    public UserResponse findById(UUID id) {
        return userRepository.findById(id)
                .map(userMapper::toResponse)
                .orElseThrow(() -> new UserNotFoundException(id));
    }

    // --- Escritura ---
    @Transactional
    public UserResponse create(CreateUserRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new EmailAlreadyRegisteredException();
        }
        UserEntity user = new UserEntity(request.email(), passwordEncoder.encode(request.password()));
        UserEntity saved = userRepository.save(user);
        log.info("User created: {}", saved.getId()); // nunca el email ni la contraseña
        return userMapper.toResponse(saved);
    }

    @Transactional
    public UserResponse update(UUID id, UpdateUserRequest request) {
        UserEntity user = userRepository.findById(id).orElseThrow(() -> new UserNotFoundException(id));
        if (request.displayName() != null) {
            user.changeDisplayName(request.displayName());
        }
        if (request.bio() != null) {
            user.changeBio(request.bio());
        }
        return userMapper.toResponse(user); // dirty checking: no hace falta save()
    }
}
```

La comprobación de email duplicado reduce errores, pero no evita la carrera entre dos peticiones simultáneas: la garantía la da un índice único, y su violación se traduce a 409 (ver `spring-persistence` y `spring-error-handling`).

## @Transactional

- En la **capa de servicio**, nunca en controladores ni repositorios propios.
- Patrón recomendado: `@Transactional(readOnly = true)` en la clase y `@Transactional` en los métodos de escritura. `readOnly` permite optimizaciones (sin *flush*, posibles réplicas de lectura).
- Usa `org.springframework.transaction.annotation.Transactional` (admite `readOnly`, `propagation`...), no `jakarta.transaction.Transactional`.
- **Funciona por proxy**. Consecuencias:
  - Solo se aplica a llamadas que vienen **de fuera** del bean: una llamada `this.otroMetodo()` dentro de la misma clase **ignora** el `@Transactional` del método llamado (auto-invocación). Si necesitas otro límite transaccional, muévelo a otro bean.
  - Solo en métodos públicos (o no privados, según versión): no la pongas en métodos privados.
- **Rollback**: por defecto solo con excepciones no comprobadas (`RuntimeException`) y `Error`. Una excepción comprobada **confirma** la transacción salvo `rollbackFor`. Usa excepciones de negocio no comprobadas.
- Si capturas una excepción dentro de una transacción y la tragas, la transacción puede quedar marcada solo para rollback y fallar al confirmar (`UnexpectedRollbackException`).
- `Propagation.REQUIRES_NEW` solo con motivo (p. ej. registrar una auditoría que debe persistir aunque falle la operación principal); usa una conexión adicional del pool.
- Transacciones **cortas**: sin llamadas HTTP externas, envío de emails ni publicación en brokers dentro de ellas. Para efectos tras confirmar, usa `@TransactionalEventListener(phase = AFTER_COMMIT)` o el patrón outbox (ver `spring-messaging`).

## Mapeo entidad → DTO

- Mapeo explícito, en un método del mapper o del propio servicio:

```java
@Component
class UserMapper {

    UserResponse toResponse(UserEntity entity) {
        return new UserResponse(entity.getId(), entity.getEmail(), entity.getCreatedAt());
    }
}
```

- Con MapStruct (si las guidelines lo usan): `@Mapper(componentModel = "spring")` y `unmappedTargetPolicy = ReportingPolicy.ERROR` para que un campo nuevo sin mapear rompa la compilación en lugar de quedar vacío.
- Mapea dentro de la transacción: fuera de ella, acceder a una relación perezosa lanza `LazyInitializationException` (con `open-in-view=false`, que es lo correcto; ver `spring-persistence`).
- En actualizaciones, **nunca** mapees el DTO entero sobre la entidad: copia los campos permitidos (ver asignación masiva en `spring-security`).

## Excepciones de negocio

- Excepciones propias **no comprobadas** que expresan el problema de negocio, sin dependencias de HTTP:

```java
public class UserNotFoundException extends NotFoundException {
    public UserNotFoundException(UUID id) {
        super("USER_NOT_FOUND", "User %s not found".formatted(id));
    }
}
```

- Una jerarquía base (`NotFoundException`, `ConflictException`, `BusinessRuleException`) en `common/error`, traducida a HTTP en el manejador global (ver `spring-error-handling`).
- Nunca lances `RuntimeException` o `Exception` genéricas para errores de negocio.
- Alternativa: `ResponseStatusException`/`ErrorResponseException` desde el servicio acopla el dominio a HTTP; úsalas solo si las guidelines lo aceptan.

## Estado y concurrencia

- Los beans son **singleton** por defecto y se ejecutan en varios hilos a la vez: **no** guardes estado de una petición (usuario actual, datos del request) en campos del servicio.
- Pasa el contexto como parámetro o léelo del `SecurityContext` cuando haga falta.
- Evita `@Scope("request")`/`@RequestScope` salvo necesidad.
- Con hilos virtuales activados, evita bloques `synchronized` largos alrededor de I/O; usa `ReentrantLock` si necesitas exclusión (o lo que recomiende la documentación de la versión de Java instalada).

## @Async y eventos

- `@Async` también funciona por proxy (misma limitación de auto-invocación) y necesita `@EnableAsync` y un ejecutor configurado.
- El método `@Async` no participa en la transacción del llamante y pierde el `SecurityContext` salvo configuración.
- Para desacoplar efectos secundarios, prefiere eventos de aplicación (ver `spring-messaging`).

## Checklist

- [ ] Una responsabilidad por servicio; dependencias por constructor
- [ ] `@Transactional(readOnly = true)` en lectura y `@Transactional` en escritura, en el servicio
- [ ] Sin auto-invocación que dependa de `@Transactional`/`@Async`
- [ ] Excepciones de negocio no comprobadas
- [ ] Sin llamadas externas ni publicación de mensajes dentro de la transacción
- [ ] Mapeo explícito dentro de la transacción; nunca DTO entero sobre la entidad
- [ ] Sin estado de la petición en campos del bean
- [ ] Sin datos personales ni secretos en los logs
