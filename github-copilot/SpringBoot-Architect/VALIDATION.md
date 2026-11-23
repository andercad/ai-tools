# Validación del agente Spring Boot Architect — v1 → v2

## Cómo se ha probado

| Nivel | Qué comprueba | Herramienta |
|---|---|---|
| 1. Estructura | Frontmatter, `name` = carpeta, descripción ≤ 1024 con "Usar cuando", routing agente ↔ 17 skills, referencias cruzadas | `run_tests.py` |
| 2. Coherencia | Los ejemplos cumplen las restricciones críticas del agente: sin `@Autowired` en campos (fuera de tests), sin `System.out`/`printStackTrace`, sin `javax.*`, sin APIs eliminadas de Spring Security, sin `@MockBean`, sin `RestTemplate` nuevo, sin entidades como `@RequestBody`, DTOs como records, sin `Optional` como parámetro, sin `@Transactional` en controladores, controladores sin `Page<T>`, sin `@Data` en entidades, YAML sin `ddl-auto: update`, `open-in-view: true` ni Actuator con `*` | `run_tests.py` |
| 3. Sintaxis | 67 bloques Java analizados con el parser de `javac` (JDK 17) y 11 bloques YAML con PyYAML | `ParseJava.java`, `run_tests.py` |
| 4. Hechos | Afirmaciones contrastadas con la documentación oficial que el agente no debe contradecir | `run_tests.py` |
| 5. Escenarios | 22 peticiones realistas → skill esperada en el top 3 | `scenarios.py` |
| 6. Revisión cruzada | Métodos, tipos y firmas usados en una skill frente a su definición en otra | manual |
| 7. Mutaciones | 8 defectos introducidos a propósito para comprobar que los tests los detectan | manual |

Repetir: `javac -encoding UTF-8 validation/ParseJava.java` (una vez), y después `python3 validation/run_tests.py spring .` y `python3 validation/scenarios.py spring .`.

## Resultados

| Nivel | v1 (entregada) | v2 |
|---|---|---|
| 1. Estructura | 88/88 | 88/88 |
| 2. Coherencia | 1 fallo | OK |
| 3. Sintaxis | OK | OK |
| 4. Hechos | 2 imprecisiones | OK |
| 5. Escenarios | 20/22 | 22/22 |
| 6. Revisión cruzada | 3 incoherencias | OK |
| 7. Mutaciones detectadas | — | 8/8 |

## Hallazgo principal: el paquete entregado mezclaba dos versiones

Al generar el agente escribí dos versiones de 12 ficheros en paralelo. Según las marcas de tiempo de escritura, el ZIP entregado contenía la versión A de 4 skills (`controllers`, `persistence`, `error-handling`, `http-clients`) y la versión B de las otras 8. Cada versión era coherente por separado, pero la mezcla no. La revisión cruzada encontró:

| # | Incoherencia | Corrección |
|---|---|---|
| 1 | `spring-services` y `spring-security` llaman a `user.changeDisplayName()` y `user.changeBio()`, pero la entidad de `spring-persistence` no tenía esos métodos (ni el campo `bio`) | Entidad con campo `bio`, métodos de negocio y getters |
| 2 | `spring-controllers` devolvía `Page<UserResponse>` mientras su propio texto decía que no se devuelva `Page`; `spring-graphql` esperaba un `PagedResponse` | Controlador con `PagedResponse<T>` y definición del record |
| 3 | `spring-http-clients` construía una `SimpleClientHttpRequestFactory` (sin reutilización de conexiones) justo antes de recomendar una con pool | `JdkClientHttpRequestFactory` y explicación de la selección automática de fábrica desde Boot 3.4 |

## Otros defectos corregidos

| # | Defecto | Gravedad | Corrección |
|---|---|---|---|
| 4 | El apagado ordenado se describía como "por defecto en versiones recientes; compruébalo": es el valor por defecto desde Boot 3.4 | Baja | Afirmación precisa |
| 5 | No se mencionaba que, desde Boot 3.4, la validación de `@ConfigurationProperties` solo llega a objetos anidados con `@Valid` | Media: configuración anidada sin validar en silencio | Nota en `spring-config` |
| 6 | Búsquedas `LIKE` parametrizadas sin advertir que `%` y `_` siguen actuando como comodines | Baja | Nota en `spring-security` |
| 7 | Dos escenarios no encontraban su skill: "validar el body y rechazar campos extra" y "mensajes duplicados" | Baja | Descripciones ampliadas |

## Afirmaciones verificadas como correctas

- `@MockBean` deprecado en 3.4 y eliminado en 4.0; sustituto `@MockitoBean`.
- Jackson 3 con paquete `tools.jackson` en Boot 4.
- Dependency management de Spring Retry eliminado en Boot 4.
- `@Retryable` y `@ConcurrencyLimit` en el núcleo de Spring Framework 7, con atributos `includes`, `maxRetries`, `delay`, `jitter`, `multiplier` y `maxDelay`.
- `spring-boot-starter-aop` renombrado a `spring-boot-starter-aspectj`.
- Apagado ordenado por defecto desde 3.4.
- Orden de selección de la fábrica de `RestClient` y propiedad `spring.http.client.factory` desde 3.4.

Sin verificar con fuente en esta revisión, aunque no contradichas: el valor por defecto de fechas en Jackson 3, el nombre exacto de propiedades como `spring.security.oauth2.resourceserver.jwt.audiences` y `spring.graphql.schema.introspection.enabled`, y el comportamiento al relanzar `AccessDeniedException` desde un `@ExceptionHandler`. Las skills ya indican que se comprueben en la versión instalada.

## Limitaciones

- **No se ha compilado contra Spring**: el parser de `javac` verifica la sintaxis, pero no los tipos, las anotaciones ni el comportamiento. La siguiente validación debería generar proyectos con Spring Initializr (Boot 3.5 y 4.x), copiar los ejemplos y ejecutar `./mvnw verify`.
- **La selección de skills es una simulación** por palabras, no una prueba en GitHub Copilot.
- La revisión cruzada entre skills se hizo a mano; no hay un test automático que compruebe que los métodos usados en una skill existen en otra.

## Autoevaluación

| Dimensión | Nota | Comentario |
|---|---|---|
| Estructura y routing | 10/10 | Sin fallos |
| Coherencia interna | 5/10 → 9/10 | La mezcla de versiones por escribir ficheros en paralelo produjo tres incoherencias entre skills. Es el fallo más importante, y es mío: no verifiqué el resultado tras la escritura concurrente |
| Exactitud técnica | 8/10 | Los hechos de Boot 4 eran correctos; dos afirmaciones de 3.4 eran imprecisas |
| Cobertura | 9/10 | Sin huecos en los 22 escenarios |
| Calidad del banco de pruebas | 8/10 | Validado con mutaciones, incluida sintaxis Java y YAML; la coherencia entre skills sigue siendo manual |
