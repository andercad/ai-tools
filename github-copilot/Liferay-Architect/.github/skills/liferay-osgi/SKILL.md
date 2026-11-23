---
name: liferay-osgi
description: 'Liferay DXP. Módulos OSGi: componentes Declarative Services (@Component, @Reference), módulos API e implementación, portlets MVC con clase de constantes, render por defecto y comandos MVC, preferencias con comprobación de configuración obligatoria, JSP con JSTL sin scriptlets, portletNamespace y ParamUtil, aplicaciones del panel de control (isShow), helpers como componentes, Lombok y Jackson, model listeners, configuración tipada (ConfigurationProvider), bnd.bnd, traducciones en Language.properties, tareas programadas, Gogo Shell y overrides del núcleo. Usar cuando: crear un módulo, un API, un portlet o un servicio OSGi, definir constantes o preferencias de un portlet, escribir JSP, crear una utilidad, serializar JSON, reaccionar a cambios de entidades, resolver referencias que no se satisfacen, sobrescribir un comportamiento de Liferay.'
argument-hint: 'Describe el componente, portlet o comportamiento que necesitas implementar.'
---

# Módulos OSGi

**No disponibles en Liferay SaaS.** Antes de crear un módulo, comprueba que el requisito no se resuelve con configuración, Objects, contenido o client extensions (orden de *Cómo extender Liferay* en el agente). Nomenclatura de módulos, paquetes y clases: ver el agente y `guidelines/coding-guidelines.md`.

## API e implementación

```
modules/apis/send-emails/
  send-emails-api/      ← interfaces y modelos (paquete exportado)
  send-emails-impl/     ← implementación (no exporta paquetes)
```

```properties
# send-emails-api/bnd.bnd
Bundle-Name: Acme Send Emails API
Bundle-SymbolicName: com.acme.send.emails.api
Bundle-Version: 1.0.0
Export-Package: com.acme.send.emails.api
```

```java
// send-emails-api: com.acme.send.emails.api
public interface SendEmailsApi {

	void send(String templateName, String to, Map<String, Object> variables) throws PortalException;

}
```

```java
// send-emails-impl: com.acme.send.emails.impl
@Component(service = SendEmailsApi.class)
public class SendEmailsApiImpl implements SendEmailsApi {

	@Override
	public void send(String templateName, String to, Map<String, Object> variables) throws PortalException {
		if (_log.isDebugEnabled()) {
			_log.debug("Sending email with template " + templateName);
		}

		_mailService.sendEmail(_sendEmailsHelper.buildMessage(templateName, to, variables));
	}

	private static final Log _log = LogFactoryUtil.getLog(SendEmailsApiImpl.class);

	@Reference
	private MailService _mailService;

	@Reference
	private SendEmailsHelper _sendEmailsHelper;

}
```

- **Exporta solo el paquete del API.** La implementación no exporta nada; los consumidores dependen del API (`compileOnly project(...)`, ver `liferay-workspace`).
- **Versionado semántico** de los paquetes exportados (`packageinfo` o `@Version`): cambios incompatibles suben la versión mayor. El *baseline* de bnd lo comprueba (ver `liferay-quality`).

## Componentes y helpers

- Dependencias con **`@Reference`**: `*LocalService`, `Portal`, `Language`, `ConfigurationProvider`... Nunca sus equivalentes `*Util` estáticos ni `new`: afectan al proceso de arranque y algunos han desaparecido en versiones recientes.
- Convención de Liferay: campos privados con prefijo `_`, referencias al final de la clase.
- **Utilidades propias como componentes OSGi**, con interfaz `[Funcionalidad]Helper` e implementación `[Funcionalidad]HelperImpl`, inyectadas con `@Reference`. Sin métodos estáticos.

```java
public interface OrdersHelper {

	boolean isEnabledForSite(long groupId);

}
```

