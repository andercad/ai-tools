---
name: liferay-sites
description: 'Liferay DXP. Sites e instancias: diseño de sites, sites hijos y plantillas de site, site initializer como client extension, exportación e importación (LAR), staging local y remoto, Publications (control de cambios), instancias virtuales, idiomas y traducciones, URLs amigables, SEO (sitemap, robots, metadatos), navegación y menús. Usar cuando: crear un site o varios a partir de una base común, mover contenido entre entornos, preparar cambios antes de publicarlos, gestionar varias marcas o clientes en la misma instalación, configurar idiomas, mejorar el SEO.'
argument-hint: 'Describe los sites, quién los gestiona y cómo se mueven los cambios entre entornos.'
---

# Sites, entornos de publicación e instancias

## Organización

| Necesidad | Opción |
|---|---|
| Varias webs de la misma organización | Varios sites (o sites hijos) en la misma instancia |
| Sites con la misma base (páginas, fragments, configuración) | **Site initializer** (client extension) o plantillas de site |
| Clientes o marcas totalmente aislados (usuarios, configuración, dominios) | **Instancias virtuales** |
| Intranet con áreas por departamento | Site principal y sites hijos, o organizaciones con sites |

- Las instancias virtuales aíslan usuarios, roles, configuración y contenido; comparten la instalación y la base de datos. Cada instancia tiene su propio dominio.
- Identifica los sites por su **clave o nombre**, nunca por ID, en código, plantillas y configuración.

## Site initializer

- Crea un site completo desde el repositorio: páginas, master pages, fragments, style books, contenidos, documentos, objects, configuración...
- Es la forma recomendada de **crear sites reproducibles** en todos los entornos y en todos los modelos de despliegue.
- Ejemplos completos en el *sample workspace*; copia la estructura de carpetas de tu versión.

## Mover contenido entre entornos

| Mecanismo | Uso |
|---|---|
| **Configuración y estructura como código** (site initializer, batch, client extensions) | Lo que pertenece al proyecto: debe estar en el repositorio |
| **Exportación/importación (LAR)** | Copias puntuales de contenido entre instalaciones de la misma versión |
| **Staging remoto** | Un entorno de edición separado que publica en el de producción |
| **Staging local** | Una versión de trabajo del site dentro de la misma instalación |
| **Publications** | Agrupar cambios en una "publicación" que se revisa y publica de una vez |

- **Staging** y **Publications** son modelos distintos para preparar cambios: elige uno por instalación y comprueba en la documentación de tu versión si pueden convivir.
- **A/B testing no funciona con staging activado** (ver `liferay-personalization`).
- Las entidades propias (Service Builder) necesitan soporte de exportación/importación y staging para viajar con el site (`uuid`, manejadores de datos); los Objects lo integran.
- La exportación/importación es entre **la misma versión**; no es un mecanismo de migración de versión.

## Idiomas

- Idiomas disponibles en `locales.enabled` (instancia) y por site en Site Settings.
- Contenidos, páginas y fragments localizables; textos fijos con claves de idioma (ver `liferay-osgi` y `liferay-content`).
- URLs con prefijo de idioma y etiquetas `hreflang` gestionadas por el portal.

## URLs, navegación y SEO

- URLs amigables legibles y estables para páginas, contenidos (plantillas de visualización) y Objects.
- **Menús de navegación** gestionados en la interfaz, no codificados en temas.
- SEO: título y descripción por página, metadatos Open Graph, **sitemap** y **robots.txt** configurados por site, URLs canónicas.
- Redirecciones (gestor de redirecciones) al cambiar URLs; evita romper enlaces existentes.

## Checklist

- [ ] Estructura de sites, sites hijos o instancias elegida por el grado de aislamiento necesario
- [ ] Sites reproducibles con site initializer desde el repositorio
- [ ] Un único modelo para preparar cambios (staging o Publications); A/B testing compatible
- [ ] LAR solo entre instalaciones de la misma versión
- [ ] Idiomas configurados en instancia y site; textos fijos con claves
- [ ] URLs amigables, sitemap, robots y redirecciones al cambiar URLs
