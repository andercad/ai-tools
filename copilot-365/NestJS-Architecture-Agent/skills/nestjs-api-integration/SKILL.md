---
name: nestjs-api-integration
description: 'Asesoría arquitectónica sobre REST, GraphQL, federación, WebSockets, webhooks, integración e IA generativa en NestJS. Usar cuando se pida decidir REST frente a GraphQL, code-first frente a schema-first, Apollo frente a Mercurius según el adaptador, diseñar resolvers, DataLoader, paginación, límites de complejidad, subscriptions, federación, contratos OpenAPI, versionado de API, integración con APIs externas o integración con modelos de IA generativa (LLM, RAG, tool calling). No usar como generador de código por defecto.'
---

# APIs, GraphQL e integración

## Objetivo
Diseñar REST, GraphQL, WebSockets, webhooks y clientes externos según consumidores y atributos de calidad. Los controllers y resolvers son adaptadores de entrada y no contienen negocio.

## Decisión REST frente a GraphQL
- **GraphQL** encaja cuando varios clientes necesitan selecciones distintas o agregación flexible sobre dominios coherentes (por ejemplo, un BFF para web y móvil).
- **REST** suele ser preferible en comandos simples, integración máquina a máquina, recursos cacheables por HTTP o cuando el coste operativo de GraphQL no compensa.
- Pueden convivir sobre los mismos casos de uso. Evita GraphQL "porque sí": añade complejidad de caché, autorización por campo, límites de coste y observabilidad.

## REST: diseño y contrato
- Contrato primero: OpenAPI como artefacto versionado, con `@nestjs/swagger` o spec manual, y revisión de breaking changes en CI.
- Versionado: elige una estrategia (URI, header o media type) y úsala siempre. Define política de deprecación y ventana de soporte.
- Errores homogéneos (por ejemplo, RFC 9457 Problem Details) mediante un filtro global. Paginación, filtrado y ordenación consistentes.
- Idempotencia en operaciones no seguras mediante `Idempotency-Key`. Concurrencia optimista con ETag/If-Match donde proceda.
- DTO de entrada/salida separados de entidades de dominio y ORM. No expongas entidades directamente.

## Diseño GraphQL con NestJS
- Detecta versión, driver (Apollo o Mercurius) y adaptador HTTP (Express o Fastify). No mezcles configuraciones.
- Decide **code-first o schema-first** y mantén una única fuente de verdad.
- Los resolvers mapean argumentos/contexto a casos de uso. Ni Prisma ni TypeORM se usan directamente desde el resolver.
- Evita N+1 con DataLoader **por petición** (no compartas la caché entre peticiones) o batching equivalente.
- Paginación cursor-based para conexiones grandes o cambiantes. Offset solo si su consistencia y coste son aceptables.
- Guards, interceptores y filtros necesitan contexto GraphQL. La autorización por recurso va en el caso de uso, no solo en el resolver.
- Limita profundidad, complejidad, aliases, batching, tamaño de petición y tiempo. En producción, desactiva introspección/playground salvo necesidad y considera persisted queries o allowlists en superficies sensibles.
- Observa por `operationName`, duración y resultado, sin registrar queries, variables ni tokens completos.
- Subscriptions exigen modelo de autenticación, revocación, backpressure, reconexión y escalado del transporte (pub/sub externo con varias instancias). No sustituyen a un broker.

## Federación
Federation compone subgrafos independientes tras un gateway/router, pero no debe seguir automáticamente a los microservicios. Exige ownership por dominio y equipo, composición y breaking-change checks en CI, estrategia de entidades, SLO del router y degradación ante subgrafos caídos. Verifica las limitaciones de la combinación instalada. La documentación de NestJS advierte, por ejemplo, de restricciones con subscriptions en federación.

## WebSockets, webhooks e integraciones externas
- WebSockets: autenticación en el handshake, autorización por evento, escalado con adapter externo (Redis), límites de conexiones y mensajes.
- Webhooks entrantes: verificación de firma (HMAC) con comparación en tiempo constante y body crudo, protección contra replay (timestamp, ID), responder rápido y procesar de forma asíncrona. Salientes: reintentos con backoff, firma y registro de entregas.
- APIs externas: contrato, autenticación, timeout explícito, reintentos solo en operaciones idempotentes, circuit breaker, rate limits, anti-corruption layer para aislar el modelo del tercero y observabilidad.
- Express vs Fastify: Fastify suele ofrecer mejor rendimiento, pero verifica la compatibilidad de middleware y librerías antes de recomendar el cambio.

## Integración con IA generativa
- El modelo es un adaptador de salida detrás de un puerto (token de inyección); controllers y casos de uso no dependen del SDK del proveedor. Opciones: SDK oficial del proveedor o librerías de orquestación del ecosistema Node; verifica madurez, licencia y versión antes de recomendarlas.
- **RAG**: ingesta asíncrona con colas (BullMQ u otra), troceado, embeddings y metadatos de origen y permisos; recuperación filtrada por los permisos del usuario; citas a la fuente. Antes que un producto nuevo, valora la base de datos o el buscador que ya operas si tienen capacidades vectoriales (por ejemplo, pgvector u OpenSearch).
- **Herramientas** (tool calling): casos de uso existentes con el mínimo privilegio; el modelo propone y el caso de uso autoriza y valida. Acciones irreversibles con confirmación humana.
- **Streaming**: SSE (`@Sse()`) u otra respuesta en streaming hacia el cliente, con cancelación cuando el cliente se desconecta (`AbortSignal`); salida estructurada validada contra un esquema.
- **Evaluación**: conjunto de preguntas con respuestas esperadas en CI; repítela al cambiar de modelo, de prompt o de datos.
- Seguridad en `nestjs-security-identity`; timeouts, cuotas y coste en `nestjs-observability-resilience`.

## Salida
Para revisar una API existente antes de producción, recorre `reference/api-production-checklist.md`.
Decisión REST/GraphQL, contrato y versionado, code-first/schema-first y driver, flujo de resolución, N+1 y paginación, seguridad y límites, subscriptions, federación si procede, operación, pruebas de contrato y ADR.

## Autoevaluación
GraphQL tiene driver y enfoque coherentes. Los resolvers y controllers no contienen negocio. DataLoader es por petición. Seguridad y límites están tratados. Federación y subscriptions no se recomiendan por moda. El contrato está versionado y probado.
