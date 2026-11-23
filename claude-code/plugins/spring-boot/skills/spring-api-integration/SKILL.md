---
name: spring-api-integration
description: 'Asesoría arquitectónica sobre APIs e integración en Spring Boot: diseño REST (versionado, OpenAPI, errores ProblemDetail, idempotencia, paginación, compatibilidad), GraphQL (REST frente a GraphQL, resolvers, N+1/BatchMapping, límites, federación), mensajería y arquitectura orientada a eventos (Kafka, RabbitMQ, Spring Cloud Stream, contratos de eventos, orden, reprocesado, DLQ) y clientes HTTP hacia terceros e integración con modelos de IA generativa (LLM, RAG, tool calling). Usar cuando se pregunte cómo diseñar o versionar una API, elegir entre síncrono y asíncrono, integrar sistemas, diseñar eventos o contratos, elegir REST, GraphQL o mensajería o integrar un LLM o un asistente con RAG. No usar como generador de código por defecto.'
---

# APIs, eventos e integración empresarial

## Objetivo
Diseñar contratos de integración según las necesidades del consumidor: REST, GraphQL o mensajería. Todos son adaptadores de entrada o salida sobre los mismos casos de uso; ninguno contiene lógica de negocio. La política de timeouts, reintentos y circuit breakers la define `spring-observability-resilience`; aquí solo se identifica qué dependencias la necesitan.

## Elegir el estilo
| Necesidad | Preferir |
|---|---|
| Comandos y recursos, máquina a máquina, cacheable, partners externos | REST |
| Varios clientes con vistas distintas sobre un dominio coherente | GraphQL |
| Desacoplar en el tiempo, notificar hechos, absorber picos, varios consumidores | Mensajería/eventos |
| Respuesta inmediata necesaria para continuar | Síncrono (REST/gRPC) |
Pueden coexistir. Elegir asíncrono implica aceptar consistencia eventual y diseñar su visibilidad para el usuario.

## Diseño REST
- **Contrato**: OpenAPI como fuente de verdad (contract-first para APIs públicas o de partners; code-first aceptable en APIs internas con generación verificada en CI). Evita dos fuentes de verdad.
- **Recursos y verbos**: recursos orientados al dominio, no a tablas; DTOs propios, nunca entidades JPA.
- **Errores**: formato estándar `ProblemDetail` (RFC 9457) con tipos estables, sin stack traces ni detalles internos.
- **Idempotencia**: `PUT`/`DELETE` idempotentes; `POST` con clave de idempotencia cuando el cliente pueda reintentar (pagos, pedidos).
- **Paginación**: cursor para colecciones grandes o cambiantes; offset solo con volumen acotado. Límite máximo de página.
- **Versionado y compatibilidad**: cambios aditivos sin nueva versión; versión (en ruta o cabecera, una convención única) solo ante cambios incompatibles, con política de deprecación y fechas. Spring Framework 7 incorpora soporte de versionado de API; verifica disponibilidad en la versión instalada.
- **Concurrencia**: `ETag`/`If-Match` para evitar actualizaciones perdidas cuando aplique.
- **Validación** en el borde (Bean Validation) y reglas de negocio en el caso de uso.
- **Pruebas**: tests de contrato (Spring Cloud Contract, Pact o validación del OpenAPI) y detección de cambios incompatibles en CI.

## Diseño GraphQL con Spring
- Detecta la versión de Spring Boot y Spring for GraphQL antes de fijar APIs.
- Decide **schema-first** o generación de esquema solo con un criterio explícito.
- Controladores/resolvers y `@SchemaMapping` traducen GraphQL a puertos de entrada; no acceden directamente a JPA.
- Evita N+1 con `@BatchMapping` o DataLoader/`BatchLoaderRegistry`; mide número de consultas y tamaño de batches.
- Paginación cursor-based para conexiones grandes o cambiantes; offset solo si su semántica y coste son aceptables.
- Errores de dominio estables sin exponer stack traces ni detalles de persistencia.
- Autorización por operación y recurso, y por campo solo cuando esté justificado. El filtrado visual no sustituye al control en el caso de uso.
- Límites de profundidad, complejidad, tamaño de batch, tiempo de ejecución y payload; persisted queries y allowlists para superficies sensibles.
- Observa por nombre de operación, resultado, duración y errores, evitando cardinalidad no controlada y el cuerpo completo de la query.

