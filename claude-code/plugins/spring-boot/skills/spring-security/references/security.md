
# Seguridad del código

Esta skill cubre **que el código no sea vulnerable**. La configuración de autenticación, roles y autorización por recurso está en `spring-security`.

Principio base: **toda entrada externa es hostil** hasta validarla. Entrada externa es el cuerpo, parámetros y cabeceras HTTP, los argumentos GraphQL, los mensajes de colas, los ficheros subidos, el XML, las respuestas de APIs de terceros y la configuración.

## Validación como frontera (A03 / API3)

- Toda entrada pasa por DTOs validados con `@Valid` y límites de tamaño (ver `spring-api`).
- Límites globales del servidor para evitar peticiones enormes:

```yaml
spring:
  servlet:
    multipart:
      max-file-size: 5MB
      max-request-size: 10MB
server:
  max-http-request-header-size: 16KB
```

Comprueba en la referencia de la versión instalada el límite de tamaño de cuerpo del servidor embebido (Tomcat/Jetty) y configúralo si el valor por defecto no es adecuado.

### Asignación masiva (API3 / API6)

Enlazar la petición directamente a una entidad, o copiar el DTO entero sobre ella, permite modificar campos que el usuario no debe controlar (`role`, `enabled`, `ownerId`, `price`).

```java
// ❌ Entidad como modelo de entrada: el cliente puede enviar "role": "ADMIN"
@PutMapping("/{id}")
UserEntity update(@PathVariable UUID id, @RequestBody UserEntity user) { ... }

// ❌ Copia indiscriminada
BeanUtils.copyProperties(request, user);

// ✅ DTO con solo los campos editables y copia explícita en el servicio
public record UpdateProfileRequest(@Size(max = 100) String displayName, @Size(max = 500) String bio) { }

user.changeDisplayName(request.displayName());
user.changeBio(request.bio());
```

- Nunca uses entidades con `@RequestBody` ni con `@ModelAttribute`.
- Los campos sensibles (`role`, `ownerId`) se asignan en el servicio a partir del usuario autenticado.
- Mappers automáticos (MapStruct) en actualizaciones: mapea solo los campos permitidos, con `unmappedTargetPolicy = ERROR`.

## Inyección (A03)

### SQL y JPQL

```java
// ❌ Inyección
em.createQuery("select u from UserEntity u where u.email = '" + email + "'");
jdbcTemplate.queryForList("select * from users where name like '%" + term + "%'");

// ✅ Parametrizado
em.createQuery("select u from UserEntity u where u.email = :email", UserEntity.class)
  .setParameter("email", email);
jdbcClient.sql("select * from users where name like :term")
          .param("term", "%" + term + "%")
          .query(UserRow.class).list();
```

- Nunca concatenes texto del usuario en JPQL, HQL, SQL nativo ni criterios de `@Query(nativeQuery = true)`.
- En búsquedas `LIKE`, el parámetro evita la inyección, pero `%` y `_` del usuario siguen actuando como comodines: escápalos (con la cláusula `ESCAPE` del motor) si la búsqueda debe ser literal, y limita la longitud del término.
- **Ordenación**: el `Sort` de `Pageable` recibe nombres de propiedad del cliente. Valídalos contra una lista permitida antes de pasarlos a la consulta; en consultas nativas no se pueden parametrizar:

```java
private static final Set<String> SORTABLE = Set.of("createdAt", "email");

Pageable safe(Pageable pageable) {
    pageable.getSort().forEach(order -> {
        if (!SORTABLE.contains(order.getProperty())) {
            throw new InvalidSortException(order.getProperty());
        }
    });
    return pageable;
}
```

- Consultas dinámicas con `Specification`/Criteria, nunca con texto construido.
- NoSQL (MongoDB): no conviertas objetos JSON de entrada en filtros sin validar sus tipos.

### SpEL

- **Nunca** evalúes expresiones SpEL que contengan entrada del usuario (`SpelExpressionParser` con `StandardEvaluationContext` permite ejecutar código arbitrario).
- No construyas el texto de `@PreAuthorize`, `@Value` ni `@Cacheable(key)` a partir de datos externos. Si es imprescindible evaluar expresiones de usuario, usa `SimpleEvaluationContext` restringido.

### Comandos del sistema

```java
// ❌ La shell interpreta el string: filename = "a.pdf; rm -rf /"
Runtime.getRuntime().exec(new String[] { "sh", "-c", "convert " + filename + " out.png" });

// ✅ Sin shell, argumentos separados y valor validado previamente
new ProcessBuilder("convert", validatedPath.toString(), outputPath.toString()).start();
```

### LDAP y logs

- Filtros LDAP con los métodos de codificación de Spring LDAP (`LdapQueryBuilder`, `LdapEncoder`), nunca concatenando.
- No registres entrada del usuario sin neutralizar saltos de línea (inyección en logs); con logging estructurado (JSON) el riesgo se reduce (ver `spring-testing-quality`).

### Path traversal

```java
Path safeResolve(Path root, String fileName) {
    Path target = root.resolve(fileName).normalize();
    if (!target.startsWith(root)) {
        throw new InvalidFileNameException(fileName);
    }
    return target;
}
```

