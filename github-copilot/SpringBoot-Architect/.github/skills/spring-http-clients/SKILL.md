---
name: spring-http-clients
description: 'Clientes HTTP en Spring Boot: RestClient, WebClient, interfaces declarativas @HttpExchange, timeouts, manejo de errores de servicios remotos, reintentos (@Retryable de Spring Framework 7 o Resilience4j), circuit breaker, límites de concurrencia, propagación de trazas y protección frente a SSRF. Usar cuando: llamar a una API externa u otro microservicio, configurar timeouts o reintentos, encapsular un servicio remoto.'
argument-hint: 'Describe el servicio remoto que necesitas consumir.'
---

# Clientes HTTP y resiliencia

## Qué cliente usar

| Cliente                          | Uso                                                              |
| -------------------------------- | ---------------------------------------------------------------- |
| `RestClient`                     | Llamadas síncronas en aplicaciones Spring MVC (por defecto)      |
| Interfaces `@HttpExchange`       | Cliente declarativo sobre `RestClient`/`WebClient`              |
| `WebClient`                      | Aplicaciones WebFlux o llamadas reactivas                        |
| `RestTemplate`                   | Solo en código existente; no lo uses en código nuevo             |

- Crea los clientes a partir del **`RestClient.Builder` auto-configurado** (inyectado), no con `RestClient.create()`: el builder de Boot incluye los convertidores de mensajes y la instrumentación de observabilidad (métricas y propagación de trazas).
- Encapsula cada servicio remoto en un *gateway* propio: el resto del código no conoce URLs, cabeceras ni el cliente HTTP.

## Interfaz declarativa

```java
@HttpExchange("/api/v1/customers")
interface CustomerApi {

    @GetExchange("/{id}")
    CustomerDto findById(@PathVariable UUID id);

    @PostExchange
    CustomerDto create(@RequestBody CreateCustomerDto request);
}
```

```java
@Configuration(proxyBeanMethods = false)
class CustomerClientConfig {

    @Bean
    CustomerApi customerApi(RestClient.Builder builder, CustomerClientProperties props) {
        RestClient restClient = builder
                .baseUrl(props.baseUrl().toString())
                .requestFactory(requestFactory(props))
                .defaultStatusHandler(HttpStatusCode::isError, (request, response) -> {
                    throw new RemoteServiceException("customers", response.getStatusCode());
                })
                .build();
        return HttpServiceProxyFactory.builderFor(RestClientAdapter.create(restClient))
                .build()
                .createClient(CustomerApi.class);
    }

    private ClientHttpRequestFactory requestFactory(CustomerClientProperties props) {
        // HttpClient del JDK: reutiliza conexiones (a diferencia de SimpleClientHttpRequestFactory)
        HttpClient httpClient = HttpClient.newBuilder()
                .connectTimeout(props.connectTimeout())
                .build();
        JdkClientHttpRequestFactory factory = new JdkClientHttpRequestFactory(httpClient);
        factory.setReadTimeout(props.readTimeout());
        return factory;
    }
}
```

- Las versiones recientes de Spring Boot permiten configurar timeouts y la implementación del cliente HTTP con propiedades y registrar grupos de interfaces `@HttpExchange` de forma declarativa. Usa esos mecanismos si la versión instalada los ofrece; comprueba los nombres de las propiedades en la referencia de esa versión.
- Elige una implementación que reutilice conexiones (JDK `HttpClient`, Apache HttpClient, Reactor Netty). Desde Spring Boot 3.4 la fábrica auto-configurada se elige según el classpath (Apache, Jetty, Reactor Netty, JDK y, en último lugar, `SimpleClientHttpRequestFactory`) y se puede fijar con `spring.http.client.factory`; si no necesitas una fábrica propia por cliente, configura esa en lugar de crearla a mano.

## Timeouts — obligatorios

- **Timeout de conexión y de lectura** en toda llamada saliente. Sin timeout, un servicio lento agota los hilos o conexiones de la aplicación y provoca un fallo en cascada.
- Valores en `@ConfigurationProperties` por servicio remoto (ver `spring-config`).
- El tiempo total (incluidos los reintentos) debe ser menor que el timeout de quien te llama.