### Federación
No federes únicamente porque haya microservicios. Exige ownership claro de subgrafos, contratos de entidad, composición validada en CI, compatibilidad y operación de gateway/router. Spring for GraphQL integra Apollo Federation mediante `FederationSchemaFactory`, `@EntityMapping`, `@SchemaMapping`, `@BatchMapping` y DataLoader; confirma la API en la versión instalada.

## Mensajería y eventos
- **Tipo de mensaje**: distingue *evento* (hecho pasado, el emisor no espera nada), *comando* (petición a un destinatario) y *evento con estado completo* frente a *notificación* que obliga a consultar. Elige según acoplamiento y volumen.
- **Broker**: Kafka para logs de eventos, alto volumen, reprocesado y varios consumidores independientes; RabbitMQ (u otro broker de colas) para enrutado flexible y colas de trabajo; servicio gestionado del cloud cuando reduzca operación. Justifica por patrón de uso, no por moda.
- **Abstracción**: Spring Cloud Stream si se necesita portabilidad entre brokers; Spring Kafka/Spring AMQP directos si se usan capacidades específicas.
- **Contrato del evento**: nombre en pasado, versión de esquema, identificador, fecha, correlación y clave de partición. Registro de esquemas (Avro/JSON Schema/Protobuf) y reglas de compatibilidad cuando haya varios equipos.
- **Entrega**: asume *at-least-once*; consumidores **idempotentes** (deduplicación por id). Publicación fiable con outbox (ver `spring-data-transactions`).
- **Orden**: garantizado solo por partición/clave; diseña sin depender de orden global.
- **Errores**: reintentos acotados, **DLQ** con proceso de revisión y reprocesado, mensajes venenosos aislados.
- **Evolución**: cambios aditivos; consumidores tolerantes a campos desconocidos; nunca reutilizar un campo con otro significado.
- **Observabilidad**: propagación de traza en cabeceras, lag del consumidor y antigüedad de DLQ como métricas.
- Event sourcing y CQRS completos solo con drivers explícitos (auditoría total, reconstrucción de estado, modelos de lectura muy distintos).

## Integración con terceros
Cliente HTTP con timeouts y autenticación definidos, mapeo anticorrupción para no filtrar el modelo externo al dominio, límites de tasa del proveedor, contrato de errores, entorno de pruebas (WireMock o sandbox) y monitorización de disponibilidad del tercero. `RestClient` o HTTP Service Clients según versión; Spring Boot 4 añade auto-configuración para HTTP Service Clients; no lo presupongas en Boot 3.

## Integración con IA generativa
- El modelo es una dependencia externa más: adaptador de salida detrás de un puerto; el dominio no conoce el proveedor ni el prompt. Spring AI ofrece abstracciones de chat, embeddings, almacenes vectoriales y llamada a herramientas (tool calling); verifica la versión compatible con tu Spring Boot antes de citar APIs.
- **RAG**: ingesta (troceado, embeddings y metadatos de origen y permisos), recuperación filtrada por los permisos del usuario, citas a la fuente y respuesta explícita cuando no hay información. Antes que un producto nuevo, valora la base de datos o el buscador que ya operas si tienen capacidades vectoriales (por ejemplo, pgvector).
- **Herramientas**: expón casos de uso existentes con el mínimo privilegio; el modelo propone, el caso de uso autoriza y valida. Acciones irreversibles con confirmación humana.
- **Contrato**: streaming (SSE) hacia el cliente cuando la latencia lo justifique; salida estructurada validada contra un esquema antes de usarla.
- **Evaluación**: conjunto de preguntas con respuestas esperadas y métricas de calidad (exactitud, fidelidad a las fuentes) en CI; repítela al cambiar de modelo, de prompt o de datos.
- Seguridad en `spring-security-identity`; timeouts, cuotas y coste en `spring-observability-resilience`.

## Salida
Para revisar un contrato o una integración existente, usa `reference/api-contract-checklist.md`.
Estilo elegido y por qué, contrato y ownership, versionado y compatibilidad, diseño de errores e idempotencia, flujo de integración o de eventos, estrategia N+1/paginación cuando aplique, seguridad, observabilidad, pruebas de contrato y ADR.

## Autoevaluación
Comprueba que el estilo resuelve una necesidad real, que no hay negocio en controladores, resolvers ni listeners, que los consumidores son idempotentes, que existe política de compatibilidad, que federación y event sourcing no siguen automáticamente a microservicios y que las APIs citadas corresponden a la versión instalada.
