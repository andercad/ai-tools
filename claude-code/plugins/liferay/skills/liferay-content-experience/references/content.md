# Contenidos, plantillas y documentos

## Estructuras de contenido web

- Definen los campos que rellena el editor: texto, texto enriquecido, imagen, documento, fecha, enlace a página o a otro contenido, selección, campos repetibles y fieldsets.
- Cada campo tiene una **referencia de campo** (*field reference*) estable: es el nombre que usan las plantillas y la API. Dale un nombre significativo antes de crear contenido y no lo cambies después.
- Campos **localizables** solo cuando el valor cambia por idioma.
- Para contenido estructurado que necesita API, permisos o relaciones complejas, valora **Objects** (ver `liferay-objects-workflow`).
- Versiona estructuras, plantillas y ADT en la carpeta de recursos del proyecto (ver guidelines) y despliégalos con exportación/importación o site initializer (ver `liferay-content-experience`), no los recrees a mano.

## Plantillas de contenido web

Para estructuras con listado y detalle, crea **como mínimo dos plantillas**:

- **Resumen**: la que se embebe en listados (ADT) y en portlets que muestran contenidos.
- **Detalle**: con toda la información o con lo que se defina.

### Organización

Cada plantilla se ordena en bloques, en este orden:

| Bloque | Contenido |
|---|---|
| **Variables** | Variables generales de la plantilla (valores de campos, helpers expuestos, cálculos) |
| **Template** | HTML y JavaScript |
| **Macros** | Macros de la plantilla |
| **Functions** | Funciones de la plantilla |

Las variables de bucles se definen donde se necesitan, pero intenta mantenerlas en el bloque de variables. En FreeMarker, macros y funciones están disponibles en toda la plantilla aunque se definan al final.

```ftl
<#-- ===== Variables ===== -->
<#assign title = Title.getData() />
<#assign summary = Summary.getData() />
<#assign hasImage = Image.getData()?has_content />

<#-- ===== Template ===== -->
<article class="acme-news">
	<h2 class="acme-news__title">${htmlUtil.escape(title)}</h2>

	<#if summary?has_content>
		<p class="acme-news__summary">${htmlUtil.escape(summary)}</p>
	</#if>

	<#if hasImage>
		<@newsImage image=Image />
	</#if>
</article>

<#-- ===== Macros ===== -->
<#macro newsImage image>
	<img
		alt="${htmlUtil.escape(image.getAttribute("alt"))}"
		class="acme-news__image"
		src="${image.getData()}"
	/>
</#macro>

<#-- ===== Functions ===== -->
<#function formatDate value>
	<#return dateUtil.getDate(value?date("yyyy-MM-dd"), "dd/MM/yyyy", locale) />
</#function>
```

- Accede a cada campo por su referencia (`Title.getData()`); en campos repetibles, recorre `Campo.getSiblings()`.
- **Escapa** con `htmlUtil.escape(...)` todo texto que se inserte en HTML, y `htmlUtil.escapeAttribute(...)` en atributos. Un campo de texto enriquecido ya contiene HTML: muéstralo sin escapar solo si su origen es de confianza (editores con permiso).
- Comprueba con `?has_content` antes de usar valores opcionales; un error de plantilla rompe la página.
- Accesibilidad: `alt` en imágenes, encabezados en orden, sin información solo por color.
- Las variables y utilidades disponibles (`dateUtil`, `htmlUtil`, `locale`...) dependen de la versión: consulta el panel de variables del editor de plantillas.

## Servicios y helpers en plantillas: Template Context Contributor

**No uses `serviceLocator`, `staticUtil` ni `objectUtil`.** Están restringidas por defecto porque dan acceso a cualquier servicio del portal desde una plantilla editable. Para usar un servicio o un helper propio, exponlo con un **Template Context Contributor** (módulo OSGi; **no disponible en SaaS**):

```java
@Component(
	property = "type=" + TemplateContextContributor.TYPE_GLOBAL,
	service = TemplateContextContributor.class
)
public class AcmeTemplateContextContributor implements TemplateContextContributor {

	@Override
	public void prepare(Map<String, Object> contextObjects, HttpServletRequest httpServletRequest) {
		contextObjects.put("acmeTemplateHelper", _acmeTemplateHelper);
	}

	@Reference
	private AcmeTemplateHelper _acmeTemplateHelper;

}
```

```ftl
<#assign vocabularyId = acmeTemplateHelper.getVocabularyId(themeDisplay.getScopeGroupId(), "Tipologías") />
```

- Expón **helpers con métodos concretos** (por ejemplo, obtener un ID a partir de un nombre), no servicios completos de Liferay.
- `TYPE_GLOBAL` lo hace disponible en temas, ADT y fragments; `TYPE_THEME`, solo en temas. **Comprueba en tu versión** que la variable llega también a las plantillas de contenido web.
- Si en algún tipo de plantilla no hay alternativa, el uso de `serviceLocator` debe ser una **excepción documentada en las guidelines**, limitada a esa plantilla.
- `HttpServletRequest` es del espacio de nombres (`jakarta`/`javax`) de tu versión.

