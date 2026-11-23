
# DTOs y validación

## Reglas

- DTOs como **records**, en el subpaquete `dto/` de la funcionalidad.
- DTOs separados por intención: `CreateXRequest`, `UpdateXRequest`, `XResponse`, `XFilter`.
- Validación con Bean Validation (`jakarta.validation.constraints.*`), requiere `org.springframework.boot:spring-boot-starter-validation`.
- `@Valid` en cada `@RequestBody` (y en argumentos de GraphQL y payloads de mensajes cuando se validen ahí).
- **Nunca** uses una entidad JPA como DTO de entrada ni de salida.
- La validación del DTO es la frontera de seguridad de entrada: todo dato externo pasa por ella. La asignación masiva y otros riesgos se tratan en `spring-security`.

## DTO de entrada

```java
public record CreateUserRequest(

        @NotBlank
        @Email
        @Size(max = 254)
        String email,

        @NotBlank
        @Size(min = 8, max = 128)
        String password,

        @NotNull
        @Valid
        AddressRequest address,

        @NotNull
        @Size(min = 1, max = 20)
        List<@NotBlank @Size(max = 50) String> tags
) {
    // Normalización sencilla en el constructor compacto
    public CreateUserRequest {
        email = email == null ? null : email.strip().toLowerCase(Locale.ROOT);
    }
}
```

- **Límites en todo** campo de tamaño variable (`@Size`, `@Max`, `@DecimalMax`): sin ellos, un solo campo puede consumir memoria o CPU.
- `@NotBlank` para textos obligatorios (`@NotNull` acepta `""`).
- **Objetos anidados**: `@Valid` en el campo; sin él, el contenido anidado no se valida.
- **Elementos de colecciones**: restricciones en el tipo genérico (`List<@NotBlank String>`).
- No uses tipos primitivos para campos opcionales en DTOs de entrada: un `int` ausente llega como `0` y no se puede distinguir de un valor enviado. Usa `Integer` con `@NotNull` si es obligatorio.

## Actualizaciones parciales

```java
public record UpdateUserRequest(
        @Size(max = 100) String displayName,
        @Size(max = 500) String bio
) { }
```

- En un `PATCH`, `null` significa "no se envía". Si el contrato necesita distinguir "no enviado" de "poner a null", usa `Optional<String>` en el DTO de entrada solo para ese caso, o JSON Merge Patch, según las convenciones del proyecto.
- El servicio copia solo los campos presentes, campo a campo (ver `spring-structure-services`).

## Validación de parámetros

- Restricciones directamente sobre `@PathVariable`/`@RequestParam` (`@Min`, `@Max`, `@Size`): las versiones recientes de Spring MVC validan estos parámetros y responden 400 (`HandlerMethodValidationException`). En versiones antiguas hacía falta `@Validated` en la clase: comprueba la versión instalada.
- Validación de métodos en servicios: `@Validated` en la clase y restricciones en los parámetros. Úsala con moderación: la validación de entrada pertenece al borde (controlador).

## Grupos

Usa grupos solo cuando un mismo DTO necesite reglas distintas según la operación y no compense crear dos DTOs. Por defecto, mejor **dos DTOs**: es más legible.

## Restricciones personalizadas

```java
@Target({ ElementType.FIELD, ElementType.PARAMETER, ElementType.RECORD_COMPONENT })
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = IbanValidator.class)
public @interface ValidIban {
    String message() default "{validation.iban.invalid}";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}

class IbanValidator implements ConstraintValidator<ValidIban, String> {

    @Override
    public boolean isValid(String value, ConstraintValidatorContext context) {
        if (value == null) {
            return true; // la obligatoriedad la decide @NotNull/@NotBlank
        }
        return IbanChecker.isValid(value);
    }
}
```

- El validador devuelve `true` para `null`: combinable con `@NotNull`.
- Restricciones entre campos (`password` y `confirmPassword`): restricción a nivel de clase/record.
- Los validadores pueden ser beans e inyectar dependencias, pero **no** pongas reglas de negocio con acceso a base de datos (p. ej. "email único") en un validador: pertenecen al servicio y las garantiza un índice único (ver `spring-persistence`).
- Mensajes en `ValidationMessages.properties` si la API está internacionalizada.

## Jackson

Spring Boot 4 usa **Jackson 3** (paquete `tools.jackson`, `JsonMapper` inmutable, excepciones no comprobadas); Spring Boot 3.x usa Jackson 2 (`com.fasterxml.jackson`). Las anotaciones (`@JsonProperty`, `@JsonFormat`...) siguen en `com.fasterxml.jackson.annotation` en ambos. Usa la API de la versión instalada.

- Configuración por propiedades (`spring.jackson.*`) o por los *customizers* de la versión instalada; no crees un `ObjectMapper`/`JsonMapper` propio que sustituya al autoconfigurado salvo necesidad.
- **Fechas**: `Instant`/`OffsetDateTime` en ISO-8601 para la API. Jackson 3 serializa fechas como texto ISO por defecto; en Jackson 2 hay que desactivar `WRITE_DATES_AS_TIMESTAMPS`. Revisa el contrato al migrar.
- **Propiedades desconocidas**: decide la política con las convenciones del proyecto. Rechazarlas (`FAIL_ON_UNKNOWN_PROPERTIES`) protege frente a campos inesperados; aceptarlas facilita la evolución de clientes. Lo que nunca debe pasar es que un campo desconocido llegue a la entidad (ver `spring-security`).
- **Nunca** actives el tipado polimórfico global (*default typing*) con datos de entrada: permite instanciar clases arbitrarias (ver `spring-security`).

## DTOs de respuesta

```java
public record UserResponse(UUID id, String email, Instant createdAt) { }
```

- Solo los campos que el cliente necesita: un campo nuevo en la entidad no debe aparecer en la API sin una decisión consciente.
- Sin datos sensibles (hashes, tokens, campos internos).

## Checklist

- [ ] DTOs como records separados por intención
- [ ] `@Valid` en cuerpos de entrada y en objetos anidados
- [ ] Límites de tamaño en todos los campos variables
- [ ] Restricciones en los elementos de colecciones
- [ ] Wrappers en lugar de primitivos para campos opcionales
- [ ] Reglas de negocio con base de datos fuera de los validadores
- [ ] API de Jackson de la versión instalada; fechas ISO-8601
- [ ] Sin tipado polimórfico global; sin entidades en la API
