# Checklist de contratos de API e integración

Marca cada punto como Cumple / No cumple / No verificado / No aplica y cita la evidencia. «No verificado» nunca equivale a «Cumple».

## Contrato y gobierno
- [ ] Una única fuente de verdad del contrato (OpenAPI, esquema GraphQL o esquema de eventos) con dueño identificado.
- [ ] Política de compatibilidad escrita: cambios aditivos sin versión nueva; versión nueva solo ante ruptura; deprecación con fechas.
- [ ] Detección de cambios incompatibles en CI (diff de OpenAPI, validación de esquema o pruebas de contrato).
- [ ] DTO propios; ninguna entidad JPA forma parte del contrato.

## REST
- [ ] Errores con `ProblemDetail` (RFC 9457), tipos estables y sin detalles internos.
- [ ] `POST` reintentables con clave de idempotencia; `PUT` y `DELETE` idempotentes.
- [ ] Paginación con tamaño máximo (cursor en colecciones grandes o cambiantes).
- [ ] Control de concurrencia (`ETag`/`If-Match`) donde haya actualizaciones concurrentes.
- [ ] Validación de entrada en el borde y reglas de negocio en el caso de uso.

## GraphQL (si aplica)
- [ ] N+1 resuelto con `@BatchMapping` o DataLoader y medido.
- [ ] Límites de profundidad, complejidad, tamaño de batch y tiempo de ejecución.
- [ ] Autorización por operación y recurso en el caso de uso.
- [ ] Superficies sensibles con persisted queries o allowlist.
- [ ] Federación justificada por ownership de subgrafos, no por el número de servicios.

## Eventos y mensajería (si aplica)
- [ ] Nombre en pasado, identificador, fecha, versión de esquema, correlación y clave de partición.
- [ ] Publicación fiable (outbox) y consumidores idempotentes.
- [ ] Reintentos acotados y DLQ con dueño y procedimiento de reprocesado.
- [ ] Orden requerido solo por clave; nada depende de un orden global.
- [ ] Registro de esquemas o reglas de compatibilidad si hay varios equipos.

## Terceros
- [ ] Timeouts y política de fallo definidos con `spring-observability-resilience`.
- [ ] Capa anticorrupción: el modelo externo no llega al dominio.
- [ ] Límites de tasa del proveedor, entorno de pruebas (sandbox o WireMock) y monitorización de disponibilidad.

## Seguridad y observabilidad
- [ ] Autenticación y autorización definidas por operación (ver `spring-security-identity`).
- [ ] Propagación de traza en HTTP y en cabeceras de mensajes; métricas por operación con cardinalidad acotada.

## Resultado
Lista priorizada de incumplimientos con riesgo, acción recomendada, responsable y forma de verificarlo.
