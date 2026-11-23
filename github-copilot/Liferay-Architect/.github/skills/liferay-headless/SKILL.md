---
name: liferay-headless
description: 'Liferay DXP. APIs headless e integración: APIs de entrega y administración (headless-delivery, headless-admin-user, headless-admin-taxonomy, objects en /o/c/), GraphQL, filtros, ordenación, paginación, campos y búsqueda, autenticación (OAuth2, sesión con p_auth), batch engine para cargas masivas, API Explorer, REST Builder para APIs propias con OpenAPI, y patrones de integración con sistemas externos. Usar cuando: consumir Liferay desde otra aplicación o un frontend, crear un endpoint propio, importar o exportar datos masivos, integrar Liferay con un ERP, CRM u otro sistema, elegir entre REST y GraphQL.'
argument-hint: 'Describe qué datos necesitas leer o escribir, desde dónde y con qué volumen.'
---

# APIs headless e integración

Las APIs headless son **versionadas y estables entre actualizaciones**: son la forma recomendada de integrar Liferay con otros sistemas y de comunicar client extensions con el portal.

## Descubrir las APIs

- **API Explorer** en `/o/api` de la instancia: lista todas las APIs de tu versión (incluidas las de tus Objects) con su contrato OpenAPI. **Comprueba ahí rutas, parámetros y esquemas**; no los supongas.
- Familias habituales:
  - Entrega de contenidos: `/o/headless-delivery/v1.0/...` (sites, contenido estructurado, documentos, páginas, blogs...).
  - Usuarios y organizaciones: `/o/headless-admin-user/v1.0/...`.
  - Taxonomía: `/o/headless-admin-taxonomy/v1.0/...`.
  - Objects: `/o/c/<nombre-en-plural-en-minúsculas>/`.
  - Commerce: `/o/headless-commerce-.../v1.0/...` (ver `liferay-commerce`).

## Consultas

```bash
curl -H "Authorization: Bearer ${TOKEN}" \
  "https://portal.example.com/o/c/orders/?filter=status%20eq%20'pending'&sort=dateCreated:desc&page=1&pageSize=50&fields=id,reference,status"
```

- `filter` (sintaxis OData), `sort`, `page`/`pageSize`, `search`, `fields` (solo los campos necesarios), `nestedFields` y `restrictFields` según la API.
- **Pagina siempre**: no pidas colecciones completas.
- Las APIs devuelven solo lo que el usuario autenticado tiene permiso a ver.

## Autenticación

| Caso | Mecanismo |
|---|---|
| Sistema externo, servidor a servidor | **OAuth2** *client credentials* con una aplicación con los scopes mínimos (client extension `oAuthApplicationHeadlessServer`) |
| Aplicación que actúa en nombre del usuario | **OAuth2** *authorization code* con PKCE (client extension `oAuthApplicationUserAgent`) |
| Custom element dentro del portal | Sesión del usuario + token CSRF `p_auth` (`x-csrf-token`), o OAuth2 |
| Pruebas locales | Autenticación básica solo en desarrollo; nunca en producción |

- Scopes **mínimos** por integración; una aplicación OAuth2 por sistema integrado, para poder revocarla por separado.
- Credenciales en secretos del entorno, nunca en el repositorio.

## GraphQL

- Disponible en `/o/graphql` con los mismos permisos. Útil para combinar varias entidades en una sola petición desde un frontend.
- Para integraciones de sistemas y cargas masivas, preferir REST y batch.

## Batch engine

- Importación y exportación masiva (JSON, CSV...) de entidades soportadas: objects, usuarios, contenidos, catálogos de Commerce...
- Usa los endpoints `/batch` de cada API o el servicio de batch (`/o/headless-batch-engine/...`); consulta el contrato en el API Explorer.
- Procesamiento asíncrono: consulta el estado de la tarea; no lances una petición por registro.
- Con **ERC** en los registros, las importaciones repetidas actualizan en lugar de duplicar.

## REST Builder (APIs propias)

**No disponible en SaaS** (requiere módulos OSGi). Antes de crear una API propia, comprueba si basta con la API de un Object.

```yaml
# rest-config.yaml (módulo -impl)
apiDir: "../orders-rest-api/src/main/java"
apiPackagePath: "com.acme.orders.rest"
application:
    baseURI: "/acme-orders"
    className: "OrdersRestApplication"
    name: "Acme.Orders"
author: "Acme"
clientDir: "../orders-rest-client/src/main/java"
testDir: "../orders-rest-test/src/testIntegration/java"
```

- Diseña el contrato en `rest-openapi.yaml` (OpenAPI), genera con `./gradlew buildREST` y escribe solo la implementación en las clases `*ResourceImpl`.
- La implementación **delega en servicios** que comprueban permisos; no accedas a la persistencia desde el recurso.
- Versiona la API (`v1.0`); los cambios incompatibles van a una versión nueva.
- Comprueba que el endpoint está registrado con `jaxrs:check` en Gogo Shell.

```java
@Component(
	properties = "OSGI-INF/liferay/rest/v1_0/order.properties",
	scope = ServiceScope.PROTOTYPE, service = OrderResource.class
)
public class OrderResourceImpl extends BaseOrderResourceImpl {

	@Override
	public Order getOrder(Long orderId) throws Exception {
		return _toOrder(_acmeOrderService.getOrder(orderId));
	}

	private Order _toOrder(AcmeOrder acmeOrder) {
		Order order = new Order();

		order.setId(acmeOrder.getOrderId());
		order.setReference(acmeOrder.getReference());

		return order;
	}

	@Reference
	private AcmeOrderService _acmeOrderService;

}
```

(Las anotaciones y propiedades exactas las genera REST Builder para tu versión; no las escribas a mano.)

## Patrones de integración

- **Liferay → sistema externo** ante un evento: acción de objeto o de workflow como client extension (ver `liferay-client-extensions`).
- **Sistema externo → Liferay**: el sistema llama a las APIs headless con OAuth2; para volumen, batch.
- **Sincronizaciones periódicas**: un microservicio programado que use batch, con ERC para idempotencia.
- **Timeouts, reintentos con espera creciente e idempotencia** en todas las integraciones; registra las correlaciones para poder diagnosticar.

## Checklist

- [ ] Rutas y contratos comprobados en el API Explorer de la versión
- [ ] Paginación y `fields` en las consultas
- [ ] OAuth2 con scopes mínimos y una aplicación por integración; sin autenticación básica en producción
- [ ] Batch para cargas masivas, con ERC
- [ ] REST Builder solo si la API del Object no basta (y no en SaaS); implementación que delega en servicios con permisos
- [ ] Integraciones con timeouts, reintentos e idempotencia
