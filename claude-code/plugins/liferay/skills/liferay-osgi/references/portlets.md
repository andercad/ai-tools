# Portlets MVC, constantes, render, acciones, JSP, panel de control

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
