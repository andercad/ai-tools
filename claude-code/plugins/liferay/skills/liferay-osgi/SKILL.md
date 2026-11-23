---
name: liferay-osgi
description: 'Liferay DXP. Módulos OSGi y Service Builder: componentes Declarative Services (@Component, @Reference), módulos API e implementación, portlets MVC (constantes, render por defecto, comandos MVC, preferencias, JSP con JSTL sin scriptlets, panel de control), helpers como componentes, Lombok, Jackson, model listeners, configuración tipada, traducciones, tareas programadas, overrides del núcleo, Gogo Shell, y mantenimiento de Service Builder (frente a Objects). Usar al crear o modificar un módulo, API, portlet o servicio OSGi, escribir JSP, serializar JSON, reaccionar a cambios de entidades, tocar service.xml o resolver referencias sin satisfacer. No usar para modelos de datos nuevos (liferay-objects-workflow) ni en SaaS (no admite módulos OSGi).'
---

# Módulos OSGi y Service Builder

## Reglas clave
- Solo disponible fuera de SaaS: antes de crear un módulo, comprueba que no basta configuración, Objects, contenido o client extensions (`liferay-extension-model`).
- Componentes Declarative Services con `@Reference`; sin `*LocalServiceUtil`/`*ServiceUtil` ni utilidades estáticas cuando existe el servicio OSGi.
- Utilidades propias como componentes `Helper`/`HelperImpl` (nunca sufijo `Util`).
- Entidades nuevas: Objects por defecto; Service Builder solo con los criterios de `references/service-builder.md`.
- Permisos antes de llamar a un `*LocalService` (`liferay-security`); logging con `Log` de Liferay; JSP sin scriptlets salvo `<c:set>` con expresiones en `init.jsp`/`configuration.jsp`.

## Referencias
| Tema | Fichero |
|---|---|
| Módulos API/impl, componentes DS, helpers, Lombok, Jackson | [components.md](references/components.md) |
| Portlets MVC, constantes, render, acciones, JSP, panel de control | [portlets.md](references/portlets.md) |
| Traducciones, model listeners, configuración tipada, tareas, overrides, Gogo Shell | [config-i18n-overrides.md](references/config-i18n-overrides.md) |
| Service Builder frente a Objects, mantenimiento, migración | [service-builder.md](references/service-builder.md) |

## Checklists
### Módulos OSGi
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

### Service Builder frente a Objects
- [ ] Entidad nueva como Object, o Service Builder justificado con los criterios y documentado
- [ ] Alternativas sin microservicios valoradas si el proyecto los prohíbe
- [ ] DTD de la versión y `dependency-injector="ds"`
- [ ] Columnas de auditoría y `uuid`
- [ ] Lógica en `*LocalServiceImpl`; permisos en `*ServiceImpl`
- [ ] Consumo con `@Reference`, nunca `*LocalServiceUtil`
- [ ] Clases generadas sin modificar; cambios de esquema con upgrade step
