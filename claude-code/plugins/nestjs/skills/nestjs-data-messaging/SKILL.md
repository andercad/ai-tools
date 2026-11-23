---
name: nestjs-data-messaging
description: 'Asesoría arquitectónica sobre datos, eventos y mensajería en NestJS. Usar cuando se pida elegir o comparar ORM/acceso a datos (TypeORM, Prisma, MikroORM, Drizzle, Kysely, SQL), SQL frente a NoSQL, transacciones, migraciones de esquema, caché (Redis), consistencia eventual, outbox/inbox, sagas, idempotencia, colas y brokers (Kafka, RabbitMQ, NATS, BullMQ, Azure Service Bus), gRPC o diseño de eventos. No usar como generador de código por defecto.'
---

# Datos, eventos y mensajería

## Objetivo
Elegir persistencia y comunicación asíncrona según las garantías necesarias (consistencia, orden, latencia, volumen) y el coste operativo. No compartas la base de datos entre servicios como atajo.

## Persistencia: criterios de elección
Parte de los requisitos: modelo de datos, consultas, transacciones, volumen, equipo, tooling de migraciones y complejidad del dominio.
| Opción | Encaja cuando | Cuidado con |
|---|---|---|
| TypeORM | Equipo familiarizado con decoradores y data mapper/active record, integración nativa con Nest | Entidades ligadas al ORM, consultas complejas, comportamiento de migraciones y relaciones perezosas |
| Prisma | Tipado fuerte, esquema declarativo, buen DX y migraciones | Sin unit of work, mapeo a dominio manual, limitaciones con SQL muy específico, verifica soporte de tu versión y base de datos |
| MikroORM | Dominio rico con identity map y unit of work | Curva de aprendizaje, menos adopción |
| Query builder (Kysely/Knex/Drizzle) o SQL | Consultas complejas, rendimiento, control total | Más código propio de mapeo |
Reglas: en hexagonal, el ORM vive solo en adaptadores de salida y las entidades del ORM no son el modelo de dominio. Mantén un único enfoque de acceso a datos por contexto. Verifica la compatibilidad con la versión de Node/NestJS instalada.

## Transacciones y migraciones
- Define la frontera transaccional en el caso de uso (unit of work), no en el controller. Propaga la transacción con el mecanismo del ORM o con `AsyncLocalStorage`/nestjs-cls, sin pasar `EntityManager` por todas las firmas.
- No mezcles en una transacción llamadas externas lentas (HTTP, broker).
- Migraciones versionadas, revisadas y ejecutadas en el pipeline, no con `synchronize: true` en producción. Estrategia **expand/contract** (añadir, migrar datos, cambiar código, eliminar) para desplegar sin parada y permitir rollback de aplicación con esquema compatible hacia atrás.
- Pool de conexiones dimensionado: instancias x pool no debe superar el máximo de la base de datos. Valora PgBouncer/proxy y límites en serverless.

## Caché
Define qué se cachea, TTL, invalidación y consistencia aceptable antes de añadirla. Cache-aside como patrón por defecto. Protege contra cache stampede. No guardes datos sensibles sin necesidad. Redis para caché distribuida. La caché en memoria por proceso solo para datos inmutables o muy tolerantes.

## Mensajería: elegir el modelo
| Necesidad | Opciones típicas |
|---|---|
| Tareas en segundo plano, reintentos, delays en el mismo sistema | BullMQ/Redis |
| Mensajería empresarial con routing, DLQ y entrega fiable | RabbitMQ, Azure Service Bus |
| Streaming de eventos, alto volumen, reproducción, orden por clave | Kafka / Azure Event Hubs |
| Pub/sub ligero y baja latencia | NATS |
| RPC entre servicios con contrato tipado | gRPC |
Reglas: distingue **comando** (un destinatario, puede fallar) de **evento** (hecho pasado, varios consumidores). Un broker es infraestructura que alguien debe operar: si no existe un equipo/plataforma que lo gestione, valora servicios gestionados. El patrón request-response sobre brokers (`send()` en `@nestjs/microservices`) añade acoplamiento temporal. Úsalo con criterio.

## Fiabilidad
- **Outbox transaccional**: escribe el cambio y el evento en la misma transacción y publica de forma asíncrona (polling o CDC). Evita el dual write.
- **Consumidores idempotentes** (inbox/tabla de mensajes procesados o claves naturales): la entrega "al menos una vez" es lo normal.
- Reintentos con backoff y jitter, **dead-letter queue**, mensajes venenosos y política de reproceso.
- Orden: Kafka solo garantiza orden dentro de una partición. Elige la clave de partición según la entidad. Cuidado con el rebalanceo y el escalado de consumidores.
- Contratos de eventos versionados (schema registry, JSON Schema/Avro/Protobuf) y compatibilidad hacia atrás. Incluye `eventId`, `occurredAt`, `correlationId` y versión.
- Sagas (orquestación o coreografía) para transacciones distribuidas, con compensaciones. Evita 2PC. Si necesitas consistencia fuerte entre servicios, quizá deban ser un solo servicio.
- CQRS y event sourcing solo con drivers claros (auditoría completa, lecturas muy distintas de escrituras). Por defecto, no.

## Verificación
Tests de integración con base de datos y broker reales (Testcontainers), tests de contrato de eventos, pruebas de idempotencia y de fallo (reentrega, duplicados, broker caído), pruebas de migración sobre copia de datos.

## Salida
Para definir eventos o mensajes, usa `templates/event-contract.md`.
Modelo de datos y propiedad por contexto, elección de persistencia con criterios, estrategia transaccional y de migración, topología de mensajería, garantías de entrega y orden, estrategia de fallos/DLQ, contratos de eventos, operación y ADR.

## Autoevaluación
¿Hay dual write sin outbox? ¿Son idempotentes los consumidores? ¿Existe base de datos compartida entre servicios? ¿Hay plan de migración compatible y rollback? ¿Se justifica el broker y quién lo opera? ¿Se evita CQRS/ES sin driver?