## Errores del servicio remoto

- Traduce las respuestas de error a excepciones propias del *gateway* (`RemoteServiceException`, `CustomerNotFoundException`), con el estado y el servicio, **sin** propagar al cliente final el cuerpo de error del servicio remoto.
- Decide explícitamente qué hacer ante cada fallo: error al cliente, valor degradado, reintento o datos en caché.
- Un 404 del remoto puede ser un resultado esperado (`Optional.empty()`) o un error, según el contrato.

## Reintentos

- Solo para operaciones **idempotentes** (GET, PUT/DELETE idempotentes, o POST con clave de idempotencia acordada) y errores **transitorios** (timeouts, conexión rechazada, 502/503/504). Nunca ante 4xx.
- Espera exponencial con *jitter* y número máximo de intentos.
- **Spring Framework 7** incluye reintentos en el núcleo: `@Retryable` (con `@EnableResilientMethods`) y `RetryTemplate`. Spring Retry deja de estar gestionado por Spring Boot 4; no lo añadas en proyectos nuevos sobre Boot 4.

```java
@Retryable(includes = {ResourceAccessException.class, ServiceUnavailableException.class},
           maxRetries = 3, delay = 200, multiplier = 2, jitter = 50, maxDelay = 2000)
public CustomerDto findCustomer(UUID id) {
    return customerApi.findById(id);
}
```

- En Boot 3 se usan Spring Retry o Resilience4j. Usa lo que tenga el proyecto.
- `@Retryable` funciona por proxy: sin auto-invocación (ver `spring-services`).
- No combines varios niveles de reintento (cliente HTTP + anotación + gateway): multiplican las peticiones.

## Circuit breaker y límites de concurrencia

- **Circuit breaker** (Resilience4j, o Spring Cloud Circuit Breaker) para dependencias que pueden caer durante un tiempo: deja de llamar mientras el remoto está caído y responde con un *fallback* o un error rápido.
- **Límite de concurrencia** hacia recursos escasos: `@ConcurrencyLimit` en Spring Framework 7, o *bulkhead* de Resilience4j. Especialmente con *virtual threads*, donde no hay un pool de hilos que limite de forma natural.
- Configura estos mecanismos con valores medidos, no copiados, y expón sus métricas (ver `spring-observability`).

## Seguridad

- URLs base desde configuración, nunca desde la petición del usuario. Si la URL depende del usuario (webhooks, importar desde URL), aplica las protecciones SSRF de `spring-security`.
- Credenciales del servicio remoto (API keys, client credentials OAuth2) desde gestor de secretos; con OAuth2 entre servicios, usa el soporte de cliente OAuth2 de Spring Security (`OAuth2ClientHttpRequestInterceptor` o equivalente de la versión) en lugar de gestionar tokens a mano.
- TLS siempre; nunca desactives la verificación de certificados.
- No registres cabeceras de autorización ni cuerpos con datos sensibles.

## Observabilidad

- Con el builder auto-configurado, cada llamada genera métricas (`http.client.requests`) y propaga el contexto de traza al servicio remoto (ver `spring-observability`).
- Usa plantillas de URI (`/customers/{id}`) en lugar de concatenar valores, para que la métrica no tenga una etiqueta por cada id (cardinalidad).

## Tests

- Unitarios del *gateway* con `MockRestServiceServer` (para `RestClient`/`RestTemplate`) o un servidor simulado (WireMock, MockWebServer).
- Prueba los timeouts, los errores 4xx/5xx y el comportamiento de reintento y *fallback*.

## Checklist

- [ ] `RestClient` (o `@HttpExchange`) creado desde el builder auto-configurado
- [ ] Gateway por servicio remoto
- [ ] Timeouts de conexión y lectura configurados
- [ ] Errores remotos traducidos, sin propagar cuerpos internos
- [ ] Reintentos solo idempotentes y transitorios, con backoff y jitter
- [ ] Circuit breaker / límite de concurrencia donde aplique
- [ ] URLs desde configuración; protección SSRF si dependen del usuario
- [ ] Credenciales desde gestor de secretos; TLS verificado
- [ ] Plantillas de URI para métricas de baja cardinalidad
