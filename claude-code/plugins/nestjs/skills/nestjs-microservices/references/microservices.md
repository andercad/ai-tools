# Microservicios y mensajería

Comprueba en `package.json` y en el `CLAUDE.md` del proyecto el **transporte** usado (RabbitMQ, Kafka, NATS, Redis, TCP, gRPC...) y sus garantías de entrega. Los ejemplos usan RabbitMQ; las opciones, el modelo de *ack* y la ordenación cambian según el transporte.

## Cuándo usarlos

- No introduzcas un broker ni un microservicio sin una necesidad concreta: desacoplar despliegues, absorber picos de carga, procesar en segundo plano o integrar sistemas.
- Un microservicio añade latencia de red, fallos parciales, consistencia eventual y coste operativo. Un módulo bien aislado dentro del mismo servicio suele ser suficiente.
- Varios microservicios en el mismo repositorio forman un monorepo: estructura, contratos compartidos y despliegue por aplicación en `nestjs-workspace`.

## Patrones de comunicación

| Patrón                 | Decorador          | Cliente              | Uso                                                   |
| ---------------------- | ------------------ | -------------------- | ----------------------------------------------------- |
| Petición-respuesta     | `@MessagePattern`  | `client.send()`      | Necesitas una respuesta (consulta a otro servicio)    |
| Evento                 | `@EventPattern`    | `client.emit()`      | Notificar algo que ya ha ocurrido; nadie responde     |

- Prefiere **eventos** para integrar servicios: reducen el acoplamiento temporal. Usa petición-respuesta con moderación; una cadena de `send()` síncronos reproduce un monolito distribuido.
- Nombra los eventos en pasado y por dominio: `order.created`, `payment.failed`. Los mensajes de petición, en imperativo: `orders.get-by-id`.

## Aplicación híbrida (HTTP + mensajería)

Permite leer la configuración con `ConfigService` y exponer health checks HTTP:

```typescript
// main.ts
async function bootstrap(): Promise<void> {
  const app = await NestFactory.create(AppModule);
  const config = app.get(ConfigService);

  app.connectMicroservice<MicroserviceOptions>(
    {
      transport: Transport.RMQ,
      options: {
        urls: [config.getOrThrow<string>('RABBITMQ_URL')],
        queue: 'orders',
        queueOptions: { durable: true },
        noAck: false,      // ack manual: el mensaje solo se elimina si se procesó bien
        prefetchCount: 10, // mensajes en vuelo por consumidor
      },
    },
    { inheritAppConfig: true }, // aplica también los useGlobal* (pipes, filtros...)
  );

  app.enableShutdownHooks();
  await app.startAllMicroservices();
  await app.listen(config.get<number>('PORT', 3000));
}
void bootstrap();
```

- Lo registrado con `APP_PIPE`, `APP_GUARD`, `APP_FILTER` y `APP_INTERCEPTOR` se aplica también a los handlers de mensajes. Revisa que esos componentes funcionen en el contexto `rpc` (ver más abajo).
- Para un servicio que solo consume mensajes, `NestFactory.createMicroservice()` también es válido; en ese caso la configuración del transporte no puede usar `ConfigService` del propio módulo y se resuelve antes de crear la app.

## Contratos de mensajes

Los mensajes son una API pública entre servicios: define un contrato versionado y compartido (paquete o librería de contratos; en un monorepo, una librería `type:contract`, ver `nestjs-workspace`), igual que los DTOs.

```typescript
export class OrderCreatedEvent {
  static readonly pattern = 'order.created';

  @IsUUID()
  readonly eventId!: string;        // identificador único: base de la idempotencia

  @IsInt()
  @Min(1)
  readonly version!: number;        // versión del contrato

  @IsISO8601()
  readonly occurredAt!: string;

  @IsUUID()
  readonly orderId!: string;

  @IsUUID()
  readonly userId!: string;

  @IsInt()
  @Min(0)
  readonly totalCents!: number;
}
```

- Cada evento lleva `eventId`, `version`, `occurredAt` y, si aplica, `correlationId`.
- Cambios compatibles: añadir campos opcionales. Cambios incompatibles (quitar, renombrar o cambiar el tipo de un campo): nueva versión del evento y período de convivencia.
- No incluyas en los eventos datos personales que el consumidor no necesite: los mensajes se replican, se reintentan y acaban en DLQ y logs.
- En un monorepo, aunque todos los servicios compilen juntos, se **despliegan** por separado: un cambio de contrato sigue necesitando versión y convivencia.

## Consumidores

