# Checklist de datos, consistencia y migraciones

Marca cada punto como Cumple / No cumple / No verificado / No aplica y cita la evidencia. «No verificado» nunca equivale a «Cumple».

## Propiedad de los datos
- [ ] Cada tabla o colección tiene un módulo o servicio dueño.
- [ ] Ningún servicio lee ni escribe directamente las tablas de otro; si ocurre, está registrado como deuda con fecha de salida.

## Transacciones
- [ ] El límite transaccional está en el caso de uso, no en controladores ni repositorios.
- [ ] No hay llamadas HTTP, mensajería síncrona ni esperas dentro de una transacción.
- [ ] Se conocen las limitaciones de `@Transactional` (autoinvocación, visibilidad, `rollbackFor`) en la versión instalada.
- [ ] Bloqueo optimista (`@Version`) por defecto; pesimista solo con contención medida.
- [ ] `open-in-view` decidido de forma explícita.

## Consistencia entre componentes
- [ ] Sin 2PC/XA salvo restricción justificada y documentada.
- [ ] Eventos publicados con outbox (o con el registro de publicación de Spring Modulith dentro del monolito).
- [ ] Consumidores idempotentes, con reintentos acotados y dead-letter.
- [ ] Sagas con compensaciones y estados intermedios visibles para el usuario.

## Migraciones de esquema
- [ ] Flyway o Liquibase versionado; nada de `ddl-auto=update` en producción.
- [ ] Cambios incompatibles con expand/contract: la versión anterior de la aplicación funciona con el esquema nuevo.
- [ ] Migraciones probadas con volumen realista, con bloqueos y duración estimados.

## Rendimiento
- [ ] Consultas por petición medidas; N+1 tratado (fetch join, `EntityGraph`, proyecciones, batch size).
- [ ] Pool dimensionado: instancias × tamaño del pool ≤ conexiones máximas de la base de datos menos la reserva de administración.
- [ ] Caché solo con TTL, invalidación, métricas de acierto y dueño.

## Protección y recuperación
- [ ] Datos sensibles clasificados, cifrados y enmascarados en logs.
- [ ] Retención y borrado definidos por tipo de dato según la normativa aplicable.
- [ ] RPO y RTO acordados; última restauración probada: <AAAA-MM-DD>.

## Pruebas
- [ ] Testcontainers con el motor real, pruebas de migración, de concurrencia y de idempotencia de consumidores.

## Resultado
Riesgos priorizados con acción, responsable y forma de verificarlo.