Mejor aún: genera el nombre en el servidor (`UUID.randomUUID()`) y guarda el nombre original solo como metadato.

## SSRF — peticiones a URLs externas (A10 / API7)

Si el servidor llama a una URL aportada por el usuario (webhooks, importar desde URL, vista previa de enlaces), un atacante puede apuntar a servicios internos (`localhost`, `169.254.169.254` de metadatos cloud, red interna).

- **Lista permitida** de dominios cuando sea posible.
- Si no: solo `https`, resolución DNS y rechazo de IPs privadas, loopback, link-local y metadatos; sin seguir redirecciones (o validándolas de nuevo).
- Timeout y límite de tamaño de respuesta en toda petición saliente (ver `spring-integration`).
- Nunca devuelvas al cliente el contenido o los errores en bruto de la petición interna.

## Deserialización insegura (A08)

- **Nunca** uses `ObjectInputStream` sobre datos externos (deserialización nativa de Java). Si un protocolo lo exige, usa filtros de deserialización (`ObjectInputFilter`) con lista permitida.
- **Jackson**: nunca actives el tipado polimórfico global (`activateDefaultTyping` / `enableDefaultTyping`) ni `@JsonTypeInfo(use = Id.CLASS)` con datos externos: permiten instanciar clases arbitrarias. Para polimorfismo, `Id.NAME` con subtipos declarados.
- **Mensajería**: con deserializadores JSON de Spring Kafka/AMQP, configura los paquetes de confianza explícitos (nunca `*`) (ver `spring-integration`).
- No uses `XMLDecoder`, `XStream` sin lista permitida ni librerías de serialización que ejecuten código.

## XML y XXE

Los parsers XML de Java resuelven entidades externas por defecto en muchas configuraciones, lo que permite leer ficheros del servidor o hacer SSRF:

```java
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
factory.setXIncludeAware(false);
factory.setExpandEntityReferences(false);
```

- Aplica la configuración equivalente a `SAXParserFactory`, `XMLInputFactory`, `TransformerFactory` y `Unmarshaller`.
- Si basta con JSON, no aceptes XML.

## Subida de ficheros

```java
@PostMapping(path = "/avatar", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
@ResponseStatus(HttpStatus.NO_CONTENT)
void uploadAvatar(@RequestParam("file") MultipartFile file, @AuthenticationPrincipal Jwt jwt) {
    avatarService.store(UUID.fromString(jwt.getSubject()), file);
}
```

En el servicio:

- Límites de tamaño globales (`spring.servlet.multipart.*`) y comprobación en el servicio.
- Tipo real por contenido (*magic bytes*, p. ej. con Apache Tika), no por extensión ni por el `Content-Type` del cliente.
- Nombre generado en el servidor; nunca rutas a partir de `getOriginalFilename()`.
- Almacenamiento fuera del directorio servido como estático (o almacenamiento de objetos); descarga con `Content-Disposition: attachment` y `X-Content-Type-Options: nosniff`.
- Para ficheros de usuarios no confiables, análisis antivirus si el riesgo lo justifica.
- Cuidado con ficheros comprimidos (*zip bombs*, rutas `../` dentro del zip).

## Límites y protección frente a abuso (API4)

- Spring Boot **no** incluye rate limiting. Aplícalo en el API gateway/ingress o con una librería (p. ej. Bucket4j) según las convenciones del proyecto, con límites más estrictos en login, registro, recuperación de contraseña y operaciones costosas.
- Con varias réplicas, el estado del límite debe ser compartido (Redis) o aplicarse en el gateway.
- Detrás de un proxy, configura `server.forward-headers-strategy` para obtener la IP y el esquema reales; confía solo en las cabeceras de proxies conocidos.
- Paginación con tamaño máximo (ver `spring-api`), timeouts en llamadas salientes y límites de profundidad/complejidad en GraphQL (ver `spring-graphql`).

## Configuración segura (A05)

### CORS

```java
@Bean
CorsConfigurationSource corsConfigurationSource(AppProperties props) {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(props.cors().allowedOrigins()); // lista explícita
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
    config.setAllowCredentials(true);
    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/api/**", config);
    return source;
}
// En la SecurityFilterChain: .cors(Customizer.withDefaults())
```

- Nunca `*` (ni `allowedOriginPatterns("*")`) junto con credenciales. CORS protege navegadores, no sustituye a la autenticación.
- Configura CORS en Spring Security (no solo en `WebMvcConfigurer`), para que las peticiones *preflight* no sean rechazadas antes.

### CSRF

- Spring Security activa CSRF por defecto. Desactivarlo **solo** es correcto en APIs stateless autenticadas exclusivamente por cabecera `Authorization`.
- Si la autenticación viaja en cookies (sesión o token en cookie), CSRF debe estar activo; para SPAs, `CookieCsrfTokenRepository` según la documentación de la versión instalada.

### Cabeceras

- Spring Security añade cabeceras seguras por defecto (`X-Content-Type-Options`, `X-Frame-Options`, `Cache-Control`, HSTS en HTTPS). No las desactives; añade una `Content-Security-Policy` si la aplicación sirve HTML.

