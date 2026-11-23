---
name: spring-messaging
description: 'Mensajería y eventos en Spring Boot: eventos de aplicación (@EventListener, @TransactionalEventListener), Spring Kafka (@KafkaListener, KafkaTemplate), Spring AMQP/RabbitMQ (@RabbitListener), contratos de mensajes, idempotencia, patrón outbox (incluida la publicación de eventos de Spring Modulith), reintentos y DLQ, ordenación, serialización segura, seguridad y tests. Usar cuando: mensajes duplicados o repetidos que producen efectos dobles, publicar o consumir mensajes, comunicar módulos o servicios, diseñar eventos, configurar reintentos.'
argument-hint: 'Describe el evento, mensaje, productor o consumidor que necesitas.'
---

# Mensajería y eventos

Comprueba en el build y en las guidelines el broker y la librería (Spring Kafka, Spring AMQP, Spring Cloud Stream...). Las garantías de entrega, el modelo de confirmación y la ordenación cambian según el broker.

## Cuándo usar cada mecanismo

| Necesidad                                                  | Mecanismo                                           |
| ---------------------------------------------------------- | --------------------------------------------------- |
| Desacoplar funcionalidades dentro de la misma aplicación    | Eventos de aplicación (`ApplicationEventPublisher`) |
| Efecto tras confirmar la transacción, en el mismo proceso   | `@TransactionalEventListener(phase = AFTER_COMMIT)` |
| Comunicar servicios distintos o absorber picos de carga     | Broker (Kafka, RabbitMQ...)                         |
| Publicar un evento al broker de forma consistente con la BD | Patrón outbox                                       |

No introduzcas un broker sin una necesidad concreta: añade latencia, fallos parciales, consistencia eventual y coste operativo.

## Eventos de aplicación

```java
public record OrderPlacedEvent(UUID orderId, UUID userId, long totalCents) { }

@Service
public class OrderService {

    private final OrderRepository orderRepository;
    private final ApplicationEventPublisher events;

    // constructor...

    @Transactional
    public OrderResponse place(PlaceOrderRequest request, UUID userId) {
        OrderEntity order = orderRepository.save(OrderEntity.place(userId, request));
        events.publishEvent(new OrderPlacedEvent(order.getId(), userId, order.getTotalCents()));
        return orderMapper.toResponse(order);
    }
}

@Component
class InvoicingListener {

    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    void on(OrderPlacedEvent event) {
        // se ejecuta solo si la transacción del pedido se confirmó
    }
}
```

- `@EventListener` se ejecuta **síncronamente dentro** de la transacción del publicador: si falla, deshace la operación principal.
- `@TransactionalEventListener(AFTER_COMMIT)` se ejecuta tras confirmar; si falla, la operación principal ya está confirmada y **el evento se pierde** (es en memoria). Si el efecto es crítico, usa outbox.
- En un listener `AFTER_COMMIT` que escribe en base de datos necesitas una transacción nueva (`@Transactional(propagation = REQUIRES_NEW)`).
- `@Async` en el listener lo desacopla del hilo de la petición (ver limitaciones en `spring-services`).

## Outbox: publicar eventos de forma consistente

Guardar en base de datos y publicar en el broker son dos operaciones: si el proceso cae entre ambas, se pierde el evento o se publica uno de algo que no se guardó.

- **Spring Modulith** (si el proyecto lo usa): el registro de publicación de eventos (`spring-modulith-events-*`) persiste los eventos en la misma transacción y los reintenta si el listener falla; la externalización (`@Externalized`) los publica en Kafka/RabbitMQ.
- **Outbox propio**: en la misma transacción, guarda el cambio y una fila en `outbox`; un proceso programado (o CDC) publica las filas pendientes y las marca. Los consumidores son idempotentes porque el relay puede publicar dos veces.
- Para efectos no críticos, un `AFTER_COMMIT` que publica directamente puede bastar; documenta la decisión.

## Contratos de mensajes

```java
public record OrderCreatedEventV1(
        @NotNull UUID eventId,       // base de la idempotencia
        @NotNull Instant occurredAt,
        @NotNull UUID orderId,
        @NotNull UUID userId,
        @PositiveOrZero long totalCents
) {
    public static final String TOPIC = "orders.order-created.v1";
}
```

- Los mensajes son una API pública entre servicios: contrato versionado y compartido (o esquema en un registro: Avro/Protobuf con Schema Registry, según guidelines).
- `eventId`, versión y `occurredAt` en todos los eventos; `correlationId`/trazas en cabeceras.
- Cambios compatibles: añadir campos opcionales. Incompatibles: nueva versión del evento y convivencia temporal.
- Eventos en pasado (`order-created`); sin datos personales que el consumidor no necesite.

## Consumidores

```java
@Component
class OrderCreatedListener {

    private static final Logger log = LoggerFactory.getLogger(OrderCreatedListener.class);

    private final InvoicingService invoicingService;

    OrderCreatedListener(InvoicingService invoicingService) {
        this.invoicingService = invoicingService;
    }

    @KafkaListener(topics = OrderCreatedEventV1.TOPIC, groupId = "invoicing")
    void on(@Payload @Valid OrderCreatedEventV1 event) {
        invoicingService.createInvoiceForOrder(event); // idempotente
    }
}
```