## Valores dependientes del entorno: por nombre, nunca por ID

Los IDs (de vocabularios, categorías, plantillas, carpetas, sites) cambian entre entornos; los nombres y claves no. Obtén siempre el ID a partir del nombre o la clave:

- Desde plantillas: un helper expuesto por Template Context Contributor (`acmeTemplateHelper.getVocabularyId(groupId, "Tipologías")`).
- Desde Java: el mismo helper o el servicio correspondiente, buscando por nombre o clave.
- Si el valor debe ser configurable, guarda el **nombre o la clave** en la configuración, no el ID.

## Plantillas de visualización de widgets (ADT)

En listados de contenidos de una estructura, el ADT **no procesa los campos de la estructura**: embebe la **plantilla de resumen**, indicando su clave (`ddmTemplateKey`) obtenida **por el nombre de la plantilla**, para que funcione en todos los entornos.

```ftl
<#-- ===== Variables ===== -->
<#assign summaryTemplateKey = acmeTemplateHelper.getTemplateKey(themeDisplay.getScopeGroupId(), "Noticia - Resumen") />

<#-- ===== Template ===== -->
<#if entries?has_content>
	<ul class="acme-news-list">
		<#list entries as entry>
			<#assign article = entry.getAssetRenderer().getArticle() />
			<li class="acme-news-list__item">
				<@liferay_journal["journal-article"]
					articleId=article.getArticleId()
					ddmTemplateKey=summaryTemplateKey
					groupId=article.getGroupId()
				/>
			</li>
		</#list>
	</ul>
</#if>
```

- Así la presentación del resumen está en un solo sitio: cambiarla no obliga a tocar cada ADT.
- Comprueba en tu versión el nombre de la taglib (`liferay_journal["journal-article"]`) y que el asset renderer expone `getArticle()`.
- Las variables disponibles dependen del widget (Asset Publisher, Navigation Menu, Categories Navigation...): consulta el panel de variables del editor.
- En páginas de contenido, valora **fragments con colecciones** frente a Asset Publisher + ADT (ver `liferay-content-experience`).

## Campos de estructura desde Java

- Para leer o asignar por programa los valores de un contenido estructurado, usa la API de Liferay pensada para ello (`JournalConverter` y la API de valores de formulario de DDM de tu versión), **no** parsees el XML con `SAXReader`: es más frágil y menos legible.
- Comprueba las clases y métodos en el código de `liferay-portal` de tu versión: esta API ha cambiado entre versiones.
- Para crear o actualizar contenidos desde fuera, la API headless de contenido estructurado (ver `liferay-headless`).

## Documents and Media

- **Tipos de documento** con **conjuntos de metadatos** para documentos con campos propios.
- Carpetas con permisos por rol; no confíes en carpetas "ocultas" para proteger documentos.
- **Previsualizaciones y conversión**: dependen de herramientas externas (LibreOffice/OpenOffice para ofimática, Ghostscript o PDFBox según versión y configuración, ImageMagick). Problemas de conversión: ver `liferay-config-operations`.
- Tamaño máximo de subida y extensiones permitidas configurados en System Settings; ajústalos al caso de uso.
- El **almacén** (S3, file system...) se configura en el despliegue (ver `liferay-config-operations`).

## Adaptive Media

- Genera versiones de las imágenes en distintas resoluciones y las sirve según el ancho de la pantalla.
- Define las resoluciones según el diseño (no decenas de variantes) y regenera las imágenes existentes tras cambiar la configuración.
- En plantillas y fragments, usa las etiquetas o URLs de Adaptive Media de tu versión en lugar de la imagen original.

## Categorías y etiquetas

- **Vocabularios y categorías** para clasificaciones controladas; **etiquetas** para palabras clave libres.
- Vocabularios globales para clasificaciones comunes a todos los sites; de site para las propias.
- Las colecciones, la búsqueda, la segmentación y la navegación se apoyan en categorías: diséñalas antes de cargar contenido.

## Colecciones

- **Manuales** o **dinámicas** (por tipo, estructura, categoría, etiqueta...).
- Se muestran con el fragment *Collection Display* o con páginas de colección, y se pueden **personalizar por segmento** (ver `liferay-content-experience`).

## Traducción

- Contenidos localizables por idioma del site; flujo de traducción con exportación/importación XLIFF o traducción automática si está configurada.
- Textos fijos de plantillas y ADT mediante claves de idioma (`languageUtil.get(locale, "clave")`), definidas en un módulo resource bundle (ver `liferay-osgi`).
