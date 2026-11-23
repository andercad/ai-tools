# Plantilla de contrato de evento o mensaje

## Identificación
- **Nombre**: `<contexto>.<entidad>.<hecho-en-pasado>` (p. ej. `orders.order.placed`) o `<contexto>.<comando>` para comandos.
- **Tipo**: Evento (hecho, varios consumidores) | Comando (petición, un destinatario).
- **Productor (owner)**: <servicio/módulo y equipo>.
- **Consumidores conocidos**: <lista>.
- **Canal**: <topic/cola/exchange y broker>.
- **Clave de partición/orden**: <p. ej. orderId> y motivo.

## Sobre (envelope)
| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| eventId | UUID | Sí | Identificador único para idempotencia |
| eventType | string | Sí | Nombre del evento |
| schemaVersion | integer | Sí | Versión del esquema del payload |
| occurredAt | ISO-8601 UTC | Sí | Momento del hecho en el dominio |
| producer | string | Sí | Servicio emisor |
| correlationId | string | Sí | Correlación con la petición de origen |
| causationId | string | No | Evento/comando que lo provocó |
| traceparent | string | Recomendado | Contexto W3C para trazas distribuidas |
| tenantId | string | Si multi-tenant | Aislamiento de datos |

## Payload
Define campos, tipos, obligatoriedad y ejemplo. Incluye solo lo necesario (evita PII si no es imprescindible). Decide entre evento "delgado" (IDs, el consumidor consulta) y "gordo" (estado completo, el consumidor no consulta), y justifica la elección.

## Garantías y comportamiento
- Entrega: al menos una vez. Los consumidores deben ser idempotentes por `eventId`.
- Publicación: outbox transaccional desde <tabla/mecanismo>.
- Orden: garantizado solo por <clave> dentro de <partición/cola>.
- Reintentos: <política, backoff>. DLQ: <nombre> y procedimiento de reproceso.
- Retención y reproducción: <periodo, si aplica>.

## Evolución
- Compatibilidad: solo cambios aditivos en la misma versión. Campos nuevos opcionales.
- Cambios incompatibles: nueva versión o nuevo evento, publicación en paralelo durante <ventana> y retirada comunicada.
- Registro de esquemas: <schema registry / repositorio de contratos> y validación en CI.

## Seguridad
Clasificación de datos del payload, cifrado si aplica, quién puede publicar y consumir en el canal.
