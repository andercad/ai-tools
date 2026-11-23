---
name: liferay-fragments
description: 'Liferay DXP. Fragments y construcción de páginas: fragments con HTML, CSS, JavaScript y configuración, elementos editables y mapeables, fragments de formulario para Objects, colecciones, páginas de contenido, plantillas de página y de visualización, master pages, style books y tokens de diseño, temas (theme CSS como client extension frente a temas clásicos) y accesibilidad. Usar cuando: crear o modificar un fragment, maquetar una página de contenido, definir una master page, cambiar colores y tipografías del site, crear un tema, mostrar un Object o un contenido en una página de visualización.'
argument-hint: 'Describe la pieza visual o la página que necesitas construir.'
---

# Fragments, páginas y diseño

## Qué usar

| Necesidad | Herramienta |
|---|---|
| Bloque visual reutilizable editable por usuarios de negocio | **Fragment** |
| Página compuesta por fragments y widgets | **Página de contenido** |
| Cabecera, pie y estructura común | **Master page** |
| Página tipo para crear páginas nuevas | **Plantilla de página** |
| Detalle de un contenido, documento u Object con URL amigable | **Plantilla de visualización** (*display page template*) |
| Colores, tipografías, espaciados | **Style book** (tokens) |
| Aspecto global del site | **Theme CSS** como client extension (o tema clásico existente) |
| Interfaz con lógica compleja | Custom element (ver `liferay-client-extensions`) |

## Fragments

Un fragment tiene HTML, CSS, JavaScript y, opcionalmente, configuración:

```html
<div class="acme-hero acme-hero--${configuration.variant}">
	<h1 class="acme-hero__title" data-lfr-editable-id="title" data-lfr-editable-type="text">
		Título por defecto
	</h1>
	<div class="acme-hero__text" data-lfr-editable-id="text" data-lfr-editable-type="rich-text">
		<p>Texto por defecto</p>
	</div>
	<a
		class="btn btn-primary"
		data-lfr-editable-id="cta"
		data-lfr-editable-type="link"
		href=""
	>
		Saber más
	</a>
</div>
```

```json
{
	"fieldSets": [
		{
			"fields": [
				{
					"dataType": "string",
					"defaultValue": "light",
					"label": "variant",
					"name": "variant",
					"type": "select",
					"typeOptions": {
						"validValues": [
							{ "value": "light" },
							{ "value": "dark" }
						]
					}
				}
			]
		}
	]
}
```

- **Elementos editables** (`data-lfr-editable-id` + tipo): texto, texto enriquecido, imagen, enlace, HTML. Los editables se pueden **mapear** a campos de contenidos, documentos u Objects.
- La **configuración** (`configuration.<campo>`) es para variantes de presentación, no para datos.
- **CSS con prefijo** del proyecto (`.acme-hero`); usa los **tokens del style book** (variables CSS) en lugar de colores fijos para que el fragment herede el diseño del site.
- **JavaScript**: el fragment puede estar varias veces en la página; usa el elemento raíz que recibe el script (`fragmentElement`) en lugar de selectores globales.
- **FreeMarker en fragments**: permitido para lógica de presentación sencilla; mismas reglas que las plantillas: escapar, helpers vía Template Context Contributor y sin variables restringidas (ver `liferay-content`).
- Fragments de **formulario** para crear o editar entradas de Objects desde páginas.
- **Accesibilidad**: encabezados en orden, `alt` en imágenes, foco visible, contraste suficiente.

### Desarrollo y despliegue

- Desarrolla los fragments como código en una colección (carpeta con `collection.json` y un directorio por fragment con `fragment.json`, `index.html`, `index.css`, `index.js` y `configuration.json`), en la carpeta de recursos del proyecto (ver guidelines).
- Despliégalos con un **site initializer** o importando el ZIP de la colección; comprueba la herramienta y el formato de tu versión.
- No edites en producción fragments que se gestionan desde el repositorio: se sobrescribirán.

## Páginas de contenido, master pages y plantillas

- **Master pages** para cabecera, pie y navegación comunes; las páginas solo definen su zona de contenido.
- **Plantillas de página** con la estructura base de cada tipo de página.
- **Plantillas de visualización** por tipo de contenido u Object, con URL amigable.
- Usa **contenedores**, **grids** y el sistema de columnas del editor en lugar de maquetar todo dentro de un único fragment.
- Las experiencias por segmento se definen sobre páginas de contenido (ver `liferay-personalization`).

## Style books y temas

- **Style book**: valores de los tokens (colores, tipografías, espaciados, bordes) que usan los fragments y Clay. Cambiar el aspecto de un site empieza por aquí.
- **Theme CSS** como client extension: el aspecto global sin desplegar un tema WAR; funciona en todos los modelos de despliegue. Puede definir tokens propios.
- **Temas clásicos** (WAR con FreeMarker, módulos `-theme`/`-themelet`): solo para mantener los existentes o necesidades que no cubren style books y theme CSS. No disponibles en SaaS.
- Favicon y sprite map también como client extensions.

## Checklist

- [ ] Herramienta adecuada (fragment, master page, plantilla, style book, client extension)
- [ ] Editables mapeables; configuración solo para variantes de presentación
- [ ] CSS con prefijo y tokens del style book; JavaScript limitado a `fragmentElement`
- [ ] FreeMarker con escapado y sin variables restringidas
- [ ] Fragments versionados y desplegados desde el repositorio
- [ ] Aspecto global con style book y theme CSS antes que tema clásico
- [ ] Accesibilidad revisada