```typescript
@Controller()
export class OrderEventsController {
  private readonly logger = new Logger(OrderEventsController.name);

  constructor(private readonly invoicing: InvoicingService) {}

  @EventPattern(OrderCreatedEvent.pattern)
  async handleOrderCreated(
    @Payload() event: OrderCreatedEvent,
    @Ctx() context: RmqContext,
  ): Promise<void> {
    const channel = context.getChannelRef() as Channel;
    const message = context.getMessage() as Message;

    try {
      await this.invoicing.createInvoiceForOrder(event); // idempotente
      channel.ack(message);
    } catch (error: unknown) {
      this.logger.error(
        `Failed to process ${OrderCreatedEvent.pattern} ${event.eventId}`,
        error instanceof Error ? error.stack : undefined,
      );
      // requeue=false: el broker lo envía a la dead-letter queue configurada
      channel.nack(message, false, false);
    }
  }
}
```

- Los handlers son la capa de transporte: validan, delegan en un servicio y confirman. Sin lógica de negocio.
- `@Payload()` con una clase validada: el `ValidationPipe` global también valida mensajes. Un mensaje inválido no debe reintentarse indefinidamente: va a la DLQ.
- Con ack manual, **confirma solo después** de haber persistido el resultado.
- `Channel` y `Message` son tipos de `amqplib`; los objetos de contexto cambian por transporte (`KafkaContext`, `NatsContext`...).

## Entrega al menos una vez e idempotencia

La mayoría de brokers garantizan entrega **al menos una vez**: el mismo mensaje puede llegar varias veces (reintentos, reconexiones, rebalanceos). Todo consumidor debe ser **idempotente**:

```typescript
@Injectable()
export class InvoicingService {
  constructor(private readonly dataSource: DataSource) {}

  async createInvoiceForOrder(event: OrderCreatedEvent): Promise<void> {
    await this.dataSource.transaction(async (manager) => {
      // Índice único en processed_events.event_id
      const inserted = await manager
        .createQueryBuilder()
        .insert()
        .into(ProcessedEventEntity)
        .values({ eventId: event.eventId })
        .orIgnore()
        .execute();

      if (inserted.identifiers.length === 0) {
        return; // ya procesado: no repetir el efecto
      }

      await manager.save(InvoiceEntity, { orderId: event.orderId, totalCents: event.totalCents });
    });
  }
}
```

- El registro del evento procesado y el efecto van en la **misma transacción**.
- No prometas "exactly once" salvo que el transporte y toda la cadena lo garanticen de verdad.

## Publicar eventos de forma consistente (outbox)

Guardar en base de datos y publicar en el broker son dos operaciones: si el proceso cae entre ambas, se pierde el evento o se publica uno de algo que no se guardó. Patrón **outbox**:

1. En la misma transacción del caso de uso, guarda el cambio y una fila en `outbox` con el evento.
2. Un proceso (tarea programada o CDC) publica las filas pendientes y las marca como enviadas.
3. Los consumidores son idempotentes, porque el relay puede publicar dos veces.

```typescript
await this.dataSource.transaction(async (manager) => {
  const order = await manager.save(OrderEntity, { userId, status: 'created', totalCents });
  await manager.save(OutboxEntity, {
    pattern: OrderCreatedEvent.pattern,
    payload: { eventId: randomUUID(), version: 1, occurredAt: new Date().toISOString(), orderId: order.id, userId, totalCents },
  });
});
```

Para efectos no críticos (estadísticas, notificaciones opcionales), un `emit()` directo tras el commit puede ser aceptable; documenta la decisión.

## Clientes (productores)

```typescript
export const ORDERS_SERVICE = 'ORDERS_SERVICE';

@Module({
  imports: [
    ClientsModule.registerAsync([
      {
        name: ORDERS_SERVICE,
        inject: [ConfigService],
        useFactory: (config: ConfigService): ClientProvider => ({
          transport: Transport.RMQ,
          options: {
            urls: [config.getOrThrow<string>('RABBITMQ_URL')],
            queue: 'orders',
            queueOptions: { durable: true },
          },
        }),
      },
    ]),
  ],
  providers: [OrdersGateway],
  exports: [OrdersGateway],
})
export class OrdersClientModule {}
```

```typescript
@Injectable()
export class OrdersGateway {
  constructor(@Inject(ORDERS_SERVICE) private readonly client: ClientProxy) {}

  /** Petición-respuesta con timeout: nunca esperes indefinidamente a otro servicio. */
  getOrder(orderId: string): Promise<OrderSummary> {
    return firstValueFrom(
      this.client.send<OrderSummary, { orderId: string }>('orders.get-by-id', { orderId }).pipe(
        timeout(5_000),
      ),
    );
  }

  /** emit() publica aunque no haya suscripción; esperar solo confirma que el broker lo aceptó. */
  async publishOrderCreated(event: OrderCreatedEvent): Promise<void> {
    await lastValueFrom(this.client.emit(OrderCreatedEvent.pattern, event), { defaultValue: undefined });
  }
}
```

