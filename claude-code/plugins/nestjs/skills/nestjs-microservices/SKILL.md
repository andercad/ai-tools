---
name: nestjs-microservices
description: 'Microservicios y mensajería con NestJS (@nestjs/microservices). Usar al crear consumidores o productores, eventos, MessagePattern frente a EventPattern, ClientProxy, aplicaciones híbridas, transportes (RabbitMQ, Kafka, NATS, Redis, TCP, gRPC), idempotencia, acks, reintentos, DLQ, outbox, timeouts o graceful shutdown. No usar para decidir broker o dividir en microservicios a nivel arquitectura (skills nestjs-data-messaging y nestjs-modularity-domain).'
---

# Microservicios y mensajería

## Reglas clave
- Detecta el transporte y sus garantías de entrega; no extrapoles de uno a otro.
- Handlers sin lógica de negocio: delegan en servicios; payloads validados con DTOs.
- Consumidores **idempotentes**; ack tras procesar; reintentos acotados y DLQ.
- Toda llamada entre servicios con timeout; propaga ids de correlación.
- Contratos de mensajes versionados en librería de solo tipos.
- Outbox para publicar eventos de forma atómica con la transacción.

## Referencias
- [microservices.md](references/microservices.md): transportes, patrones, contratos, idempotencia, reintentos/DLQ, outbox, health checks y shutdown.
