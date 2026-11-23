---
name: liferay-client-extensions
description: 'Liferay DXP. Client extensions: client-extension.yaml, tipos frontend (custom element, IFrame, CSS y JS globales, theme CSS, favicon, sprite map, import maps, frontend data sets, static content), configuración (instance settings, OAuth2 user agent y headless server), microservicios (acciones y validaciones de objeto, acciones de workflow, notificaciones, CAPTCHA) con Spring Boot o Node, batch y site initializer, y Commerce (pagos, envíos, pasos de checkout). Usar cuando: crear un widget con React, Angular u otro framework, añadir CSS o JS a todas las páginas, ejecutar lógica externa ante eventos de Liferay, versionar configuración, desplegar datos iniciales, extender Liferay en SaaS.'
---

# Client extensions

Las client extensions extienden Liferay **sin desplegar código dentro del servidor**: se comunican por APIs headless y funcionan en **todos** los modelos de despliegue (self-hosted, PaaS y SaaS). Son la opción preferida frente a módulos OSGi (ver el orden de extensión del agente).

## Tipos

| Categoría | Tipos (nombres de la referencia oficial) | Para qué |
|---|---|---|
| Frontend | Custom Element, IFrame, CSS, JavaScript, Theme CSS, Theme Favicon, Theme Sprite Map, JavaScript Import Map Entry, Frontend Data Set Filter y Cell Renderer, Editor Config Contributor, Static Content | Widgets, estilos, scripts y recursos |
| Configuración | Instance Settings, OAuth Headless Server, OAuth User Agent | Configuración como código y credenciales OAuth2 |
| Microservicio | Object Action, Object Validation, Object Entry Manager, Workflow Action, Notification Type, CAPTCHA | Lógica fuera de Liferay ante eventos |
| Batch | Batch, Site Initializer | Datos, definiciones y sites como código |
| Commerce | Checkout Step, Payment Integration, Shipping Engine | Extender el flujo de compra (ver `liferay-commerce`) |

- El valor exacto del campo `type` de cada uno está en la **Client Extension Reference** de la documentación; algunos tipos aparecen en versiones concretas. Compruébalo para tu versión antes de usarlo.
- Copia los ejemplos del **sample workspace** oficial (`com.liferay.sample.workspace`) o de `liferay-portal`, que incluyen todos los tipos.

## Proyectos y agrupación

- Cada proyecto vive en `client-extensions/<proyecto>/` con un `client-extension.yaml`. Al compilarse genera un único archivo desplegable **LUFFA** (`.zip`).
- Agrupaciones permitidas en un mismo proyecto:
  - Varias del mismo tipo.
  - Configuración + batch.
  - Configuración + frontend.
  - Configuración + microservicio.
- **No** se puede mezclar frontend con microservicio en el mismo proyecto: el build falla.

## Frontend

```yaml
# client-extensions/acme-orders-custom-element/client-extension.yaml
assemble:
    - from: build/static
      into: static
acme-orders-custom-element:
    cssURLs:
        - style.*.css
    friendlyURLMapping: acme-orders
    htmlElementName: acme-orders
    instanceable: false
    name: Acme Orders
    portletCategoryName: category.client-extensions
    type: customElement
    urls:
        - main.*.js
    useESM: true
```

- **Custom element**: la aplicación se registra como elemento HTML personalizado (`htmlElementName`) y se añade a las páginas como widget. Puede escribirse en React, Angular, Vue o JavaScript sin framework. El código del framework lo resuelve el agente o las guías de ese framework; aquí se cubre la integración con Liferay.
- **IFrame**: para aplicaciones alojadas fuera que no deben compartir el DOM de la página.
- **CSS y JavaScript globales**: para todo el site o páginas concretas. El JavaScript global no debe bloquear la carga; usa los atributos del script (`async`, etc.) que admita tu versión.
- **Theme CSS** y tokens del **style book** en lugar de temas clásicos (ver `liferay-content-experience`).

