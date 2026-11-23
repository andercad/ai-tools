# Checklist de integraciones y Client Extensions

Marca cada punto como Cumple / No cumple / No verificado / No aplica y cita la evidencia. «No verificado» nunca equivale a «Cumple».

## Decisión
- [ ] Tipo de Client Extension verificado para la release y la modalidad.
- [ ] El servicio externo tiene responsabilidad propia y un equipo que lo opera; no es un proxy.
- [ ] No se usan APIs internas cuando existe Headless.

## Contrato
- [ ] OpenAPI (o esquema del evento o de la acción) versionado y con dueño.
- [ ] Pruebas de contrato en el pipeline del servicio.
- [ ] Política de compatibilidad y deprecación acordada con Liferay y con los consumidores.

## Seguridad
- [ ] Aplicación OAuth2 por integración con scopes mínimos (User Agent para usuarios, Headless Server para servicio a servicio).
- [ ] Las llamadas de Liferay al servicio (acciones, webhooks) se autentican y se validan.
- [ ] Secretos en almacén externo; nada en `client-extension.yaml`, repositorio ni imagen.
- [ ] Autorización en Liferay o en el servicio, nunca solo en el frontend.

## Fiabilidad
- [ ] Consumidores de acciones y batch idempotentes (la entrega puede repetirse).
- [ ] Timeouts, reintentos con backoff solo en operaciones idempotentes, circuit breaker y degradación definida.
- [ ] Batch: tamaño de lote, orden, reintentos e impacto en búsqueda e índices medidos.

## Operación
- [ ] Health checks, métricas, trazas con correlación y logs sin datos sensibles.
- [ ] Build reproducible y versionado; la misma build se promueve entre entornos.
- [ ] Rollback definido y probado según la modalidad.
- [ ] Cargas con ciclos de vida o escalado incompatibles en proyectos separados.

## Resultado
Riesgos priorizados con acción, responsable y verificación; decisiones que corresponden al agente de Angular, Spring Boot o NestJS.