### Superficie expuesta

- **Actuator**: exponer solo `health`, `info` y métricas necesarias; nunca `env`, `configprops`, `heapdump` (contiene secretos en memoria), `threaddump`, `loggers` o `shutdown` sin autenticación y sin red restringida (ver `spring-config-observability`).
- **Consola H2**, DevTools y `org.springframework.boot:spring-boot-docker-compose` solo en desarrollo.
- **Documentación** (springdoc) desactivada o protegida en producción.
- **Página de error**: `server.error.include-stacktrace=never`, `include-message` e `include-binding-errors` con `never` salvo decisión explícita (ver `spring-api`).
- `ddl-auto` distinto de `validate`/`none` y `show-sql` en producción, prohibidos.

## Secretos (A02 / A05)

- Sin secretos en el código, en `application.yml` versionado ni en tests; vienen de variables de entorno, ficheros montados (`configtree`) o un gestor de secretos (Vault, Key Vault...) (ver `spring-config-observability`).
- Ni en logs, ni en errores, ni en respuestas, ni en el endpoint `env` de Actuator.
- Si un secreto se ha commiteado, **rótalo**: borrarlo del historial no basta.
- Credenciales distintas por entorno y por servicio, con permisos mínimos.

## Criptografía (A02)

- Valores aleatorios de seguridad (tokens de reseteo, nonces) con `SecureRandom` o `UUID.randomUUID()`, **nunca** `java.util.Random` ni `Math.random()`.
- Comparación de secretos o firmas en tiempo constante con `MessageDigest.isEqual`:

```java
boolean isValidSignature(byte[] payload, String signatureHex, byte[] secret) throws GeneralSecurityException {
    Mac mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(secret, "HmacSHA256"));
    byte[] expected = mac.doFinal(payload);
    return MessageDigest.isEqual(expected, HexFormat.of().parseHex(signatureHex));
}
```

- No implementes algoritmos propios. Cifrado con AES-GCM y claves gestionadas fuera del código (o los utilitarios de `spring-security-crypto`).
- Contraseñas: ver `spring-security`.
- TLS en todas las comunicaciones, también hacia la base de datos, el broker y entre servicios.

## Fugas de información (A04 / A09)

- Errores sin stack traces, mensajes de base de datos ni rutas internas (ver `spring-api`).
- DTOs de respuesta con solo los campos necesarios (API3: exposición excesiva de datos).
- Logs sin contraseñas, tokens, cabeceras `Authorization`, cuerpos completos ni datos personales.
- Mensajes que no revelen la existencia de recursos o cuentas (404 ante recursos ajenos, mismo error en login).

## Dependencias (A06)

```bash
./mvnw versions:display-dependency-updates     # dependencias desactualizadas
./mvnw org.owasp:dependency-check-maven:check  # vulnerabilidades conocidas (o la herramienta del proyecto)
```

- Versiones gestionadas por el BOM de Spring Boot; no fijes versiones de dependencias gestionadas salvo para aplicar un parche de seguridad (y documéntalo).
- Escaneo de vulnerabilidades en CI (OWASP Dependency-Check, Dependabot, Snyk, Trivy... según convenciones del proyecto).
- Sin vulnerabilidades críticas o altas sin parche en producción; actualiza Spring Boot dentro de su línea de mantenimiento.
- Antes de añadir una dependencia: mantenimiento, licencia, vulnerabilidades conocidas y necesidad real.

## Logging y monitorización de seguridad (A09)

- Registra eventos relevantes: logins fallidos, accesos denegados (401/403), cambios de permisos, límites de rate alcanzados. Spring Security publica eventos de autenticación (`AuthenticationFailure...`) que se pueden escuchar.
- Con correlación (traceId) y sin datos sensibles.

## Checklist de revisión de seguridad

- [ ] Entrada validada con DTOs; sin entidades en `@RequestBody`/`@ModelAttribute`
- [ ] Sin copia indiscriminada sobre entidades (asignación masiva)
- [ ] Autenticación y autorización por recurso revisadas (ver `spring-security`)
- [ ] JPQL/SQL parametrizados; ordenación en lista permitida
- [ ] Sin SpEL con entrada del usuario; sin shell ni rutas construidas con ella
- [ ] URLs externas controladas frente a SSRF, con timeout
- [ ] Sin `ObjectInputStream` ni tipado polimórfico global de Jackson; paquetes de confianza en mensajería
- [ ] Parsers XML con DTD/entidades externas desactivadas
- [ ] Subidas con límite, tipo real validado y nombre generado
- [ ] Rate limiting en endpoints sensibles; paginación y límites de tamaño
- [ ] CORS con lista de orígenes; CSRF desactivado solo en APIs stateless con Bearer
- [ ] Actuator, H2, DevTools y documentación no expuestos en producción
- [ ] Sin secretos en código, configuración versionada, logs ni respuestas
- [ ] `SecureRandom`/`UUID.randomUUID()` y `MessageDigest.isEqual` donde corresponda
- [ ] Errores sin información interna
- [ ] Escaneo de dependencias sin vulnerabilidades críticas o altas
