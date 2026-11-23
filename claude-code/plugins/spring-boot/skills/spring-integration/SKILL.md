---
name: spring-integration
description: Backend Spring Boot. Integración con otros sistemas. Usar al llamar a servicios HTTP con RestClient, WebClient o interfaces HTTP, configurar timeouts, reintentos y circuit breaker, y al publicar o consumir mensajes y eventos con Kafka, RabbitMQ o eventos de aplicación, idempotencia, DLQ y patrón outbox. No usar para GraphQL (spring-graphql) ni decisiones de arquitectura de integración (spring-api-integration).
---

# Clientes HTTP y mensajería

## Reglas clave
- Toda llamada HTTP o de mensajería a otro servicio tiene timeout (conexión y lectura); reintentos solo en operaciones idempotentes y con backoff.
- Un cliente HTTP por servicio remoto, configurado en una clase `@Configuration`; no expongas DTOs externos en tu dominio, mapéalos.
- Los consumidores de mensajes son idempotentes; define DLQ/reintentos y trata los mensajes envenenados.
- Los listeners no contienen lógica de negocio: delegan en servicios.
- Mensajes como API pública: contrato versionado; publica tras confirmar la transacción (eventos transaccionales u outbox).
- No registres cuerpos con datos personales ni credenciales; propaga el id de correlación.

## Referencias
| Tema | Fichero |
|---|---|
| `RestClient`, interfaces HTTP, timeouts, reintentos, resiliencia | [http-clients.md](references/http-clients.md) |
| Kafka, RabbitMQ, eventos de aplicación, idempotencia, outbox | [messaging.md](references/messaging.md) |
