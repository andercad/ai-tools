---
name: spring-config-observability
description: Backend Spring Boot. Configuración y operación. Usar al definir @ConfigurationProperties, perfiles, application.yml, secretos, variables de entorno, o al configurar Actuator, health checks, probes, métricas Micrometer, trazas, logs estructurados, apagado ordenado, hilos virtuales y ajuste en contenedor. No usar para decisiones de runtime y despliegue (spring-cloud-runtime) ni resiliencia arquitectónica (spring-observability-resilience).
---

# Configuración y observabilidad

## Reglas clave
- `@ConfigurationProperties` (records, validadas con `@Validated`) en lugar de `@Value` disperso; sin secretos en `application.yml` versionado.
- Perfiles solo para diferencias reales de entorno; comprueba los nombres de propiedades en la referencia de la versión instalada (cambian entre versiones).
- Actuator: exponer solo lo necesario (`health`, `info`, `metrics`, `prometheus`), protegido; nunca `env`, `heapdump`, `configprops` ni `loggers` sin protección.
- Probes de liveness y readiness separados; apagado ordenado (`server.shutdown=graceful`).
- Métricas con Micrometer, trazas con Micrometer Tracing/OpenTelemetry, logs sin datos personales y con id de correlación.
- Memoria en contenedor con `-XX:MaxRAMPercentage`, no `-Xmx` fijo.

## Referencias
| Tema | Fichero |
|---|---|
| `@ConfigurationProperties`, perfiles, secretos, metadatos | [config.md](references/config.md) |
| Actuator, health, métricas, trazas, apagado, contenedores | [observability.md](references/observability.md) |