```java
@Component(service = OrdersHelper.class)
public class OrdersHelperImpl implements OrdersHelper {

	@Override
	public boolean isEnabledForSite(long groupId) {
		Group group = _groupLocalService.fetchGroup(groupId);

		return (group != null) && _ACME_SITE_KEYS.contains(group.getGroupKey());
	}

	private static final Set<String> _ACME_SITE_KEYS = Set.of("Inmo", "Inmo Admin");

	@Reference
	private GroupLocalService _groupLocalService;

}
```

(Los sites se identifican por clave o nombre, nunca por ID: los IDs cambian entre entornos. En un caso real, la lista vendría de la configuración del módulo.)

- Referencias **dinámicas u opcionales** (`policy = ReferencePolicy.DYNAMIC`, `cardinality = OPTIONAL` o `MULTIPLE`) solo si el servicio puede no existir o haber varios; el campo debe ser `volatile` en referencias dinámicas.
- Para filtrar entre varias implementaciones, `target = "(propiedad=valor)"`.
- Un componente cuyo `@Reference` obligatorio no se satisface **no se activa**: diagnóstico con Gogo Shell (ver abajo).

## Lombok

```groovy
dependencies {
	compileOnly group: "org.projectlombok", name: "lombok", version: "<versión>"
	annotationProcessor group: "org.projectlombok", name: "lombok", version: "<versión>"
}
```

- `compileOnly` + `annotationProcessor`: Lombok genera el código al compilar y no se despliega con el módulo. Usa la versión fijada en las guidelines, compatible con el JDK del proyecto.
- Modelos: `@Getter`/`@Setter`, `@Data`, `@NoArgsConstructor`, `@AllArgsConstructor`, `@Builder` según el caso.
- Clases de constantes: **`@UtilityClass`**, que hace la clase `final`, genera el constructor privado (evita instancias y el aviso de SonarQube) y convierte todos sus miembros en `static`. Pertenece al paquete `lombok.experimental`: revísalo al actualizar Lombok.
- La convención `_` de Liferay en campos privados choca con los getters generados (`get_reference`): en clases con Lombok, nombra los campos sin `_` o configura `lombok.accessors.prefix` en `lombok.config`, según las guidelines.

```java
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderModel {

	private String reference;
	private String status;
	private Date createDate;

}
```

## Jackson

- Usa la versión de Jackson que **proporciona la instalación de Liferay**: compruébala en Gogo Shell (`lb jackson`) y decláralo como `compileOnly` con esa versión. **No incluyas otra copia** en el módulo: dos versiones cargadas a la vez provocan errores con las anotaciones entre módulos.
- Liferay distribuye su propia versión parcheada de `jackson-databind`; confirma el paquete exportado (`com.fasterxml.jackson.databind`) en tu versión. Jackson 3 cambia el paquete a `tools.jackson`: no mezcles ambos.
- Reutiliza un `ObjectMapper` configurado (campo del componente o un helper), no crees uno por petición.

```java
@Component(service = OrderJsonHelper.class)
public class OrderJsonHelperImpl implements OrderJsonHelper {

	@Override
	public String toJson(OrderModel orderModel) throws JsonProcessingException {
		return _objectMapper.writeValueAsString(orderModel);
	}

	@Override
	public OrderModel fromJson(String json) throws JsonProcessingException {
		return _objectMapper.readValue(json, OrderModel.class);
	}

	private final ObjectMapper _objectMapper = new ObjectMapper().configure(
		DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

}
```

## Portlets MVC

Antes de crear un portlet, valora un **custom element** (client extension) o un fragment: funcionan en todos los modelos de despliegue y se desacoplan de las actualizaciones. Cuando el portlet está justificado:

### Constantes

Una clase `[Portlet]PortletKeys` en `.web.constants` con las constantes y bloques de constantes que necesite el portlet:

