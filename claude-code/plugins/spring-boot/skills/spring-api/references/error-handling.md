
# Manejo de errores

## Reglas

- **Nunca** `catch` vacío, `e.printStackTrace()` ni capturar `Exception` para continuar como si nada.
- Errores de negocio: excepciones propias **unchecked** de dominio, lanzadas desde servicios (ver `spring-structure-services`).
- Errores inesperados: se propagan hasta el manejador global, que los registra y devuelve 500.
- **No expongas** stack traces, mensajes de base de datos, nombres de clases, rutas internas ni configuración en las respuestas.
- Solo captura una excepción si vas a hacer algo útil: traducirla, añadir contexto o recuperarte. Al relanzar, conserva la causa (`new X(..., cause)`).
- Un formato de error único en toda la API: **`ProblemDetail`** (RFC 9457, `application/problem+json`), salvo que las convenciones del proyecto definan otro.

## Excepciones de dominio

```java
public abstract class DomainException extends RuntimeException {

    private final String code;

    protected DomainException(String code, String message) {
        super(message);
        this.code = code;
    }

    public String getCode() {
        return code;
    }
}

public class NotFoundException extends DomainException { ... }   // → 404
public class ConflictException extends DomainException { ... }   // → 409
public class BusinessRuleException extends DomainException { ... } // → 422
```

- Una pequeña jerarquía por tipo de resultado HTTP simplifica el mapeo, sin acoplar los servicios a HTTP.
- Evita `ResponseStatusException` en servicios reutilizados desde GraphQL o mensajería.

## Manejador global

```java
@RestControllerAdvice
class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(NotFoundException.class)
    ProblemDetail handleNotFound(NotFoundException ex) {
        return problem(HttpStatus.NOT_FOUND, ex.getCode(), ex.getMessage());
    }

    @ExceptionHandler(ConflictException.class)
    ProblemDetail handleConflict(ConflictException ex) {
        return problem(HttpStatus.CONFLICT, ex.getCode(), ex.getMessage());
    }

    @ExceptionHandler(BusinessRuleException.class)
    ProblemDetail handleBusinessRule(BusinessRuleException ex) {
        return problem(HttpStatus.UNPROCESSABLE_ENTITY, ex.getCode(), ex.getMessage());
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    ProblemDetail handleIntegrity(DataIntegrityViolationException ex) {
        log.warn("Data integrity violation", ex);            // detalle solo en el log
        return problem(HttpStatus.CONFLICT, "DATA_CONFLICT", "The resource conflicts with existing data");
    }

    @ExceptionHandler(ObjectOptimisticLockingFailureException.class)
    ProblemDetail handleOptimisticLock(ObjectOptimisticLockingFailureException ex) {
        return problem(HttpStatus.CONFLICT, "CONCURRENT_MODIFICATION", "The resource was modified by another request");
    }

    @ExceptionHandler(AccessDeniedException.class)
    void handleAccessDenied(AccessDeniedException ex) {
        throw ex; // dejar que Spring Security responda 401/403
    }

    @ExceptionHandler(Exception.class)
    ProblemDetail handleUnexpected(Exception ex) {
        log.error("Unexpected error", ex);
        return problem(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", "Unexpected error");
    }

    private ProblemDetail problem(HttpStatus status, String code, String detail) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(status, detail);
        pd.setProperty("code", code);
        pd.setProperty("correlationId", MDC.get("correlationId"));
        return pd;
    }
}
```

- **Extender `ResponseEntityExceptionHandler`** hace que las excepciones propias de Spring MVC (método no soportado, cuerpo ilegible, tipo de parámetro incorrecto, validación...) también respondan con `ProblemDetail` y el código correcto. Alternativa: `spring.mvc.problemdetails.enabled=true`.
- Un manejador genérico de `Exception` **no debe** tragarse `AccessDeniedException`/`AuthenticationException` (que perderían su 401/403) ni las excepciones que ya gestiona `ResponseEntityExceptionHandler`.
- El `detail` de las excepciones de dominio es seguro solo si sus mensajes se han escrito pensando en el cliente; si contienen datos internos, usa un texto fijo por código.
- Incluye un identificador de correlación o de traza para poder localizar el error en los logs.

## Errores de validación

Sobrescribe el tratamiento para devolver los errores por campo con un formato estable:

```java
@Override
protected ResponseEntity<Object> handleMethodArgumentNotValid(MethodArgumentNotValidException ex,
        HttpHeaders headers, HttpStatusCode status, WebRequest request) {
    ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "Validation failed");
    pd.setProperty("code", "VALIDATION_ERROR");
    pd.setProperty("errors", ex.getBindingResult().getFieldErrors().stream()
            .map(e -> Map.of("field", e.getField(), "message", Objects.requireNonNullElse(e.getDefaultMessage(), "invalid")))
            .toList());
    return ResponseEntity.badRequest().body(pd);
}
```

- No devuelvas el valor rechazado (`rejectedValue`): puede contener contraseñas o datos personales.
- Trata también `HandlerMethodValidationException` (validación de parámetros en Spring Framework 6.1+) y `ConstraintViolationException` (validación en servicios con `@Validated`) como 400 con el mismo formato.

## Configuración de producción

```yaml
server:
  error:
    include-stacktrace: never
    include-message: never
    include-binding-errors: never
    include-exception: false
```

Estas propiedades afectan a la respuesta de error por defecto de Spring Boot (`/error`), que sigue usándose para errores fuera de los controladores (filtros, 404 de rutas inexistentes).

## Errores en filtros

Las excepciones lanzadas en un filtro no llegan a `@RestControllerAdvice`. Escribe la respuesta en el propio filtro con el mismo formato `ProblemDetail`, o delega en `HandlerExceptionResolver`. Los errores de autenticación y autorización los gestionan el `AuthenticationEntryPoint` y el `AccessDeniedHandler` de Spring Security: configúralos para responder también con `ProblemDetail` si las convenciones del proyecto lo exigen.

## Errores en GraphQL y mensajería

- **GraphQL**: las excepciones de los controladores GraphQL **no** pasan por `@RestControllerAdvice`. Tradúcelas con `@GraphQlExceptionHandler` o un `DataFetcherExceptionResolver` a errores con `ErrorType` y `extensions.code` estables (ver `spring-graphql`).
- **Mensajería**: no hay respuesta HTTP. La excepción decide reintento o envío a la DLQ según el manejador de errores del listener (ver `spring-integration`). Distingue errores transitorios (reintentar) de permanentes (DLQ directa).

## Checklist

- [ ] Excepciones de dominio unchecked; sin `Exception` genérica para negocio
- [ ] `@RestControllerAdvice` que extiende `ResponseEntityExceptionHandler`
- [ ] `ProblemDetail` con `code` estable y correlación
- [ ] Validación (cuerpo y parámetros) traducida a 400 con errores por campo, sin valores rechazados
- [ ] Integridad y bloqueo optimista traducidos a 409
- [ ] 401/403 de Spring Security no capturados por el manejador genérico
- [ ] Stack traces y mensajes internos solo en logs
- [ ] `server.error.include-*` desactivados
- [ ] Errores de GraphQL y mensajería tratados en sus propios mecanismos
