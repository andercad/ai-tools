
# Autenticación y autorización

Esta skill cubre **quién es el usuario y qué puede hacer**. La protección del código frente a vulnerabilidades (inyección, SSRF, deserialización, CORS, CSRF, cabeceras, Actuator, dependencias...) está en `spring-security`.

Usa la API de Spring Security de la versión instalada: DSL con lambdas y `SecurityFilterChain` como bean. `WebSecurityConfigurerAdapter` y `authorizeRequests()` ya no existen en las versiones actuales.

## SecurityFilterChain (API stateless con JWT)

```java
@Configuration(proxyBeanMethods = false)
@EnableMethodSecurity
class SecurityConfig {

    @Bean
    SecurityFilterChain apiSecurity(HttpSecurity http) throws Exception {
        http
            .securityMatcher("/api/**")
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(HttpMethod.POST, "/api/auth/login", "/api/auth/refresh").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())               // seguro por defecto
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable())                     // solo porque es stateless con Bearer (ver spring-security)
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
        return http.build();
    }
}
```

- **Seguro por defecto**: termina siempre con `.anyRequest().authenticated()` (o `denyAll()`); los endpoints públicos se enumeran explícitamente.
- Las reglas se evalúan **en orden**: de la más específica a la más general.
- Si hay varias cadenas (API, Actuator, documentación), cada una con su `securityMatcher` y `@Order`.
- Desactivar CSRF solo es correcto si la autenticación es exclusivamente por cabecera `Authorization` y sin cookies (ver `spring-security`).

## Validación de tokens

**Proveedor externo (OIDC: Keycloak, Azure AD, Auth0...)** — opción preferida:

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://idp.example.com/realms/app   # valida firma (JWKS), emisor y expiración
          audiences: app-api                               # valida la audiencia (según versión)
```

- Valida emisor, audiencia y expiración. Si la versión no admite la propiedad de audiencia, añade un validador de `aud` al `JwtDecoder`.
- Mapea los roles/scopes del token a authorities con un `JwtAuthenticationConverter` (los claims de roles varían por proveedor):

```java
@Bean
JwtAuthenticationConverter jwtAuthenticationConverter() {
    JwtGrantedAuthoritiesConverter authorities = new JwtGrantedAuthoritiesConverter();
    authorities.setAuthoritiesClaimName("roles");
    authorities.setAuthorityPrefix("ROLE_");
    JwtAuthenticationConverter converter = new JwtAuthenticationConverter();
    converter.setJwtGrantedAuthoritiesConverter(authorities);
    return converter;
}
```

**Tokens emitidos por la propia aplicación**:

- Clave de firma desde configuración/secretos, nunca en el código (ver `spring-config-observability`). Preferible firma asimétrica (RS256/ES256) si otros servicios validan los tokens.
- Access tokens de vida corta; refresh tokens con **rotación** y **revocación**, guardados con hash.
- Sin datos sensibles en el payload: el JWT está codificado, no cifrado.
- Fija el algoritmo esperado al verificar.

**Aplicación web con sesión** (no API): `formLogin`/`oauth2Login`, sesión con cookie `HttpOnly`/`Secure`/`SameSite` y CSRF **activado**.

## Contraseñas

```java
@Bean
PasswordEncoder passwordEncoder() {
    return PasswordEncoderFactories.createDelegatingPasswordEncoder(); // bcrypt por defecto, con prefijo {id}
}
```

- El `DelegatingPasswordEncoder` permite cambiar de algoritmo sin invalidar los hashes existentes. `Argon2PasswordEncoder` si las convenciones del proyecto lo exigen.
- **Nunca** contraseñas en texto plano, en logs ni en respuestas. `NoOpPasswordEncoder` solo en tests.
- BCrypt usa como máximo 72 bytes: limita la longitud en el DTO.
- En el login, mismo error y tiempo similar ante usuario inexistente o contraseña incorrecta. Limita los intentos (ver rate limiting en `spring-security`).

## Autorización por método

Con `@EnableMethodSecurity`:

```java
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(UUID id) { ... }