| Constante o bloque | Contenido |
|---|---|
| `PORTLET_NAME` | Nombre del portlet, usado en todos los componentes OSGi del portlet |
| `CATEGORY` | Categoría donde se muestra el portlet |
| `CONFIGURATION_ID` | Identificador de la configuración, si la tiene |
| `PORTLET_PREFERENCES_FORM` | Nombres de los campos del formulario de configuración (atributo `name`) |
| `PORTLET_PREFERENCE_SUFFIX` | `"Pref"`, sufijo de las preferencias |
| `PORTLET_PREFERENCES` | Nombres de las preferencias, iguales a los de la interfaz de configuración |
| `RENDER_METHODS`, `ACTION_METHODS`, `RESOURCE_METHODS` | Nombres de los comandos MVC |
| `RENDER_PARAMETERS` | Parámetros enviados entre comandos MVC |
| `FORM_FIELDS` | Campos de formularios (en el JSP y al leerlos en Java) |
| `MESSAGES_SUCCESS`, `MESSAGES_ERROR` | Claves de los mensajes |
| `EMAIL_SUBJECT`, `EMAIL_BODY_URL` | Clave del asunto y ruta de la plantilla de email (`META-INF/resources/tmpl/...`) |

Solo los bloques que el portlet necesite.

```java
@UtilityClass
public class OrdersPortletKeys {

	public static final String PORTLET_NAME = "com_acme_orders_web_OrdersPortlet";

	public static final String CATEGORY = "category.acme";

	public static final String CONFIGURATION_ID = "com.acme.orders.web.configuration.OrdersPortletConfiguration";

	public static final String PORTLET_PREFERENCE_SUFFIX = "Pref";

	@UtilityClass
	public static class PORTLET_PREFERENCES {

		public static final String FOLDER_NAME = "folderNamePref";

	}

	@UtilityClass
	public static class RENDER_METHODS {

		public static final String DETAIL = "/acme/orders/detail";

	}

	@UtilityClass
	public static class ACTION_METHODS {

		public static final String CANCEL = "/acme/orders/cancel";

	}

	@UtilityClass
	public static class FORM_FIELDS {

		public static final String ORDER_ID = "orderId";

	}

}
```

(Comprueba que tu versión de Lombok admite `@UtilityClass` en clases anidadas estáticas; si no, usa un constructor privado en esas clases.)

### Clase del portlet

```java
@Component(
	property = {
		"com.liferay.portlet.display-category=" + OrdersPortletKeys.CATEGORY,
		"jakarta.portlet.display-name=Orders",
		"jakarta.portlet.name=" + OrdersPortletKeys.PORTLET_NAME,
		"jakarta.portlet.resource-bundle=content.Language",
		"jakarta.portlet.security-role-ref=power-user,user"
	},
	service = Portlet.class
)
public class OrdersPortlet extends MVCPortlet {
}
```

- **El prefijo de las propiedades (`jakarta.portlet.*` o `javax.portlet.*`) y los imports dependen de la versión**: usa el espacio de nombres detectado en `liferay-workspace`. El ejemplo usa `jakarta`; si tu versión usa `javax`, cámbialo en todo el módulo.
- La clase del portlet **solo contiene su definición**: todas las vistas están en `MVCRenderCommand`, así se pueden reutilizar.
- Si hay varios renders por defecto posibles, se elige mediante configuración desde la clase del portlet.

### Render por defecto y configuración obligatoria