- `send()` devuelve un Observable **frío**: si nadie se suscribe (`firstValueFrom`, `subscribe`), el mensaje **no se envía** y no hay error. `emit()` devuelve uno **caliente**: el evento se publica aunque no te suscribas; esperar su resultado solo sirve para saber si el broker lo aceptó.
- Timeout obligatorio en `send()`. Ante timeout o error, decide explícitamente: error al cliente, valor degradado o reintento (solo si la operación remota es idempotente).
- Encapsula el `ClientProxy` en un gateway: el resto del código no depende del transporte. En un monorepo, el gateway de un servicio puede vivir en una librería que importan sus consumidores.

## Reintentos y dead-letter queue

- Reintentos con espera creciente (*backoff*) y un número máximo; después, a la **DLQ**.
- Distingue errores transitorios (red, base de datos no disponible: reintentar) de permanentes (mensaje inválido, regla de negocio: DLQ directa).
- La DLQ se monitoriza y tiene un procedimiento de reproceso.
- En RabbitMQ, la DLQ se configura en la cola con `x-dead-letter-exchange`; en Kafka, con un topic de reintentos/DLQ gestionado por la aplicación.

## Ordenación y Kafka

- Con varios consumidores no hay orden global. Si el orden importa para una entidad, usa una clave de partición (Kafka: `key` = id de la entidad) o una cola por entidad.
- Kafka: define el `groupId` del consumidor, el tratamiento de los *offsets* y el comportamiento ante rebalanceos según la documentación de la versión instalada.

## Guards, pipes y filtros en contexto `rpc`

- Un guard global de autenticación HTTP (`JwtAuthGuard` con `APP_GUARD`) también se ejecuta en los handlers de mensajes, donde no hay cabecera `Authorization`, y los rechazaría. Haz que distinga el contexto:

```typescript
canActivate(context: ExecutionContext): boolean | Promise<boolean> | Observable<boolean> {
  if (context.getType() === 'rpc') {
    return true; // la confianza en los mensajes se establece en el transporte (ver Seguridad)
  }
  // ... lógica HTTP/GraphQL (ver nestjs-auth)
}
```

- El `ValidationPipe` lanza `BadRequestException`; el **filtro global multicontexto** (ver `nestjs-api`) la convierte en un error del transporte. Un filtro solo-HTTP no funciona en `rpc`.
- Interceptores que usan `switchToHttp()` deben comprobar `context.getType()` (ver `nestjs-api`).

## Seguridad

- Conexión al broker con TLS y credenciales propias por servicio, con permisos mínimos (solo las colas/topics que usa).
- No confíes ciegamente en el contenido: valida siempre el payload.
- Si un mensaje actúa en nombre de un usuario, incluye su identidad y vuelve a comprobar la autorización en el consumidor.

## Correlación y observabilidad

- Propaga el `correlationId` de la petición HTTP original en el mensaje y regístralo en los logs del consumidor (ver `nestjs-testing-quality`).
- Métricas mínimas: mensajes procesados, fallidos, en DLQ, tiempo de procesamiento y tamaño de la cola.
- Si el proyecto usa OpenTelemetry, propaga el contexto de traza en las cabeceras del mensaje.

## Health checks y apagado

- Health checks con `@nestjs/terminus` (conexión al broker y a la base de datos), expuestos por HTTP en la app híbrida.
- `app.enableShutdownHooks()`: al recibir `SIGTERM`, deja de aceptar mensajes, termina los que están en curso y cierra conexiones. Con ack manual, los mensajes no confirmados vuelven a la cola.

## gRPC

- Contrato en ficheros `.proto` versionados; genera los tipos TypeScript a partir de ellos.
- `@GrpcMethod('Service', 'Method')` en el handler; deadlines en el cliente (equivalente al timeout).
- Evolución compatible de los `.proto`: no reutilices números de campo eliminados.

## Tests

- Unitarios: invoca el método del handler directamente con un payload y un contexto mockeado; comprueba el `ack`/`nack` y la llamada al servicio.
- Idempotencia: procesa el mismo evento dos veces y comprueba que el efecto ocurre una sola vez.
- Integración: broker real con Testcontainers para validar configuración de colas, DLQ y serialización.

## Checklist

- [ ] Broker/microservicio justificado
- [ ] Eventos para integración; `send()` solo cuando hace falta respuesta
- [ ] Contratos versionados con `eventId`, `version`, `occurredAt`
- [ ] Payloads validados; inválidos a la DLQ
- [ ] Consumidores idempotentes; ack tras persistir
- [ ] Outbox (o decisión documentada) para publicar eventos críticos
- [ ] `send()` con timeout y suscrito; resultado de `emit()` gestionado
- [ ] Reintentos con backoff y DLQ monitorizada
- [ ] Guards, pipes, filtros e interceptores compatibles con el contexto `rpc`
- [ ] TLS y credenciales por servicio en el broker
- [ ] Correlation ID propagado; métricas y health checks
- [ ] `enableShutdownHooks()` y apagado ordenado
