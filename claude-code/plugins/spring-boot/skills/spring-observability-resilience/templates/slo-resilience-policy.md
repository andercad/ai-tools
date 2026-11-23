# Plantilla de SLO y política de resiliencia

## 1. SLO por flujo crítico
| Flujo | SLI (definición y fuente) | Objetivo | Ventana | Error budget | Alerta (burn rate) | Responsable |
|---|---|---|---|---|---|---|
| p. ej. Confirmar pedido | % de peticiones correctas con latencia < 400 ms, medido en el borde | 99,5 % | 28 días | 0,5 % | Consumo rápido → aviso inmediato; consumo lento → ticket | Equipo Pedidos |

Mide lo que percibe el usuario y usa percentiles. Sin SLO acordado, márcalo como decisión pendiente.

## 2. Telemetría
| Señal | Contenido | Herramienta | Muestreo / retención | Restricciones |
|---|---|---|---|---|
| Métricas | Golden signals, pools (HikariCP), hilos, GC, colas | Micrometer → <backend> | <...> | Etiquetas de baja cardinalidad |
| Logs | JSON con `traceId` y `spanId` | <appender → colector> | <...> | Sin datos personales ni cuerpos completos |
| Trazas | HTTP, base de datos, broker y llamadas salientes | Micrometer Tracing u OpenTelemetry (según versión) | <head/tail, %> | Propagación en mensajes |
| Health | Liveness y readiness | Actuator (grupos de health) | — | Red de gestión |

## 3. Política por dependencia
| Dependencia | Tipo | Criticidad | Timeout | Reintentos (¿idempotente?) | Circuit breaker | Bulkhead / concurrencia | Fallback / degradación |
|---|---|---|---|---|---|---|---|
| p. ej. Pasarela de pagos | HTTP | Crítica | 2 s | 2 con backoff y jitter, solo con clave de idempotencia | Umbral medido y tiempo en abierto definido | Máx. N concurrentes | Pedido en «pago pendiente» |

Regla: la suma de timeouts y reintentos de la cadena cabe en el presupuesto de latencia del flujo, y los reintentos se hacen en una sola capa.

## 4. Pruebas
| Tipo | Objetivo | Escenario | Criterio de éxito |
|---|---|---|---|
| Carga | Validar el SLO | Tráfico esperado con mezcla real | p95 y errores dentro del SLO |
| Estrés | Punto de saturación | Rampa hasta el fallo | Degradación controlada (429/503), sin cascada |
| Resistencia | Fugas | Carga media durante horas | Memoria, hilos y latencia estables |
| Fallo | Resiliencia | Dependencia lenta o caída | Breaker, fallback y recuperación según diseño |

## 5. Operación
| Alerta | Síntoma | Runbook | Responsable | Revisión |
|---|---|---|---|---|

Dashboards mínimos: SLO y error budget, golden signals por servicio, JVM y pools, dependencias (latencia, errores, estado del breaker) y colas (lag, DLQ).