- El listener es la capa de transporte: valida, delega en un servicio y deja que la confirmación la gestione el contenedor. Sin lógica de negocio.
- Valida el payload (`@Valid` con el validador configurado en el contenedor de listeners, o validación explícita en el servicio).
- Con RabbitMQ: `@RabbitListener(queues = "...")` con el mismo patrón.
- Los listeners no pasan por la `SecurityFilterChain` ni por `@RestControllerAdvice`: los errores los gestiona el *error handler* del contenedor.

## Idempotencia

La mayoría de brokers entregan **al menos una vez**: el mismo mensaje puede llegar varias veces. Todo consumidor debe ser idempotente:

```java
@Transactional
public void createInvoiceForOrder(OrderCreatedEventV1 event) {
    if (!processedEventRepository.tryInsert(event.eventId())) { // INSERT con índice único
        return; // ya procesado
    }
    invoiceRepository.save(InvoiceEntity.forOrder(event.orderId(), event.totalCents()));
}
```

- El registro del evento procesado y el efecto, en la **misma transacción**.
- No prometas *exactly once* salvo que toda la cadena lo garantice de verdad.

## Errores, reintentos y DLQ

- **Spring Kafka**: `DefaultErrorHandler` con `BackOff` y `DeadLetterPublishingRecoverer` para enviar a un topic DLT tras agotar reintentos; o reintentos no bloqueantes con `@RetryableTopic`.
- **Spring AMQP**: reintentos del contenedor (personalizables con los *customizers* de la versión instalada) y una *dead-letter exchange* configurada en la cola; `default-requeue-rejected=false` para no reencolar indefinidamente.
- En Spring Boot 4, las capacidades de reintento de Spring Kafka y Spring AMQP se basan en el núcleo de Spring Framework 7 en lugar de Spring Retry; algunas propiedades cambiaron (p. ej. `spring.kafka.retry.topic.backoff.jitter`). Usa las de la versión instalada.
- Distingue errores **transitorios** (reintentar) de **permanentes** (mensaje inválido, regla de negocio: DLQ directa, marcándolos como no reintentables).
- La DLQ se monitoriza y tiene un procedimiento de reproceso.

## Productores

```java
public CompletableFuture<Void> publish(OrderCreatedEventV1 event) {
    return kafkaTemplate.send(OrderCreatedEventV1.TOPIC, event.orderId().toString(), event)
            .thenAccept(result -> log.debug("Published {}", event.eventId()));
}
```

- `KafkaTemplate.send` es asíncrono: trata el resultado (o espera con timeout) para no perder errores de publicación.
- **Clave de partición** = id de la entidad cuando el orden importa para esa entidad.
- Productor idempotente y `acks=all` en Kafka para no perder mensajes (comprueba los valores por defecto de la versión).

## Ordenación

- Sin orden global con varios consumidores. Si importa el orden por entidad: misma clave de partición (Kafka) o una cola por entidad.
- Con concurrencia en el listener (`concurrency`), el orden solo se mantiene dentro de una partición.

## Serialización segura

- **Nunca** `spring.json.trusted.packages: "*"` ni deserialización basada en el nombre de clase que envía el productor: permite instanciar clases arbitrarias. Paquetes de confianza explícitos o mapeo de tipos.
- Nunca deserialización nativa de Java en mensajes (ver `spring-security`).
- Un mensaje que no se puede deserializar no debe bloquear la partición: usa `ErrorHandlingDeserializer` (Kafka) para enviarlo a la DLT.

## Seguridad

- TLS y credenciales propias por servicio hacia el broker, con permisos mínimos (solo sus topics/colas).
- Si el mensaje actúa en nombre de un usuario, incluye su identidad y vuelve a autorizar en el consumidor (ver `spring-auth`).

## Tests

- Unitarios del servicio que procesa el evento, incluida la **idempotencia** (procesar dos veces, efecto una sola vez).
- Integración con el broker real en Testcontainers (`@ServiceConnection` para Kafka/RabbitMQ) para validar serialización, configuración, reintentos y DLQ.
- Para esperar el procesamiento asíncrono, Awaitility en lugar de `Thread.sleep`.
- Spring Modulith ofrece `Scenario` y `PublishedEvents` para probar eventos entre módulos.

## Checklist

- [ ] Mecanismo adecuado (evento de aplicación, AFTER_COMMIT, broker, outbox)
- [ ] Eventos críticos publicados con outbox
- [ ] Contratos versionados con `eventId` y `occurredAt`
- [ ] Listeners finos, validados y sin lógica de negocio
- [ ] Consumidores idempotentes en la misma transacción que el efecto
- [ ] Reintentos con backoff, errores permanentes a la DLQ, DLQ monitorizada
- [ ] Clave de partición cuando el orden importa
- [ ] Paquetes de confianza explícitos; `ErrorHandlingDeserializer`
- [ ] TLS y credenciales por servicio
- [ ] Tests con Testcontainers y Awaitility
