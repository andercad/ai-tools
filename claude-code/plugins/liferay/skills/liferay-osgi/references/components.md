# Módulos OSGi

**No disponibles en Liferay SaaS.** Antes de crear un módulo, comprueba que el requisito no se resuelve con configuración, Objects, contenido o client extensions (skill `liferay-extension-model`). Nomenclatura de módulos, paquetes y clases: ver `liferay-project-guidelines` y el bloque `## Convenciones Liferay` del `CLAUDE.md` del proyecto.

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
- **Versionado semántico** de los paquetes exportados (`packageinfo` o `@Version`): cambios incompatibles suben la versión mayor. El *baseline* de bnd lo comprueba (ver `liferay-testing-quality`).

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

	private static final Set<String> _ACME_SITE_KEYS = Set.of("Acme", "Acme Admin");

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