@PreAuthorize("hasAuthority('orders:write')")
public OrderResponse create(CreateOrderRequest request) { ... }
```

- Roles (`hasRole('ADMIN')` comprueba la authority `ROLE_ADMIN`) o permisos finos (`hasAuthority('orders:write')`), según el modelo de las convenciones del proyecto.
- `@PreAuthorize` funciona **por proxy**: no se aplica en llamadas internas dentro del mismo bean (como `@Transactional`).
- No construyas expresiones SpEL con datos del usuario (ver `spring-security`).

## Usuario autenticado

```java
@GetMapping("/me")
UserResponse me(@AuthenticationPrincipal Jwt jwt) {
    return userService.findById(UUID.fromString(jwt.getSubject()));
}
```

- Con autenticación propia, un principal propio (`AuthenticatedUser`) con solo lo necesario para autorizar (id, authorities), no la entidad.
- **Nunca** tomes la identidad de un parámetro de la petición (`request.userId()`, `?userId=`) para decidir permisos: tómala siempre del principal autenticado.

## Autorización por recurso

Los roles deciden qué tipo de operación puede hacer un usuario; **no** sobre qué recursos. Comprueba la propiedad o el permiso sobre cada recurso concreto (OWASP API1: Broken Object Level Authorization):

```java
@Transactional(readOnly = true)
public OrderResponse findOrder(UUID orderId, UUID currentUserId) {
    return orderRepository.findByIdAndUserId(orderId, currentUserId) // filtra por propietario
            .map(orderMapper::toResponse)
            .orElseThrow(() -> new OrderNotFoundException(orderId));  // 404: no revela si existe
}
```

Alternativa declarativa con un bean de autorización:

```java
@PreAuthorize("@orderAuthorization.isOwner(#orderId, authentication)")
public OrderResponse findOrder(UUID orderId) { ... }
```

- Aplica la comprobación a **todas** las operaciones sobre el recurso: lectura, edición, borrado, listados, exportaciones y búsquedas.
- UUIDs en rutas públicas reducen la enumeración, pero **no sustituyen** esta comprobación.
- Autorización a nivel de **propiedad**: un usuario puede editar su perfil, pero no su campo `role` (ver asignación masiva en `spring-security`).

## GraphQL y mensajería

- **GraphQL**: el endpoint `/graphql` pasa por la `SecurityFilterChain`; la autorización fina se aplica con `@PreAuthorize` en los métodos de los controladores GraphQL o de los servicios, también en los `@SchemaMapping` que exponen datos sensibles (ver `spring-graphql`).
- **Mensajería**: los listeners no pasan por la `SecurityFilterChain` y no tienen `SecurityContext`. Si un mensaje actúa en nombre de un usuario, incluye su identidad en el mensaje y vuelve a comprobar la autorización en el consumidor (ver `spring-integration`).
- **`@Async`** y otros hilos pierden el `SecurityContext` salvo que se propague (`DelegatingSecurityContextExecutor` o la configuración equivalente).

## Tests

- `@WithMockUser(roles = "ADMIN")` o el post-procesador `jwt()` de `spring-security-test` en tests de controlador (ver `spring-testing-quality`).
- Casos mínimos: 401 sin token, 403 sin permisos, 404 ante un recurso ajeno, 200 con permisos.

## Checklist

- [ ] `SecurityFilterChain` con DSL de lambdas y `anyRequest().authenticated()` al final
- [ ] Endpoints públicos enumerados explícitamente
- [ ] Tokens validados (firma, emisor, audiencia, expiración); algoritmo fijado
- [ ] Roles/scopes mapeados a authorities de forma explícita
- [ ] `DelegatingPasswordEncoder` (o Argon2); contraseñas nunca en logs
- [ ] `@PreAuthorize` en operaciones restringidas, sin auto-invocación
- [ ] Identidad tomada del principal, nunca de la petición
- [ ] Autorización por recurso y por propiedad en todas las operaciones
- [ ] CSRF desactivado solo en APIs stateless con Bearer
