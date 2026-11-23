---
name: liferay-content-experience
description: 'Liferay DXP. Contenido y experiencia: estructuras y plantillas FreeMarker de contenido web, ADT, Template Context Contributors, Documents and Media, Adaptive Media, categorías; fragments, páginas de contenido, master pages, style books y temas; sites, site initializer, exportación e importación, staging, Publications, instancias, idiomas y SEO; segmentos, experiencias y A/B testing; Analytics Cloud. Usar al crear o modificar estructuras, plantillas, ADT, fragments, páginas, temas, sites, segmentos o al medir el uso con Analytics. No usar para lógica Java (liferay-osgi) ni para búsqueda (liferay-search).'
---

# Contenido, páginas, sites y personalización

## Reglas clave
- FreeMarker: escapa todo valor de usuario; servicios y helpers propios solo mediante Template Context Contributor; no habilites `serviceLocator` ni `staticUtil` sin excepción documentada.
- Valores que dependen del entorno (vocabularios, plantillas, sites, carpetas) por nombre o clave, nunca por ID.
- Prefiere temas como client extension (theme CSS) frente a temas clásicos.
- Estructuras, plantillas, ADT, fragments y site initializers se versionan en el repositorio y se despliegan como código.
- No actives funciones beta ni feature flags experimentales salvo petición expresa.

## Referencias
| Tema | Fichero |
|---|---|
| Estructuras, plantillas, ADT, Template Context Contributors, documentos | [content.md](references/content.md) |
| Fragments, páginas, master pages, style books, temas | [fragments.md](references/fragments.md) |
| Sites, site initializer, LAR, staging, idiomas, SEO | [sites.md](references/sites.md) |
| Segmentos, experiencias, A/B testing | [personalization.md](references/personalization.md) |
| Analytics Cloud | [analytics.md](references/analytics.md) |

## Checklists
### Estructuras
- [ ] Referencias de campo estables y significativas
- [ ] Plantilla de resumen y de detalle para estructuras con listado
- [ ] Plantillas organizadas en Variables, Template, Macros y Functions
- [ ] Todo texto de usuario escapado (`htmlUtil.escape`)
- [ ] Servicios y helpers vía Template Context Contributor; sin `serviceLocator` salvo excepción documentada
- [ ] Valores del entorno por nombre o clave, nunca por ID
- [ ] ADT que embeben la plantilla de resumen por su clave obtenida por nombre
- [ ] Campos de estructura desde Java con la API de Liferay, no con `SAXReader`
- [ ] Documentos con permisos y metadatos; previsualizaciones configuradas
- [ ] Estructuras, plantillas y ADT versionados en la carpeta de recursos del proyecto

### Fragments
- [ ] Herramienta adecuada (fragment, master page, plantilla, style book, client extension)
- [ ] Editables mapeables; configuración solo para variantes de presentación
- [ ] CSS con prefijo y tokens del style book; JavaScript limitado a `fragmentElement`
- [ ] FreeMarker con escapado y sin variables restringidas
- [ ] Fragments versionados y desplegados desde el repositorio
- [ ] Aspecto global con style book y theme CSS antes que tema clásico
- [ ] Accesibilidad revisada

### Sites
- [ ] Estructura de sites, sites hijos o instancias elegida por el grado de aislamiento necesario
- [ ] Sites reproducibles con site initializer desde el repositorio
- [ ] Un único modelo para preparar cambios (staging o Publications); A/B testing compatible
- [ ] LAR solo entre instalaciones de la misma versión
- [ ] Idiomas configurados en instancia y site; textos fijos con claves
- [ ] URLs amigables, sitemap, robots y redirecciones al cambiar URLs

### Segmentos
- [ ] Segmentos pocos y con significado de negocio; criterios disponibles en la versión comprobados
- [ ] Roles asignados a segmentos revisados como permisos
- [ ] Experiencia por defecto completa; prioridades definidas; revisado con simulación
- [ ] Colecciones personalizadas con variación por defecto coherente
- [ ] A/B testing solo con Analytics Cloud y sin staging; objetivo y duración definidos
- [ ] Sin funcionalidades beta salvo petición; consentimiento y normativa respetados

### Analytics Cloud
- [ ] Token y propiedad configurados; sites y canales asignados
- [ ] Un token por entorno; no productivos desconectados tras copiar bases de datos
- [ ] Salida de red y CSP permiten los dominios de Analytics Cloud
- [ ] Catálogo de eventos personalizados con nombres estables y sin datos personales
- [ ] Datos verificados en el navegador y en los logs
- [ ] Consentimiento y base legal documentados