```java
@Component(
	property = {
		"jakarta.portlet.name=" + OrdersPortletKeys.PORTLET_NAME,
		"mvc.command.name=/"
	},
	service = MVCRenderCommand.class
)
public class OrdersDefaultMVCRenderCommand implements MVCRenderCommand {

	@Override
	public String render(RenderRequest renderRequest, RenderResponse renderResponse) throws PortletException {
		OrdersPortletConfiguration ordersPortletConfiguration = _getConfiguration(renderRequest);

		if (Validator.isNull(ordersPortletConfiguration.folderNamePref())) {
			return "/configuration_required.jsp";
		}

		renderRequest.setAttribute(
			OrdersDisplayContext.class.getName(),
			new OrdersDisplayContext(ordersPortletConfiguration, renderRequest, _ordersHelper));

		return "/view.jsp";
	}

	private OrdersPortletConfiguration _getConfiguration(RenderRequest renderRequest) throws PortletException {
		ThemeDisplay themeDisplay = (ThemeDisplay)renderRequest.getAttribute(WebKeys.THEME_DISPLAY);

		try {
			return _configurationProvider.getPortletInstanceConfiguration(
				OrdersPortletConfiguration.class, themeDisplay.getLayout(),
				themeDisplay.getPortletDisplay().getId());
		}
		catch (ConfigurationException configurationException) {
			throw new PortletException(configurationException);
		}
	}

	@Reference
	private ConfigurationProvider _configurationProvider;

	@Reference
	private OrdersHelper _ordersHelper;

}
```

- **Comprueba siempre en el render que las preferencias obligatorias están rellenas.** Si no, no ejecutes la lógica del portlet y muestra un mensaje informativo (`configuration_required.jsp`) para que no se olvide configurarlo.
- Preferencias con el sufijo `Pref`; los nombres de los campos del formulario y de las preferencias salen de las constantes.
- La firma de los métodos de `ConfigurationProvider` cambia entre versiones: compruébala en la tuya.
- El resto de vistas: un `[Funcionalidad]MVCRenderCommand` cada una, con el nombre de `RENDER_METHODS`. La lógica de presentación va en un `[Funcionalidad]DisplayContext`.

### Acciones

```java
@Component(
	property = {
		"jakarta.portlet.name=" + OrdersPortletKeys.PORTLET_NAME,
		"mvc.command.name=" + OrdersPortletKeys.ACTION_METHODS.CANCEL
	},
	service = MVCActionCommand.class
)
public class CancelOrderMVCActionCommand extends BaseMVCActionCommand {

	@Override
	protected void doProcessAction(ActionRequest actionRequest, ActionResponse actionResponse) throws Exception {
		long orderId = ParamUtil.getLong(actionRequest, OrdersPortletKeys.FORM_FIELDS.ORDER_ID);

		// El servicio remoto comprueba permisos (ver liferay-security)
		_orderService.cancelOrder(orderId);
	}

	@Reference
	private OrderService _orderService;

}
```

- Parámetros con **`ParamUtil`**: tipados, con valor por defecto y gestionando el `portletNamespace` sin añadirlo a mano.
- Las acciones están protegidas con el token `p_auth`; no lo desactives.
- Nunca confíes en valores enviados por el cliente para decidir permisos (ver `liferay-security`).

### JSP

```
src/main/resources/
  META-INF/resources/
    init.jsp                 ← taglibs y variables comunes (JSTL)
    configuration.jsp        ← variables de las preferencias
    view.jsp
    configuration_required.jsp
    css/  js/  tmpl/         ← estilos, scripts y plantillas de email
  META-INF/friendly-url-routes/
  content/Language.properties
```

```jsp
<%-- init.jsp: taglibs, imports y constantes como variables JSTL (único sitio con expresiones Java) --%>
<%@ page import="com.acme.orders.web.constants.OrdersPortletKeys" %>

<c:set var="CANCEL_ACTION" value="<%= OrdersPortletKeys.ACTION_METHODS.CANCEL %>" />
<c:set var="ORDER_ID_FIELD" value="<%= OrdersPortletKeys.FORM_FIELDS.ORDER_ID %>" />
```

