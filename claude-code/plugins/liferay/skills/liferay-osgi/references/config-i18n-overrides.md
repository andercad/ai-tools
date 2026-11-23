# Traducciones, model listeners, configuración tipada, tareas, overrides, Gogo Shell

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
- Si el dato es un Object, usa **acciones de objeto** en lugar de un model listener (ver `liferay-objects-workflow`).

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

- Aparece en System/Instance Settings o en la configuración del widget según su `scope` (`SYSTEM`, `COMPANY`, `GROUP`, `PORTLET_INSTANCE`) y se puede desplegar como `.config` (ver `liferay-config-operations`).
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
- Revisa cada override en cada actualización trimestral (ver `liferay-workspace`).

## Gogo Shell

```
lb acme                    # bundles que contienen "acme" y su estado
diag <bundleId>            # dependencias no resueltas de un bundle
scr:info <componente>      # estado del componente y referencias no satisfechas
```

- Accesible desde Control Panel → Gogo Shell o con `blade sh <comando>`. En producción, restringe el acceso.
- Comprueba los comandos disponibles en tu versión con `help`.
