# Checklist de APIs para producción (REST y GraphQL)

Marca Cumple / No cumple / No verificado y cita la evidencia.

## Contrato
- [ ] Contrato publicado y versionado (OpenAPI o esquema GraphQL) con una única fuente de verdad.
- [ ] Detección automática de breaking changes en CI.
- [ ] Política de versionado y deprecación (cabeceras `Deprecation`/`Sunset` o equivalente) comunicada.
- [ ] Formato de error homogéneo (Problem Details o convención GraphQL) con códigos estables.

## Diseño REST
- [ ] Recursos y verbos coherentes. Códigos HTTP correctos.
- [ ] Paginación con límite máximo, filtrado y ordenación consistentes.
- [ ] Idempotencia en POST críticos (`Idempotency-Key`). Concurrencia optimista (ETag/If-Match) donde haya ediciones concurrentes.
- [ ] Caché HTTP (Cache-Control, ETag) en recursos legibles cacheables.
- [ ] DTO separados de entidades de dominio y ORM.

## GraphQL
- [ ] Driver y adaptador coherentes (Apollo/Mercurius con Express/Fastify). Code-first o schema-first, no ambos.
- [ ] Resolvers delgados que llaman a casos de uso.
- [ ] DataLoader por petición para relaciones. Sin N+1 en las consultas habituales.
- [ ] Paginación por cursor en listas grandes. Límite máximo de `first`/`last`.
- [ ] Límites de profundidad, complejidad, aliases, batching y tamaño.
- [ ] Introspección y playground restringidos en producción. Persisted queries o allowlist en superficies sensibles.
- [ ] Autorización por campo/recurso en la capa de aplicación.
- [ ] Errores sin detalles internos. Observabilidad por `operationName`.
- [ ] Subscriptions solo con justificación, autenticación en la conexión y pub/sub escalable.
- [ ] Federación solo con ownership claro, composición en CI y SLO del router.

## Integraciones
- [ ] Todas las llamadas salientes con timeout, reintentos solo idempotentes y circuit breaker.
- [ ] Anti-corruption layer para modelos de terceros.
- [ ] Webhooks: firma HMAC, anti-replay, procesamiento asíncrono e idempotente.
- [ ] WebSockets: autenticación en el handshake, autorización por evento y adapter compartido para varias réplicas.

## Pruebas
- [ ] Tests de contrato (consumidor/proveedor o validación de esquema).
- [ ] Tests e2e de flujos críticos y de autorización (accesos indebidos rechazados).
- [ ] Pruebas de carga sobre las operaciones más costosas.