### Integración del custom element con Liferay

- **Usuario y sesión**: el objeto global `Liferay` expone datos del contexto (`Liferay.ThemeDisplay`, idioma, usuario...). Encapsula su acceso en un servicio o adaptador propio; no lo esparzas por los componentes.
- **Llamadas a las APIs headless** desde el navegador del usuario autenticado: con la sesión del portal y el token CSRF `p_auth` (`Liferay.authToken`) como cabecera `x-csrf-token`, o con OAuth2 si la aplicación lo requiere.
- **Traducciones**: `Liferay.Language.get('clave')` para textos del portal; los propios del componente, en su sistema de i18n.
- **Estilos**: Clay y variables CSS del style book para heredar el aspecto del site.
- **Comunicación entre widgets**: eventos del navegador (`CustomEvent`) o `Liferay.on`/`Liferay.fire`, con nombres con prefijo del proyecto.
- **Rutas**: si la aplicación tiene rutas internas, usa `friendlyURLMapping` y no rompas la navegación del portal.
- **Varias instancias en la misma página**: solo si `instanceable: true` y el componente no usa identificadores globales fijos.

## Microservicios

- Una aplicación externa (Spring Boot, Node...) que recibe peticiones de Liferay (acciones de objeto o workflow, validaciones, notificaciones) o llama a sus APIs. Disponibles en todos los modelos de despliegue: en SaaS los aloja Liferay; en self-hosted y PaaS los despliegas tú y configuras su URL.
- Se autentica con **OAuth2**: una client extension `oAuthApplicationUserAgent` (acciones en nombre del usuario) o `oAuthApplicationHeadlessServer` (servidor a servidor), referenciada por su ERC.
- **Valida el JWT** de cada petición entrante (emisor, audiencia, firma). Los ejemplos oficiales de Spring Boot incluyen una librería de ayuda para ello; usa la versión que corresponda a tu Liferay.
- **Idempotencia**: Liferay puede reintentar una acción; el microservicio no debe duplicar efectos.
- **Timeouts y errores**: responde rápido; para trabajo largo, acepta y procesa en segundo plano.
- `.serviceAddress` y `.serviceScheme` en la definición OAuth2 indican dónde corre el microservicio en desarrollo local.

## Configuración y batch

- **Instance Settings** y **OAuth2** como client extension: configuración versionada que se aplica al desplegar.
- **Batch**: importa definiciones y datos exportados con el batch engine (objects, picklists, workflow, registros...). Necesita una `oAuthApplicationHeadlessServer` con los scopes adecuados (ver `liferay-objects-workflow`).
- **Site initializer**: crea un site completo (páginas, fragments, contenido, configuración) desde el repositorio (ver `liferay-content-experience`).

## Despliegue

```powershell
./gradlew :client-extensions:acme-orders-custom-element:deploy   # bundle local
./gradlew deploy -Ddeploy.docker.container.id=<id>               # contenedor
lcp deploy --extension <ruta-al-luffa>.zip                      # SaaS/PaaS (comprueba la sintaxis de tu CLI)
```

- Los LUFFA se despliegan en la carpeta `deploy` (self-hosted) o con la CLI `lcp` (PaaS/SaaS).
- Las client extensions configuradas en la interfaz pueden exportarse como JSON (desde 2024.Q1), pero para el ciclo de vida del proyecto, **defínelas en el repositorio**.

## Checklist

- [ ] Client extension elegida antes que un módulo OSGi
- [ ] Tipo y propiedades comprobados en la referencia de la versión
- [ ] Agrupación válida (sin frontend + microservicio en el mismo proyecto)
- [ ] Custom element: acceso al contexto de Liferay encapsulado, `p_auth` u OAuth2 en las llamadas, Clay y tokens
- [ ] Microservicio: OAuth2, JWT validado, idempotente, con timeouts
- [ ] Configuración y datos versionados con ERC estables
