
# Calidad de código y logging

Lee siempre la configuración real del proyecto (plugins de Maven/Gradle, `checkstyle.xml`, `sonar-project.properties`) antes de aplicar estas reglas: si difieren, prevalece la del proyecto. La estrategia de tests está en `spring-testing-quality`.

## Formato y análisis estático

- **Formato**: el definido por el proyecto (Spotless con google-java-format/palantir, o el del IDE compartido). No reformatees ficheros que no tocas.
- **Checkstyle / SpotBugs / Error Prone / PMD**: los que use el proyecto, sin avisos nuevos.
- **SonarQube**: sin code smells, bugs, vulnerabilidades ni *security hotspots* nuevos sin revisar; sin duplicaciones.
- Complejidad cognitiva baja; el umbral lo fija el quality gate (por defecto en Sonar, **15 por método**). Reduce con retornos tempranos y métodos extraídos con nombres descriptivos.
- Corrige la causa. No uses `@SuppressWarnings` ni `// NOSONAR` salvo excepción justificada y comentada.

## Buenas prácticas Java

- **Optional**: solo como retorno de búsquedas. Nunca `optional.get()` sin comprobar; usa `orElseThrow`, `map`, `ifPresent`. Nunca `Optional` como campo o parámetro.
- **Colecciones**: devuelve colecciones vacías, no `null`. Usa colecciones inmutables (`List.of`, `stream().toList()`) cuando no se deban modificar.
- **Excepciones**: no captures `Exception`/`Throwable` salvo en el manejador global; no uses excepciones para control de flujo normal (ver `spring-api`).
- **Recursos**: `try-with-resources` para todo `AutoCloseable` (streams, conexiones, ficheros).
- **Streams**: legibles; si un pipeline necesita comentarios, extrae métodos. Evita efectos secundarios dentro de `map`/`filter`.
- **Igualdad**: `equals` en lugar de `==` para objetos (incluidos `String`, `Integer`, `UUID`).
- **Fechas**: `java.time` (`Instant`, `LocalDate`, `Duration`); nunca `Date`/`Calendar`. Inyecta un `Clock` para que el tiempo sea testeable.
- **Strings**: text blocks para SQL/JSON largos; `formatted()` en lugar de concatenaciones complejas (nunca para construir SQL, ver `spring-security`).
- **Inmutabilidad**: campos `final`, records para datos, sin setters innecesarios.
- **Sin código muerto**: métodos privados no usados, beans que nadie inyecta, ramas inalcanzables, código comentado.

## Logging

- **SLF4J** (`org.slf4j.Logger`) con un logger por clase:

```java
private static final Logger log = LoggerFactory.getLogger(OrderService.class);
```

  (o `@Slf4j` si el proyecto usa Lombok).
- **Nunca** `System.out`, `System.err` ni `e.printStackTrace()`.
- **Mensajes parametrizados**, no concatenación (se evita construir el texto si el nivel está desactivado y se facilita el análisis):

```java
log.info("Order {} cancelled by user {}", orderId, userId);   // ✅
log.info("Order " + orderId + " cancelled");                  // ❌
```

- Al registrar una excepción, pásala como **último argumento** para incluir el stack: `log.error("Payment failed for order {}", orderId, ex);`.
- **Niveles**: `error` (requiere atención), `warn` (anómalo pero recuperable), `info` (eventos de negocio relevantes), `debug` (diagnóstico). No registres en `info` dentro de bucles ni por cada fila.
- **Nunca** registres contraseñas, tokens, cabeceras `Authorization`, cuerpos completos de petición o de mensaje ni datos personales.
- Niveles por paquete en configuración (`logging.level.com.example=info`), no en código.

### Logging estructurado y correlación

- En producción, logs en **JSON**. Las versiones recientes de Spring Boot lo soportan de forma nativa (`logging.structured.format.console`, con formatos como ECS o Logstash); comprueba la propiedad en la versión instalada.
- Correlación con el `traceId` de Micrometer Tracing (ver `spring-config-observability`) o un correlation ID propio en el `MDC` (ver `spring-api`), incluido en todas las líneas.
- En código asíncrono (`@Async`, ejecutores propios), el `MDC` no se propaga solo: usa un `TaskDecorator` o la propagación de contexto de Micrometer.

## Checklist pre-PR

```bash
./mvnw spotless:check verify     # o ./gradlew spotlessCheck build
```

- [ ] Compila sin avisos nuevos
- [ ] Formato aplicado según el proyecto
- [ ] Tests en verde (cobertura según convenciones del proyecto)
- [ ] Sin avisos nuevos de análisis estático ni de SonarQube
- [ ] Sin `System.out`, `printStackTrace`, código muerto ni código comentado
- [ ] Logs parametrizados, con la excepción como último argumento y sin datos sensibles
- [ ] Complejidad dentro del quality gate
