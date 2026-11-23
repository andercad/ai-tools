---
name: spring-observability-resilience
description: 'Asesoría arquitectónica sobre observabilidad, rendimiento y resiliencia en Spring Boot: SLI/SLO, métricas, logs estructurados, trazas distribuidas, Actuator, Micrometer, OpenTelemetry, alertas, timeouts, reintentos, circuit breakers, bulkheads, límites de concurrencia, capacity planning, pruebas de carga, degradación controlada y dependencias de IA generativa (cuotas, latencia, coste por tokens). Usar cuando se pregunte cómo monitorizar, diagnosticar latencia o fallos, definir SLO, evitar fallos en cascada, dimensionar capacidad o diseñar tolerancia a fallos. No usar como generador de código por defecto.'
---

# Observabilidad, rendimiento y resiliencia

## Objetivo
Hacer que el sistema sea medible, diagnosticable y tolerante a fallos, con objetivos de servicio explícitos.

## SLI/SLO primero
Antes de instrumentar, define por servicio crítico: SLI (disponibilidad, latencia p95/p99, tasa de error, frescura), SLO objetivo, ventana y error budget. Alerta sobre síntomas del usuario (consumo del error budget), no sobre cada causa técnica. Sin SLO acordados, marca el dato como decisión pendiente.

## Tres señales y correlación
- **Métricas**: Micrometer; golden signals (latencia, tráfico, errores, saturación), pools de conexiones, hilos, GC, colas. Controla la **cardinalidad** de etiquetas (sin IDs de usuario ni URLs sin plantilla).
- **Logs**: estructurados (JSON), con `traceId`/`spanId`, nivel adecuado, sin datos sensibles ni cuerpos completos. Centralizados.
- **Trazas**: OpenTelemetry (en Spring Boot vía Micrometer Tracing o la integración de OpenTelemetry según versión; verifica cuál aplica). Propaga contexto en HTTP y mensajería; muestreo definido por coste.
- **Actuator**: exponer solo endpoints necesarios, protegidos y en red de gestión. Grupos de health para liveness/readiness.
- Observa por nombre de operación y resultado, no por cuerpo de petición.

## Resiliencia: reglas de diseño
Esta skill es la dueña de la política de resiliencia de todo el sistema; las demás skills identifican dependencias y remiten aquí.
1. **Timeouts en toda llamada remota** (conexión y lectura), con un presupuesto total por petición; el timeout de quien llama debe ser mayor que la suma de lo que espera.
2. **Reintentos** solo en operaciones idempotentes, con backoff exponencial y jitter, máximo acotado; sin reintentos en cada capa de la cadena (amplificación).
3. **Circuit breaker** para dependencias inestables, con umbrales medidos y comportamiento definido en estado abierto.
4. **Bulkhead / límites de concurrencia** para aislar dependencias lentas y evitar agotar hilos o conexiones.
5. **Rate limiting y backpressure** en el borde y en consumidores de mensajes.
6. **Degradación controlada**: define qué funcionalidad se sacrifica (respuesta en caché, valor por defecto, modo lectura) y cómo se comunica.
7. **Idempotencia** en comandos y consumidores; claves de idempotencia donde haya reintentos.
Librerías habituales: Resilience4j o las capacidades de resiliencia del propio framework según versión. Verifica la API y las propiedades de la versión instalada.

## Rendimiento y capacidad
- Mide antes de optimizar: perfiles, consultas por petición, tiempos de GC, saturación de pools.
- Pruebas de carga con perfil realista (k6, Gatling, JMeter) en un entorno comparable; incluye picos, resistencia y pruebas de fallo de dependencias (caos controlado).
- Capacity planning: demanda esperada, margen, límites por instancia, punto de saturación, política de escalado.
- Concurrencia: hilos de plataforma frente a virtuales o reactive solo con beneficio medido y sin bloqueos ocultos.

## Dependencias de IA generativa
Trata al proveedor del modelo como una dependencia crítica con política propia: timeouts acordes a una latencia alta y variable (streaming cuando aplique), cuotas del proveedor (429) con reintentos que respeten `Retry-After` y limitación propia de concurrencia, modelo alternativo o degradación sin IA, y caché de respuestas o embeddings cuando sea válido. Mide el coste en tokens por funcionalidad y por usuario o tenant con presupuestos y alertas, la latencia hasta el primer token y la calidad mediante evaluación continua. Traza las llamadas con las convenciones semánticas de OpenTelemetry para IA generativa (verifica su estado) sin registrar prompts ni respuestas con datos personales.

## Operación
Runbooks por alerta, dashboards por servicio, propiedad de cada alerta, revisión post-incidente, retención de telemetría y coste de almacenamiento.

## Anti-patrones
Alertas por CPU sin impacto en usuario; etiquetas de alta cardinalidad; reintentos sin timeouts; circuit breakers sin pruebas; logs con datos personales; métricas sin dueño.

## Salida
Usa `templates/slo-resilience-policy.md` para SLO y políticas por dependencia.
SLI/SLO propuestos, modelo de telemetría, política de resiliencia por dependencia (tabla timeout/reintento/breaker/bulkhead/fallback), plan de pruebas de carga y fallo, runbooks, riesgos y ADR.

## Autoevaluación
Comprueba que cada dependencia tiene timeout y política de fallo, que no hay reintentos en cascada, que los SLO son medibles con las señales propuestas y que la cardinalidad y el coste de telemetría están acotados.
