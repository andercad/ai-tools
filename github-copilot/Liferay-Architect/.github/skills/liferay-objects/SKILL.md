---
name: liferay-objects
description: 'Liferay DXP. Objects: definir modelos de datos sin código (campos, picklists, relaciones, validaciones, reglas de estado, acciones, vistas, layouts, permisos y ámbito company o site), APIs headless generadas, exportar e importar definiciones, desplegarlas como código con batch, acciones y validaciones como client extensions, y Liferay Forms. Usar cuando: crear una entidad o modelo de datos nuevo, añadir campos o relaciones, validar datos, ejecutar lógica al crear o actualizar un registro, exponer datos por API, construir un formulario, migrar entidades de Service Builder.'
argument-hint: 'Describe la entidad: campos, relaciones, quién la usa y qué debe pasar al crear o modificar registros.'
---

# Objects

Objects es la forma recomendada de crear **modelos de datos** en Liferay: funciona en todos los modelos de despliegue, genera APIs REST y GraphQL, y se integra con permisos, workflow, búsqueda, formularios, fragments y exportación/importación. Cuándo usar Service Builder en su lugar: ver `liferay-service-builder`.

## Diseño de la definición

| Elemento | Reglas |
|---|---|
| Nombre | PascalCase en singular (`ServiceRequest`); Liferay usa `C_ServiceRequest` como nombre interno de los objetos personalizados |
| Ámbito | **Company** (datos de toda la instancia) o **Site** (datos por site). Decide antes de publicar: no se cambia después sin migrar |
| Campos | Tipos adecuados (texto, número, fecha, booleano, picklist, adjunto, relación...); obligatorios y únicos según negocio |
| Picklists | Para valores cerrados; con ERC estables |
| Relaciones | Uno a muchos o muchos a muchos; define el comportamiento al borrar |
| Validaciones | Expresiones o Groovy en self-hosted y PaaS; para lógica externa, validación como client extension |
| Estados | Campo picklist de estado con reglas de transición |
| Acciones | Al crear, actualizar, borrar o manualmente: notificaciones, webhooks, actualizar campos, scripts, client extension |
| Permisos | Por rol y acción; *account restriction* si los datos pertenecen a cuentas (B2B) |
| Vistas y layouts | Para la administración en la interfaz |

- Se **publica** la definición para que exista la tabla y la API. Antes de publicar, revisa nombre y ámbito.
- **External reference codes (ERC)** estables en definiciones, campos, picklists y registros que se crean desde código o se migran: permiten actualizar en lugar de duplicar entre entornos.

## Objects como código

Lo que debe existir igual en todos los entornos se versiona:

1. Diseña la definición en un entorno de desarrollo.
2. **Exporta** la definición (interfaz o API batch) a JSON.
3. Despliégala con una **client extension batch** (o un site initializer si forma parte de un site) en el resto de entornos (ver `liferay-client-extensions`).

```yaml
# client-extensions/acme-objects-batch/client-extension.yaml
assemble:
    - from: batch
      into: batch
acme-objects-batch:
    name: Acme Objects Batch
    oAuthApplicationHeadlessServer: acme-objects-batch-oauth-headless-server
    type: batch
acme-objects-batch-oauth-headless-server:
    .serviceAddress: localhost:8080
    .serviceScheme: http
    name: Acme Objects Batch OAuth Headless Server
    scopes:
        - Liferay.Headless.Admin.Workflow.everything
        - Liferay.Object.Admin.REST.everything
    type: oAuthApplicationHeadlessServer
```

(Los `scopes` dependen de lo que importe el batch; comprueba los nombres de scope de tu versión en la referencia de la client extension batch.)

- No crees a mano en producción definiciones que existen en desarrollo.
- Los cambios incompatibles (borrar campos, cambiar tipos) se planifican como migración, con copia de seguridad.

## APIs generadas

- Cada Object publicado expone REST en `/o/c/<nombre-en-plural-en-minúsculas>/` y GraphQL, con filtros, ordenación, paginación, búsqueda y batch (ver `liferay-headless`).
- Consulta el contrato exacto en el **API Explorer** (`/o/api`) de tu instancia.
- Las APIs respetan los permisos del usuario autenticado.

## Lógica al crear o actualizar

| Necesidad | Mecanismo |
|---|---|
| Notificar, actualizar un campo, llamar a un webhook | Acción de objeto estándar |
| Lógica propia (validar con un sistema externo, calcular, sincronizar) | **Acción de objeto como client extension** (microservicio con OAuth2), disponible en todos los modelos de despliegue |
| Validación que no se expresa con las reglas estándar | **Validación de objeto como client extension** |
| Lógica en el servidor sin microservicio (solo self-hosted/PaaS) | Scripts Groovy en acciones o validaciones; model listener como último recurso (ver `liferay-service-builder`) |

```yaml
acme-order-sync-action:
    name: Acme Order Sync Action
    oAuth2ApplicationExternalReferenceCode: acme-order-sync-oauth-user-agent
    resourcePath: /orders/sync
    type: objectAction
    allowedObjectDefinitionNames:
        - C_Order
acme-order-sync-oauth-user-agent:
    name: Acme Order Sync OAuth User Agent
    scopes:
        - C_Order.everything
    type: oAuthApplicationUserAgent
```

- `resourcePath` se combina con la URL del microservicio de la aplicación OAuth2.
- `allowedObjectDefinitionNames` limita la acción a los objects indicados (por defecto está disponible para todos).
- El microservicio **valida el JWT** de cada petición y es **idempotente** (la acción puede reintentarse).

## Liferay Forms

- Para formularios de captura de datos, Liferay Forms puede guardar sus entradas en un **Object** (almacenamiento de objeto), lo que da API, permisos y workflow sobre las respuestas.
- Para formularios con lógica de interfaz muy específica, un custom element que llame a la API del Object.

## Rendimiento y volumen

- Índices: los campos usados para filtrar deben ser indexables/buscables según la configuración del campo.
- Para cargas masivas, usa la API batch, no miles de llamadas individuales.
- Con volúmenes muy altos, mide antes de decidir; documenta la decisión si eliges otra tecnología.

## Checklist

- [ ] Nombre y ámbito (company/site) decididos antes de publicar
- [ ] ERC estables en definiciones, campos, picklists y registros migrados
- [ ] Permisos por rol; *account restriction* si aplica
- [ ] Definición desplegada como código (batch o site initializer), no creada a mano
- [ ] Lógica externa como acción o validación de client extension, con JWT validado e idempotencia
- [ ] Contrato de la API comprobado en el API Explorer
