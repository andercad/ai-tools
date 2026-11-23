---
name: spring-observability
description: 'Observabilidad y operación en Spring Boot: Actuator (exposición y seguridad de endpoints), health checks y probes de Kubernetes (liveness/readiness), health indicators propios, métricas con Micrometer, trazas distribuidas (Micrometer Tracing/OpenTelemetry), @Observed, apagado ordenado y configuración para contenedores. Usar cuando: exponer health checks, añadir métricas o trazas, configurar Actuator, preparar el servicio para Kubernetes.'
argument-hint: 'Describe qué necesitas observar o qué requisito operativo tienes (health, métricas, trazas, Kubernetes).'
---

# Observabilidad y operación

## Actuator: exposición mínima

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, info, prometheus     # solo lo necesario
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true
  server:
    port: 8081                                # puerto de gestión separado, no expuesto públicamente
```

- **Nunca** expongas públicamente `env`, `configprops`, `beans`, `mappings`, `heapdump`, `threaddump`, `loggers`, `shutdown`:
  - `heapdump` contiene todo lo que hay en memoria, incluidos secretos y datos personales.
  - `env`/`configprops` revelan configuración (enmascarada solo parcialmente).
  - `loggers` permite cambiar niveles de log; `shutdown`, parar la aplicación.
- Si se necesitan para diagnóstico, exponlos solo en el puerto de gestión, en red interna y con autenticación, mediante una `SecurityFilterChain` propia para Actuator (ver `spring-auth`).
- `show-details: when-authorized` (o `never`): los detalles de health revelan versiones y conexiones.

## Health checks

- **Liveness**: ¿el proceso está vivo? Si falla, Kubernetes reinicia el pod. **No** incluyas dependencias externas (base de datos, broker): una caída de la base de datos reiniciaría todos los pods sin arreglar nada.
- **Readiness**: ¿puede atender tráfico? Si falla, deja de recibir peticiones. Puede incluir dependencias imprescindibles.
- Spring Boot expone `/actuator/health/liveness` y `/actuator/health/readiness` (activos automáticamente en Kubernetes o con `probes.enabled`). Configura qué indicadores entran en cada grupo:

```yaml
management:
  endpoint:
    health:
      group:
        readiness:
          include: readinessState, db
```

- Indicador propio para una dependencia crítica:

```java
@Component
class PaymentsHealthIndicator implements HealthIndicator {

    private final PaymentsClient paymentsClient;

    PaymentsHealthIndicator(PaymentsClient paymentsClient) {
        this.paymentsClient = paymentsClient;
    }

    @Override
    public Health health() {
        try {
            paymentsClient.ping();               // con timeout corto
            return Health.up().build();
        } catch (RuntimeException ex) {
            return Health.down().withDetail("reason", "unreachable").build(); // sin detalles internos
        }
    }
}
```

- Los health checks deben ser **rápidos y con timeout**: un indicador lento hace fallar las probes.

## Métricas (Micrometer)

- Spring Boot instrumenta automáticamente HTTP, JVM, pool de conexiones, clientes HTTP creados desde el builder autoconfigurado (ver `spring-http-clients`), Kafka/RabbitMQ y más.
- Métricas de negocio con `MeterRegistry`:

```java
@Service
public class OrderService {

    private final Counter ordersPlaced;

    public OrderService(MeterRegistry registry, ...) {
        this.ordersPlaced = Counter.builder("orders.placed")
                .description("Orders placed")
                .register(registry);
    }
}
```

- **Etiquetas de baja cardinalidad**: nunca ids de usuario, ids de pedido, emails ni URLs con parámetros como etiquetas (explotan el número de series temporales).
- Nombres en minúsculas separados por puntos; Micrometer los adapta al sistema de monitorización.
- `@Observed` (con el soporte de observación activado) para métricas y trazas a la vez sobre un método.

## Trazas distribuidas

- Micrometer Tracing con el puente de OpenTelemetry (o Brave) y un exportador (OTLP, Zipkin), según las guidelines. En versiones recientes existe un starter unificado de OpenTelemetry; usa el de la versión instalada.
- El contexto de traza se propaga automáticamente en peticiones HTTP entrantes, clientes HTTP del builder autoconfigurado y mensajería (con la observación activada en los templates y listeners).
- El `traceId`/`spanId` se añade al `MDC`: inclúyelo en los logs estructurados (ver `spring-quality`).
- **Muestreo** (`management.tracing.sampling.probability`): 100 % en desarrollo, un porcentaje en producción según volumen.
- No pongas datos personales ni secretos como atributos de los spans.

## Apagado ordenado

```yaml
server:
  shutdown: graceful                       # valor por defecto desde Spring Boot 3.4 ('immediate' lo desactiva)
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

- Al recibir `SIGTERM`, deja de aceptar peticiones, termina las que están en curso y cierra conexiones. Los listeners de mensajes dejan de consumir y los mensajes no confirmados vuelven al broker.
- El periodo de gracia de Kubernetes (`terminationGracePeriodSeconds`) debe ser mayor que el timeout de apagado.
- La readiness pasa a `REFUSING_TRAFFIC` durante el apagado para que el balanceador deje de enviar peticiones.

## Contenedores

- Imagen con Buildpacks (`spring-boot:build-image`) o Dockerfile con capas (*layered jar*), usuario no root y JRE (no JDK).
- Memoria: la JVM detecta los límites del contenedor; ajusta `-XX:MaxRAMPercentage` en lugar de `-Xmx` fijo, según las guidelines.
- Configuración y secretos por entorno, nunca horneados en la imagen (ver `spring-config`).
- Hilos virtuales (`spring.threads.virtual.enabled=true`) si el proyecto los usa: vigila el tamaño de los pools de conexiones, que pasan a ser el límite real de concurrencia.

## Checklist

- [ ] Actuator expone solo `health`, `info` y métricas, en puerto de gestión no público
- [ ] Endpoints sensibles (`heapdump`, `env`, `loggers`...) no expuestos o protegidos
- [ ] Liveness sin dependencias externas; readiness con las imprescindibles
- [ ] Health indicators rápidos, con timeout y sin detalles internos
- [ ] Métricas de negocio con etiquetas de baja cardinalidad
- [ ] Trazas propagadas y `traceId` en los logs; muestreo configurado
- [ ] Apagado ordenado con timeout coherente con Kubernetes
- [ ] Imagen sin root, sin secretos y con límites de memoria adecuados
