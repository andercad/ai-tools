---
name: liferay-commerce
description: 'Liferay DXP. Liferay Commerce: canales, catálogos, productos y variantes (SKU), opciones y especificaciones, listas de precios y promociones, descuentos, inventario y almacenes, cuentas y grupos de cuenta (B2B y B2C), pedidos y su workflow, checkout, métodos de pago y envío, impuestos, APIs headless de Commerce, client extensions de Commerce (paso de checkout, integración de pago, motor de envío) e integración con ERP y PIM. Usar cuando: montar una tienda B2B o B2C, cargar catálogos, configurar precios por cliente, integrar una pasarela de pago o un transportista, personalizar el checkout, sincronizar pedidos o stock con un ERP.'
argument-hint: 'Describe el escenario de Commerce: B2B o B2C, catálogo, precios, pagos, envíos o integración.'
---

# Liferay Commerce

## Conceptos

| Concepto | Qué es |
|---|---|
| **Canal** | Punto de venta (un site de tienda, un marketplace, una integración); define moneda, métodos de pago y envío, impuestos y workflow de pedidos |
| **Catálogo** | Conjunto de productos; puede compartirse entre canales |
| **Producto / SKU** | Producto con opciones (talla, color) que generan SKUs; especificaciones para atributos descriptivos |
| **Lista de precios / promoción** | Precios por canal, cuenta o grupo de cuentas; promociones temporales |
| **Descuento** | Reglas sobre productos, categorías o pedido; con o sin cupón |
| **Inventario / almacén** | Stock por SKU y almacén; almacenes asociados a canales |
| **Cuenta** | Cliente empresa (B2B, con usuarios y roles de cuenta) o persona (B2C) |
| **Pedido** | Con estados y workflow de aprobación (por ejemplo, aprobación interna del comprador en B2B) |

- Diseña primero **canales, catálogos y cuentas**: el resto (precios, permisos, visibilidad) se apoya en ellos.
- B2B: grupos de cuentas para precios y visibilidad por segmento de clientes; roles de cuenta (comprador, aprobador, administrador de cuenta).

## Extender el flujo de compra

| Necesidad | Mecanismo recomendado |
|---|---|
| Nueva pasarela de pago | Client extension **Payment Integration** (`commercePaymentIntegration`) |
| Cálculo de envío de un transportista | Client extension **Shipping Engine** |
| Paso adicional en el checkout | Client extension **Checkout Step** |
| Lógica al cambiar el estado de un pedido | Workflow de pedidos con acción de workflow como client extension |
| Interfaz de tienda a medida | Fragments y widgets de Commerce; custom elements que llamen a las APIs de entrega |
| Extensión que no cubren las client extensions | Puntos de extensión Java de Commerce (solo self-hosted y PaaS) |

```yaml
acme-payment-integration:
    name: Acme Payment Integration
    oAuth2ApplicationExternalReferenceCode: acme-payment-oauth-user-agent
    paymentIntegrationType: 4
    paymentIntegrationTypeSettings:
        provider: acme-pay
    type: commercePaymentIntegration
acme-payment-oauth-user-agent:
    name: Acme Payment OAuth User Agent
    scopes:
        - Liferay.Headless.Commerce.Admin.Payment.everything
    type: oAuthApplicationUserAgent
```

- `paymentIntegrationType` define el tipo de integración (online estándar, online con redirección u offline, gestionados por Liferay o por una función externa); consulta la tabla de valores de la referencia de tu versión. El ejemplo usa una redirección gestionada por una función externa.
- Los scopes exactos dependen de las APIs que llame el microservicio; compruébalos en la referencia.
- **Liferay Commerce no almacena datos de tarjetas.** Usa pasarelas que los gestionen (tokenización, redirección); si tuvieras que almacenarlos, aplica PCI DSS.
- Los microservicios de Commerce siguen las reglas de `liferay-client-extensions`: JWT validado, idempotencia, timeouts.

## APIs de Commerce

- Administración: `/o/headless-commerce-admin-catalog/v1.0/...`, `.../admin-pricing/...`, `.../admin-inventory/...`, `.../admin-order/...`, `.../admin-account/...`.
- Entrega (tienda): `/o/headless-commerce-delivery-catalog/v1.0/...`, `.../delivery-cart/...`, `.../delivery-order/...`.
- Comprueba nombres y contratos en el **API Explorer** de tu versión.

## Integración con ERP y PIM

- **Catálogo, precios y stock** desde el ERP/PIM hacia Liferay con **batch** y ERC (el mismo código de producto o SKU del sistema origen), en procesos programados o por eventos.
- **Pedidos** desde Liferay hacia el ERP: workflow de pedidos o acción sobre el pedido que publique en el ERP, con idempotencia y reintentos.
- Define qué sistema es **dueño** de cada dato (precios, stock, clientes) y no lo edites en el otro.
- Para volúmenes grandes de catálogo, cargas incrementales por fecha de modificación.

## Upgrades

- Commerce tiene pasos propios en los upgrades de versión: sigue la guía *Upgrading Liferay Commerce* de tu versión antes de actualizar la base de datos (ver `liferay-upgrades`).

## Analytics

- Los canales de Commerce pueden sincronizarse con Analytics Cloud para analizar comportamiento de compra (ver `liferay-analytics`).

## Checklist

- [ ] Canales, catálogos y cuentas diseñados antes de precios y descuentos
- [ ] B2B con grupos de cuentas y roles de cuenta
- [ ] Pagos, envíos y pasos de checkout como client extensions cuando sea posible
- [ ] Sin almacenamiento de datos de tarjetas
- [ ] Integraciones ERP/PIM con batch, ERC, dueño de cada dato definido e idempotencia
- [ ] Guía de upgrade de Commerce revisada antes de actualizar
