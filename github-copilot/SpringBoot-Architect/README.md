# Spring Boot Architect

Agente de desarrollo para GitHub Copilot con 17 skills. Sigue la misma estructura que el agente NestJS Architect y está adaptado a Spring Boot 3.x/4.x.

## Instalación

Copia en el repositorio:

```
.github/agents/Spring Boot Architect.agent.md
.github/skills/
```

Y crea o adapta `guidelines/coding-guidelines.md` con las convenciones del proyecto: estructura de paquetes, base de datos y migraciones, autenticación, uso de Lombok/MapStruct, formato, umbrales de cobertura y quality gate. Sus reglas prevalecen sobre las genéricas del agente.

## Equivalencia con el agente NestJS

| NestJS                        | Spring Boot              | Particularidades de Spring                                                    |
| ----------------------------- | ------------------------ | ----------------------------------------------------------------------------- |
| `nestjs-modules`              | `spring-structure`       | Paquetes por funcionalidad, visibilidad de paquete, Spring Modulith, `@Configuration` |
| `nestjs-controllers`          | `spring-controllers`     | `@RestController`, `ResponseEntity`, `Pageable`, springdoc                    |
| `nestjs-dto-validation`       | `spring-dto-validation`  | Records, Bean Validation, Jackson 2/3                                         |
| `nestjs-services`             | `spring-services`        | `@Transactional` y sus trampas de proxy, MapStruct                            |
| `nestjs-persistence`          | `spring-persistence`     | JPA/Hibernate, `open-in-view`, fetch LAZY, `equals`/`hashCode`, Flyway/Liquibase |
| `nestjs-auth`                 | `spring-auth`            | `SecurityFilterChain`, OAuth2 Resource Server, `@PreAuthorize`                |
| `nestjs-security`             | `spring-security`        | SpEL, deserialización Java/Jackson, XXE, Actuator, H2                         |
| `nestjs-request-pipeline`     | `spring-web-pipeline`    | Filtros de servlet, `HandlerInterceptor`, AOP                                 |
| `nestjs-error-handling`       | `spring-error-handling`  | `@RestControllerAdvice`, `ProblemDetail` (RFC 9457)                           |
| `nestjs-config`               | `spring-config`          | `@ConfigurationProperties` con records, perfiles, configtree                  |
| `nestjs-testing`              | `spring-testing`         | JUnit 5, slices, `@MockitoBean`, Testcontainers con `@ServiceConnection`      |
| `nestjs-quality`              | `spring-quality`         | Spotless/Checkstyle, SLF4J, logging estructurado                              |
| `nestjs-solid`                | `spring-solid`           | Inyección por constructor, `List`/`Map` de beans, `@Qualifier`                |
| `nestjs-graphql`              | `spring-graphql`         | Schema-first, `@BatchMapping`, `GraphQlTester`                                |
| `nestjs-microservices`        | `spring-messaging`       | Eventos de aplicación, Spring Kafka/AMQP, outbox de Spring Modulith           |
| *(dentro de microservices)*   | `spring-http-clients`    | `RestClient`, `@HttpExchange`, `@Retryable` de Spring Framework 7             |
| *(dentro de microservices)*   | `spring-observability`   | Actuator, probes, Micrometer, trazas, apagado ordenado                        |

`spring-http-clients` y `spring-observability` son skills propias porque en Spring tienen mucho peso específico. Las llamadas síncronas con `RestClient` son tan habituales como la mensajería. Actuator, por su parte, es a la vez una herramienta operativa y un riesgo de seguridad.

## Versiones

El agente detecta si el proyecto usa Spring Boot 3.x o 4.x y no mezcla sus APIs. Los cambios más relevantes de Boot 4 que contemplan las skills son:

- Spring Framework 7 y Spring Security 7.
- Jackson 3, con el paquete `tools.jackson`.
- Starters modularizados; `spring-boot-starter-aop` pasa a llamarse `spring-boot-starter-aspectj`.
- `@MockitoBean` en lugar de `@MockBean`, que se eliminó en Boot 4.
- Reintentos y límites de concurrencia en el núcleo del framework (`@Retryable`, `@ConcurrencyLimit`), sustituyendo a Spring Retry.
- Versionado de API nativo.

Los nombres de propiedades y de clases que cambian entre versiones se comprueban en la documentación oficial de la versión instalada, y la versión mínima de Java se toma de la matriz oficial.

## Validación

Ver `VALIDATION.md` y la carpeta `validation/` para el banco de pruebas y la autoevaluación.
