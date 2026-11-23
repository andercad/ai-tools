# Prompts de prueba (manuales, en un proyecto Spring Boot de ejemplo)

Instala el plugin y lanza cada prompt en sesión limpia. Marca el resultado.

| # | Prompt | Debe cargar / hacer | Resultado |
|---|---|---|---|
| 1 | Crea un CRUD de `products` con Spring Data JPA | `spring-structure-services`, `spring-api`, `spring-persistence`; DTOs validados (`@Valid`), DTO de respuesta, migración Flyway/Liquibase, sin exponer entidades; ejecuta `verify` | |
| 2 | Guardamos el secreto JWT en el `application.yml` del repo, ¿vale? | `spring-security`/`spring-config-observability`; lo desaconseja; `@ConfigurationProperties` y secretos fuera del repo | |
| 3 | Añade `GET /orders/{id}` | autorización por recurso (el usuario solo ve lo suyo); no confía en el UUID | |
| 4 | Endpoint de actualización de perfil que hace `repository.save(entityDesdeBody)` | detecta asignación masiva y copia campo a campo desde el DTO | |
| 5 | Subida de avatar de usuario | `spring-security`; límite de tamaño, tipo real, nombre generado, sin path traversal | |
| 6 | Resuelve el N+1 de `orders` con sus `items` | `spring-persistence`; `join fetch`/`EntityGraph`/batch, comprueba con test o log de SQL | |
| 7 | Listener de Kafka para `order.created` que envía un email | `spring-integration`; idempotente, commit tras procesar, reintentos/DLT, timeout | |
| 8 | ¿Microservicios o monolito modular para 3 equipos? | agente `spring-boot-architect`; modo Estándar, alternativa simple, drivers | |
| 9 | Evalúa la arquitectura de este repo | `spring-architecture-assessment`; lee ficheros, cita rutas, no escribe | |
| 10 | Planifica el upgrade a Spring Boot 4 | `spring-modernization-governance`; comprueba versión actual, avisos Jackson 3 / `@MockitoBean`, plantilla de ADR | |
| 11 | Redacta un ADR para adoptar Spring Modulith | `spring-boot-architect` usa `spring-modernization-governance` y `templates/adr-template.md` | |
| 12 | Arregla el test roto de `XService` | `spring-testing-quality`; ejecuta el test antes de informar | |
| 13 | `/spring-boot:spring-review` con cambios pendientes | `spring-boot-architect` solo lectura; hallazgos con `fichero:línea` | |
| 14 | Configura las convenciones de este proyecto | `spring-project-guidelines`; escribe `## Convenciones Spring Boot` en `CLAUDE.md`, enseña diff | |
| 15 | Con `tests: required`: crea `OrderService` | crea `OrderServiceTest.java` en `src/test/java` (mismo paquete); el hook Stop no bloquea; ejecuta `verify` | |
| 16 | Con `tests: required`, pedir un `@Service` y cortar antes del test (simulado) | el hook Stop bloquea (exit 2) con la lista de ficheros sin `XTest.java`/`XTests.java`/`XIT.java`; `*Application.java`, `@Configuration`, `@Entity`, records y `*Request/*Response/*Dto` no cuentan; con el test creado, pasa | |
| 17 | Con `it: required`: añade `POST /orders` | crea `OrderControllerIT.java` (Testcontainers o `@SpringBootTest`) en el mismo paso | |
| 18 | Edita un `.java` en un proyecto sin Spotless en `pom.xml`/`build.gradle` | el hook `format-lint` no hace nada (exit 0); con `spotless-maven-plugin` o `com.diffplug.spotless` formatea solo ese fichero y, si falla, devuelve el error (exit 2) | |

Criterios transversales: informa qué verificó y qué no; no mezcla APIs de Boot 3.x y 4.x; no usa APIs experimentales sin avisar; `spring-boot-architect` nunca edita ficheros.
