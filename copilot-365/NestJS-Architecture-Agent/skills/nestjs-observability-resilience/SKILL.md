---
name: nestjs-observability-resilience
description: 'Asesoría arquitectónica sobre observabilidad, rendimiento y resiliencia en NestJS. Usar cuando se pida definir SLI/SLO, logging estructurado, métricas, trazas distribuidas, OpenTelemetry, Application Insights, alertas, diagnóstico de rendimiento, event loop lag, memory leaks, timeouts, reintentos, circuit breaker, bulkhead, backpressure, rate limiting de capacidad, pruebas de carga, degradación controlada o dependencias de IA generativa (cuotas, latencia, coste por tokens). No usar como generador de código por defecto.'
---

# Observabilidad, rendimiento y resiliencia

## Objetivo
Hacer que el sistema sea observable y tolerante a fallos con un coste razonable, partiendo de objetivos de servicio medibles.

## 1. SLI/SLO primero
Define por flujo crítico de usuario: disponibilidad, latencia (percentiles p95/p99, no medias), tasa de errores y, si aplica, frescura/lag. Fija SLO, ventana y error budget. Las alertas se basan en consumo del error budget (burn rate) y en síntomas para el usuario, no en cada métrica técnica. Cada alerta necesita un responsable y un runbook.

## 2. Los tres pilares
- **Logs**: estructurados (JSON), nivel configurable, con `traceId`/`correlationId` en todas las líneas (por ejemplo, con pino/nestjs-pino y `AsyncLocalStorage`). Sin secretos ni PII. Muestreo en volumen alto. No registres cuerpos completos de petición.
- **Métricas**: RED para servicios (Rate, Errors, Duration) y USE para recursos. Métricas de runtime Node: event loop lag/utilization, heap, GC, handles activos, pool de BD, longitud de cola. Controla la **cardinalidad** de etiquetas (nada de IDs de usuario ni URLs sin normalizar).
- **Trazas**: OpenTelemetry con propagación W3C `traceparent` entre HTTP y mensajería (incluye headers del mensaje). El SDK/instrumentación debe inicializarse **antes** de cargar la aplicación (fichero de instrumentación precargado), o no instrumentará los módulos. Muestreo (head o tail) según volumen y coste. Exporta con OTLP a un colector, de modo que el backend (Azure Monitor/Application Insights, Grafana, Datadog) sea intercambiable.
- Health checks (`@nestjs/terminus`) son para orquestación, no sustituyen a la monitorización.

## 3. Rendimiento en Node/NestJS
Mide antes de optimizar. Puntos habituales:
- **Event loop bloqueado**: JSON enorme, criptografía síncrona, regex catastróficas, bucles de CPU. Mide con `perf_hooks.monitorEventLoopDelay`. Solución: workers, colas o streaming.
- **N+1 y consultas lentas**: revisa el plan de ejecución, índices y límites de paginación.
- **`Scope.REQUEST`/`TRANSIENT`** en providers que se propagan: recreación de instancias por petición. Evítalo si es posible.
- Serialización: `class-transformer` y `ClassSerializerInterceptor` sobre grandes colecciones son caros. Considera DTO planos o serialización de Fastify.
- Pool de BD/HTTP mal dimensionado, falta de keep-alive, fugas de memoria (listeners, cachés sin límite, closures), compresión en el proceso en lugar del borde.
- Diagnóstico: heap snapshots, `--cpu-prof`, flame graphs, `clinic.js`, trazas de duración por span.

## 4. Resiliencia
- **Timeouts en toda llamada saliente** (HTTP, BD, broker) con presupuesto de tiempo coherente de extremo a extremo y propagación de cancelación (`AbortSignal`). Sin timeout no hay resiliencia.
- **Reintentos** solo en operaciones idempotentes o con clave de idempotencia, con backoff exponencial y jitter, y con tope. Evita tormentas de reintentos y reintentos en cadena entre capas.
- **Circuit breaker** (por ejemplo, opossum o la capacidad de la plataforma/service mesh) con fallback definido, y **bulkheads** (pools o colas separados) para aislar dependencias.
- **Backpressure y límites**: control de concurrencia, colas acotadas, load shedding (responder 429/503 pronto) y rate limiting de capacidad. Consumidores de mensajes con prefetch/concurrencia limitados.
- **Degradación controlada**: define qué funcionalidad se apaga primero, caché obsoleta aceptable y feature flags.
- Evita fallos en cascada: dependencias síncronas en cadena, sin timeouts ni límites.

## 5. Dependencias de IA generativa
Trata al proveedor del modelo como una dependencia crítica con política propia: timeouts acordes a una latencia alta y variable (streaming cuando aplique), cuotas del proveedor (429) con reintentos que respeten `Retry-After` y limitación propia de concurrencia, modelo alternativo o degradación sin IA, y caché de respuestas o embeddings cuando sea válido. Mide el coste en tokens por funcionalidad y por usuario o tenant con presupuestos y alertas, la latencia hasta el primer token y la calidad mediante evaluación continua. Traza las llamadas con las convenciones semánticas de OpenTelemetry para IA generativa (verifica su estado) sin registrar prompts ni respuestas con datos personales.

## 6. Pruebas y práctica
Pruebas de carga (k6, Artillery, Azure Load Testing) con perfil realista, y pruebas de estrés, de soak (fugas) y de picos. Pruebas de fallo/caos controladas (dependencia lenta o caída, pérdida de réplica). Capacity planning con métricas reales y margen. Revisiones posteriores a incidentes sin culpas con acciones de seguimiento.

## Salida
Para definir SLO y políticas de resiliencia, rellena `templates/slo-and-dependency-policy.md`.
SLO propuestos con su medición, plan de instrumentación (logs/métricas/trazas) con estrategia de muestreo, alertas y dashboards mínimos, hallazgos o hipótesis de rendimiento a verificar, políticas de timeout/reintento/breaker/backpressure por dependencia, plan de pruebas de carga y fallo, y ADR.

## Autoevaluación
¿Hay SLO medibles? ¿Todo llamado saliente tiene timeout? ¿Los reintentos son seguros? ¿Hay correlación de trazas entre HTTP y mensajería? ¿Se controla la cardinalidad y la PII? ¿Se separan hechos medidos de hipótesis de rendimiento?