```jsp
<%-- view.jsp: solo JSTL y etiquetas, sin scriptlets --%>
<%@ include file="/init.jsp" %>

<c:set var="ordersDisplayContext" value="${requestScope['com.acme.orders.web.display.context.OrdersDisplayContext']}" />

<portlet:actionURL name="${CANCEL_ACTION}" var="cancelOrderURL" />

<aui:form action="${cancelOrderURL}" name="fm">
	<aui:input name="${ORDER_ID_FIELD}" type="hidden" value="${ordersDisplayContext.orderId}" />

	<button class="btn btn-secondary" id="<portlet:namespace />cancelButton" type="submit">
		<liferay-ui:message key="cancel-order" />
	</button>
</aui:form>
```

- **Scriptlets solo para pasar constantes a JSTL**:
  - En `init.jsp` (constantes generales) y `configuration.jsp` (constantes de preferencias) se permiten **únicamente** expresiones `<%= ... %>` dentro de un `<c:set>` para asignar una constante Java a una variable JSTL.
  - Ningún bloque `<% ... %>` ni declaración `<%! ... %>`, en ningún fichero, tampoco en `init.jsp` y `configuration.jsp`: nada de lógica Java en JSP.
  - El resto de JSP solo usa JSTL (`${...}`) y etiquetas.
  - Las directivas (`<%@ page import %>`, `<%@ include %>`, `<%@ taglib %>`) y los comentarios `<%-- --%>` no son scriptlets y se permiten.
- El resto de `init.jsp` (taglibs, `liferay-theme:defineObjects`, `portlet:defineObjects`) es el que genera Blade para tu versión; añade ahí las constantes.
- **`portletNamespace` siempre** en ids, campos de formulario y funciones JavaScript, aunque el portlet no sea instanciable. Las etiquetas `aui`/`liferay-ui` lo aplican solas; en HTML propio, `<portlet:namespace />`.
- Fragmentos de JSP reutilizables en ficheros `.jspf`.
- Salida escapada (ver `liferay-security`).

### Panel de control

```java
@Component(
	property = {
		"panel.app.order:Integer=300",
		"panel.category.key=" + PanelCategoryKeys.SITE_ADMINISTRATION_CONTENT
	},
	service = PanelApp.class
)
public class OrdersPanelApp extends BasePanelApp {

	@Override
	public Portlet getPortlet() {
		return _portlet;
	}

	@Override
	public String getPortletId() {
		return OrdersPortletKeys.PORTLET_NAME;
	}

	@Override
	public boolean isShow(PermissionChecker permissionChecker, Group group) throws PortalException {
		return _ordersHelper.isEnabledForSite(group.getGroupId()) && super.isShow(permissionChecker, group);
	}

	@Reference(target = "(jakarta.portlet.name=" + OrdersPortletKeys.PORTLET_NAME + ")")
	private Portlet _portlet;

	@Reference
	private OrdersHelper _ordersHelper;

}
```

- Sobrescribe **`isShow`** para que la aplicación aparezca única y exclusivamente en los sites a los que pertenece.

## Traducciones

| Caso | Ficheros |
|---|---|
| **Portlet o módulo propio** | `content/Language.properties` con los textos en el **idioma por defecto del proyecto** (siempre existe) y un `Language_<locale>.properties` por cada idioma adicional del proyecto. No crees inglés si el proyecto no lo usa |
| **Resource bundle** que sobrescribe textos del portal o de otros módulos (usados en temas, plantillas y ADT) | Solo los `Language_<locale>.properties` de los idiomas del proyecto. No crees `Language.properties`: contiene los textos por defecto del portal, en inglés, y sobrescribirlo puede romper textos existentes |

- Claves en kebab-case.
- En Java, `_language.get(locale, "clave")` con `Language` inyectado; en JSP, `<liferay-ui:message key="clave" />`.
- Los literales también pueden gestionarse desde el panel de control, pero lo que deba ser igual en todos los entornos va en el repositorio.

## Model listeners

