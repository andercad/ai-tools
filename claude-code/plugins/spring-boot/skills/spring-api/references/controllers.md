
# Controladores y documentación de la API

Esta skill cubre la API REST con Spring MVC. Para GraphQL ver `spring-graphql`; para listeners de mensajes, `spring-integration`. Si el proyecto usa WebFlux, aplica los mismos principios con tipos reactivos (`Mono`/`Flux`) y sin bloquear.

## Reglas

- `@RestController` + `@RequestMapping("/api/<recurso>")`, rutas en kebab-case y plural (`/api/users`, `/api/order-items`).
- Cada controlador gestiona un único recurso.
- Los controladores **no contienen lógica de negocio ni `@Transactional`**: adaptan HTTP y delegan en servicios.
- Entrada con DTOs validados (`@Valid`), salida con DTOs de respuesta. Nunca entidades en ninguno de los dos sentidos.
- Visibilidad de paquete para el controlador y sus métodos si las convenciones del proyecto lo permiten (Spring no necesita que sean `public`).

```java
@RestController
@RequestMapping("/api/users")
@Tag(name = "Users")
class UserController {

    private final UserService userService;

    UserController(UserService userService) {
        this.userService = userService;
    }

    // --- Lectura ---
    @GetMapping
    @Operation(summary = "Lista paginada de usuarios")
    PagedResponse<UserResponse> findAll(@ParameterObject @PageableDefault(size = 20, sort = "createdAt") Pageable pageable) {
        return userService.findAll(pageable);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Obtiene un usuario por id")
    @ApiResponse(responseCode = "200", description = "Usuario encontrado")
    @ApiResponse(responseCode = "404", description = "Usuario no encontrado")
    UserResponse findById(@PathVariable UUID id) {
        return userService.findById(id);
    }

    // --- Escritura ---
    @PostMapping
    @Operation(summary = "Crea un usuario")
    ResponseEntity<UserResponse> create(@Valid @RequestBody CreateUserRequest request) {
        UserResponse created = userService.create(request);
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}").buildAndExpand(created.id()).toUri();
        return ResponseEntity.created(location).body(created);
    }

    @PatchMapping("/{id}")
    @Operation(summary = "Actualiza parcialmente un usuario")
    UserResponse update(@PathVariable UUID id, @Valid @RequestBody UpdateUserRequest request) {
        return userService.update(id, request);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    @Operation(summary = "Elimina un usuario")
    void delete(@PathVariable UUID id) {
        userService.delete(id);
    }
}
```

## Códigos de estado

| Operación                        | Código | Cómo                                                    |
| -------------------------------- | ------ | ------------------------------------------------------- |
| `GET` correcto                   | 200    | Devolver el DTO                                         |
| `POST` que crea                  | 201    | `ResponseEntity.created(location).body(...)`            |
| `POST` que no crea (acción)      | 200/202 | Devolver el DTO o `ResponseEntity.accepted()`           |
| `DELETE`/`PUT` sin cuerpo        | 204    | `@ResponseStatus(HttpStatus.NO_CONTENT)`                |
| Recurso no encontrado            | 404    | El servicio lanza una excepción; la traduce el handler global |
| Conflicto (duplicado, versión)   | 409    | Excepción traducida en el handler global                |

- No construyas respuestas de error en el controlador: lanza excepciones y deja que las traduzca `@RestControllerAdvice` (ver `spring-api`).
- `ResponseEntity` solo cuando necesitas fijar estado dinámico o cabeceras; en el resto de casos, devuelve el DTO.

## Parámetros

- `@PathVariable UUID id`: el tipo hace la conversión; un valor inválido produce 400. Usa UUID para identificadores públicos (ver `spring-security`).
- Filtros de búsqueda agrupados en un record validado con `@Valid @ModelAttribute` (o `@ParameterObject` para documentarlo), en lugar de muchos `@RequestParam` sueltos.
- Validaciones sobre `@PathVariable`/`@RequestParam` (`@Min`, `@Size`...): ver `spring-api`.
- Usuario autenticado con `@AuthenticationPrincipal` (ver `spring-security`), nunca un `userId` recibido del cliente para decidir permisos.
- Evita `HttpServletRequest`/`HttpServletResponse` en la firma salvo necesidad real.

## Paginación

- `Pageable` con valores por defecto y un **tamaño máximo** global para evitar consultas costosas:

```yaml
spring:
  data:
    web:
      pageable:
        default-page-size: 20
        max-page-size: 100
```

- Valida que los campos de ordenación (`sort`) pertenecen a una lista permitida: Spring Data los traduce a la consulta y un campo no previsto puede exponer columnas internas o provocar errores (ver `spring-security`).
- No devuelvas `Page<T>` directamente: su serialización es una estructura interna de Spring Data que puede cambiar entre versiones. Usa un DTO de página propio (el servicio lo construye a partir del `Page`) o el modo de serialización estable (`@EnableSpringDataWebSupport(pageSerializationMode = VIA_DTO)` en las versiones que lo soportan):

```java
public record PagedResponse<T>(List<T> content, int page, int size, long totalElements, int totalPages) {

    public static <T> PagedResponse<T> from(Page<T> page) {
        return new PagedResponse<>(page.getContent(), page.getNumber(), page.getSize(),
                page.getTotalElements(), page.getTotalPages());
    }
}
```

## Versionado de la API

- Define una estrategia (en la ruta `/api/v1/...`, en una cabecera o en el tipo de medio) según las convenciones del proyecto y aplícala de forma consistente.
- Spring Framework 7 incluye soporte nativo de versionado de API (atributo `version` en los mapeos y configuración asociada); úsalo solo si la versión instalada lo ofrece y las convenciones del proyecto lo adoptan.
- Los cambios incompatibles van a una versión nueva; los compatibles (añadir campos opcionales) no requieren versión.

## Documentación con springdoc-openapi

- `@Tag` en el controlador, `@Operation` en cada endpoint y `@ApiResponse` para los códigos relevantes (especialmente los de error).
- `@Schema` en los records de DTO cuando el nombre o el ejemplo no sean evidentes.
- Esquema de seguridad declarado una vez (`@SecurityScheme` / `OpenAPI` bean) y aplicado a los endpoints protegidos.
- Exponer Swagger UI y `/v3/api-docs` es una decisión de cada proyecto. Por defecto, deshabilitado en producción:

```yaml
# application-prod.yml
springdoc:
  api-docs:
    enabled: false
  swagger-ui:
    enabled: false
```

- Si se necesita en producción, protégelo con autenticación o en una red interna.
- Comprueba la versión de springdoc compatible con la versión de Spring Boot del proyecto.

## Checklist

- [ ] Un recurso por controlador, rutas en kebab-case
- [ ] Sin lógica de negocio ni `@Transactional` en el controlador
- [ ] `@Valid` en todos los `@RequestBody`
- [ ] DTOs de entrada y de salida, nunca entidades
- [ ] 201 con `Location` al crear, 204 en borrados sin cuerpo
- [ ] Errores lanzados como excepciones, no construidos en el controlador
- [ ] Paginación con tamaño máximo y ordenación controlada
- [ ] Endpoints documentados; Swagger deshabilitado o protegido en producción
