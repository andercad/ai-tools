
# Configuración

## Reglas

- Configuración en `application.yml` (o `.properties`, según el proyecto), con valores por defecto seguros para desarrollo.
- Propiedades propias agrupadas en clases `@ConfigurationProperties` **validadas**; evita `@Value` disperso.
- **Sin secretos** en ficheros versionados: llegan por variables de entorno, ficheros montados o un gestor de secretos.
- La aplicación **no arranca** si falta una propiedad obligatoria o tiene un valor inválido (*fail fast*).
- Diferencias entre entornos mediante perfiles o variables de entorno, no con código condicional por entorno.

## @ConfigurationProperties con records

```java
@ConfigurationProperties(prefix = "app.payments")
@Validated
public record PaymentsProperties(
        @NotNull URI baseUrl,
        @NotNull @DurationMin(millis = 100) Duration timeout,
        @Min(0) @Max(10) int maxRetries,
        @NotBlank String apiKey
) { }
```

```java
@SpringBootApplication
@ConfigurationPropertiesScan
public class Application { ... }
```

```yaml
app:
  payments:
    base-url: https://payments.example.com
    timeout: 3s
    max-retries: 2
    api-key: ${PAYMENTS_API_KEY}   # el valor real viene del entorno
```

- Records inmutables; tipos ricos (`Duration`, `DataSize`, `URI`, enums) en lugar de números y strings: Spring los convierte (`3s`, `10MB`).
- `@Validated` + Bean Validation: el arranque falla con un mensaje claro si la configuración es inválida. Desde Spring Boot 3.4 la validación solo llega a las propiedades anidadas (records o clases dentro del record) si el campo lleva `@Valid`.
- Inyecta el record en los beans que lo necesitan (por constructor). No inyectes `Environment` para leer propiedades sueltas.
- Añade `org.springframework.boot:spring-boot-configuration-processor` (si las convenciones del proyecto lo usan) para generar metadatos: autocompletado en el IDE y documentación de las propiedades.
- Valores sensibles con nombres reconocibles (`password`, `secret`, `key`, `token`, `credentials`): Actuator los enmascara, pero no expongas `env`/`configprops` igualmente (ver `spring-config-observability`).

## @Value

Aceptable para un valor aislado en una clase de configuración. No lo uses para grupos de propiedades, ni con valores por defecto que oculten configuraciones faltantes en producción (`@Value("${app.url:http://localhost}")`).

## Perfiles

```
application.yml            ← común y valores por defecto de desarrollo
application-test.yml       ← tests
application-prod.yml       ← endurecimiento de producción (sin secretos)
```

- Activa perfiles con `SPRING_PROFILES_ACTIVE` en el entorno, nunca fijándolo en `application.yml` versionado.
- No uses perfiles para activar o desactivar lógica de negocio; para eso, propiedades explícitas (`app.feature.x.enabled`) o un sistema de *feature flags*.
- `@Profile` en beans solo para infraestructura (p. ej. un adaptador simulado en `local`).
- Los grupos de perfiles (`spring.profiles.group`) ayudan a componer configuraciones; evita jerarquías complejas.

## Secretos

Por orden de preferencia, según la plataforma:

1. Gestor de secretos (Vault, Azure Key Vault, AWS Secrets Manager) mediante la integración correspondiente (`spring.config.import`).
2. Ficheros montados (Kubernetes Secrets) con `spring.config.import=optional:configtree:/run/secrets/`.
3. Variables de entorno (`SPRING_DATASOURCE_PASSWORD`, o referencias `${...}` en el YAML).

- Nunca en `application*.yml` versionado, en `README`, en tests ni en Dockerfiles.
- Para desarrollo local, un fichero no versionado (`.env`, `application-local.yml` en `.gitignore`) o los valores de Docker Compose/Testcontainers.
- Si un secreto se ha commiteado, **rótalo**.

## Precedencia de propiedades

De mayor a menor prioridad (resumen): argumentos de línea de comandos → variables de entorno → ficheros de configuración externos → `application-{perfil}.yml` empaquetado → `application.yml` empaquetado → valores por defecto. Una variable de entorno sobrescribe el YAML: úsalo para configurar cada despliegue sin reconstruir la imagen. Comprueba el orden exacto en la referencia de la versión instalada.

## Propiedades de Spring Boot

- Los nombres de las propiedades de Spring Boot cambian entre versiones: compruébalos en la referencia de propiedades de la versión instalada.
- Al migrar de versión, el módulo `org.springframework.boot:spring-boot-properties-migrator` avisa (temporalmente, en tiempo de ejecución) de propiedades renombradas o eliminadas.

## Añadir una nueva propiedad

1. Añadirla al record `@ConfigurationProperties` correspondiente con su validación.
2. Añadir el valor por defecto de desarrollo en `application.yml`, o una referencia `${VAR}` si es un secreto.
3. Si cambia en producción, añadirla a `application-prod.yml` (sin secretos) o documentar la variable de entorno.
4. Inyectarla por constructor donde se use.
5. Documentar el cambio para configurarlo en cada entorno desplegado.

## Checklist

- [ ] Propiedades propias en records `@ConfigurationProperties` con `@Validated`
- [ ] Tipos ricos (`Duration`, `DataSize`, `URI`)
- [ ] Sin `@Value` disperso ni valores por defecto que oculten configuraciones faltantes
- [ ] Perfil activo definido por el entorno, no en el YAML
- [ ] Sin secretos en ficheros versionados; secretos del gestor, configtree o entorno
- [ ] Nombres de propiedades de Spring comprobados en la versión instalada