```java
@Component(service = ModelListener.class)
public class JournalArticleModelListener extends BaseModelListener<JournalArticle> {

	@Override
	public void onAfterCreate(JournalArticle journalArticle) throws ModelListenerException {
		try {
			_auditPublisher.publishCreated(journalArticle.getArticleId());
		}
		catch (Exception exception) {
			throw new ModelListenerException(exception);
		}
	}

	@Reference
	private AuditPublisher _auditPublisher;

}
```

- Se ejecutan **dentro de la transacción**: nada de llamadas lentas o remotas aquí; para efectos externos, publica un mensaje y procésalo de forma asíncrona.
- Si el dato es un Object, usa **acciones de objeto** en lugar de un model listener (ver `liferay-objects`).

## Configuración tipada

```java
@ExtendedObjectClassDefinition(
	category = "acme", scope = ExtendedObjectClassDefinition.Scope.PORTLET_INSTANCE
)
@Meta.OCD(
	id = "com.acme.orders.web.configuration.OrdersPortletConfiguration",
	localization = "content/Language", name = "orders-configuration-name"
)
public interface OrdersPortletConfiguration {

	@Meta.AD(deflt = "", name = "folder-name", required = false)
	public String folderNamePref();

}
```

- Aparece en System/Instance Settings o en la configuración del widget según su `scope` (`SYSTEM`, `COMPANY`, `GROUP`, `PORTLET_INSTANCE`) y se puede desplegar como `.config` (ver `liferay-configuration`).
- Léela con **`ConfigurationProvider`** inyectado y el método del ámbito correspondiente.
- No uses propiedades propias de `portal-ext.properties` para configurar módulos.

## Tareas programadas

- `[Funcionalidad]DispatchTaskExecutor`: tareas que se programan y supervisan desde la interfaz (Job Scheduler). Comprueba la API de tu versión. En clúster, la plataforma coordina la ejecución; no programes hilos propios.

## Overrides del núcleo (último recurso)

| Necesidad | Mecanismo |
|---|---|
| Cambiar el comportamiento de un servicio de Liferay | `ServiceWrapper` |
| Cambiar una acción de un portlet de Liferay | Override de MVC command (mayor `service.ranking`) |
| Cambiar una JSP | Módulo `-override`, o *dynamic include* si existe un punto de extensión |
| Cambiar textos del portal | Módulo `-resource-bundle` |

- Antes, busca un punto de extensión oficial (dynamic includes, extensiones de formulario, client extensions).
- Documenta por qué, qué versión se sobrescribe y añade un test que falle si el original cambia.
- Revisa cada override en cada actualización trimestral (ver `liferay-upgrades`).

## Gogo Shell

```
lb acme                    # bundles que contienen "acme" y su estado
diag <bundleId>            # dependencias no resueltas de un bundle
scr:info <componente>      # estado del componente y referencias no satisfechas
```

- Accesible desde Control Panel → Gogo Shell o con `blade sh <comando>`. En producción, restringe el acceso.
- Comprueba los comandos disponibles en tu versión con `help`.

## Checklist

- [ ] Módulo justificado frente a configuración, Objects, contenido o client extensions
- [ ] API e implementación separados; solo el API exportado, con versionado semántico
- [ ] `@Reference` en lugar de clases `*Util` estáticas; utilidades como `Helper`/`HelperImpl`
- [ ] Espacio de nombres `jakarta`/`javax` de la versión
- [ ] Portlet: constantes en `PortletKeys`, vistas en `MVCRenderCommand`, render por defecto, configuración obligatoria comprobada
- [ ] JSP sin scriptlets, con `portletNamespace`; parámetros con `ParamUtil`
- [ ] Panel de control con `isShow`
- [ ] Lombok como `compileOnly` + `annotationProcessor`; Jackson de la instalación, sin copia propia
- [ ] Valores del entorno por nombre o clave, nunca por ID
- [ ] Traducciones según sea portlet propio o resource bundle
- [ ] Permisos comprobados (servicios remotos o `ModelResourcePermission`)
- [ ] Overrides del núcleo justificados, documentados y con test
