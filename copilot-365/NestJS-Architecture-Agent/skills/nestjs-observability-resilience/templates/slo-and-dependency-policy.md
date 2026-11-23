# Plantilla de SLO y políticas de dependencias

## 1. SLO por flujo crítico
| Flujo de usuario | SLI (definición exacta y fuente) | Objetivo | Ventana | Error budget | Alerta (burn rate) | Responsable |
|---|---|---|---|---|---|---|
| p. ej. Crear pedido | % de `POST /orders` con 2xx/4xx esperados y latencia < 500 ms, medido en el gateway | 99,5 % | 28 días | 0,5 % | 2 % del budget en 1 h → página; 5 % en 6 h → ticket | Equipo Pedidos |

Notas: mide lo que percibe el usuario (borde o gateway), excluye errores del cliente justificados, usa percentiles.

## 2. Instrumentación
| Señal | Qué | Herramienta/exportador | Muestreo/retención | Restricciones |
|---|---|---|---|---|
| Logs | JSON con traceId, nivel, contexto | <pino → colector> | <...> | Sin PII ni secretos |
| Métricas | RED, event loop, heap, pool BD, colas | <OTel → backend> | <...> | Etiquetas de baja cardinalidad |
| Trazas | HTTP, BD, broker, llamadas salientes | <OTel SDK precargado → OTLP> | <head/tail, %> | Propagación en mensajes |

## 3. Políticas por dependencia
| Dependencia | Tipo | Criticidad | Timeout | Reintentos (idempotente?) | Circuit breaker | Bulkhead/concurrencia | Fallback/degradación |
|---|---|---|---|---|---|---|---|
| p. ej. API de pagos | HTTP síncrona | Crítica | 2 s | 2 con backoff+jitter, solo con Idempotency-Key | Abre con 50 % de fallo en 20 peticiones, 30 s | Máx. 20 concurrentes | Pedido en estado "pago pendiente" |

Regla: la suma de timeouts y reintentos en la cadena debe caber dentro del presupuesto de latencia del flujo.

## 4. Pruebas
| Tipo | Objetivo | Carga/escenario | Criterio de éxito |
|---|---|---|---|
| Carga | Validar SLO con tráfico esperado | <rps, mezcla de operaciones> | p95 y errores dentro del SLO |
| Estrés | Encontrar el punto de saturación | Rampa hasta el fallo | Degradación controlada (429/503), sin caída en cascada |
| Soak | Detectar fugas | Carga media durante horas | Memoria y latencia estables |
| Fallo | Validar resiliencia | Dependencia lenta/caída, pérdida de réplica | Breakers, fallback y recuperación según diseño |

## 5. Dashboards mínimos
Vista de SLO y error budget, vista RED por servicio, salud de runtime Node, dependencias (latencia/errores/estado del breaker), colas (profundidad, lag, DLQ).
