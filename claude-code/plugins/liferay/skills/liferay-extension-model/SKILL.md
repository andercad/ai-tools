---
name: liferay-extension-model
description: 'Liferay DXP. Elección del mecanismo de extensión (configuración, Objects y contenido, client extensions, módulos OSGi, overrides del núcleo) y qué admite cada modelo de despliegue (SaaS, PaaS, self-hosted). Usar al decidir cómo implementar un requisito en Liferay, antes de crear un módulo, una entidad o una personalización, o al dudar si algo es posible en SaaS o PaaS. No usar para el diseño detallado de un mecanismo ya elegido (skills de cada tema).'
---

# Modelo de extensión de Liferay

## Orden de preferencia
Usa la **primera** opción que resuelva el requisito y justifica el salto cuando no sea la primera posible.

1. **Funcionalidad y configuración estándar**: System/Instance/Site Settings, widgets y aplicaciones incluidas, Liferay Forms, workflow, permisos. Muchas peticiones no requieren código.
2. **Objects y contenido**: modelos de datos con Objects; estructuras y plantillas de contenido web, ADT, fragments y páginas de contenido. Entidades nuevas: **Objects por defecto**; Service Builder solo con los criterios de `liferay-osgi` (`references/service-builder.md`).
3. **Client extensions**: interfaz (custom elements, CSS/JS globales, temas), lógica externa (acciones de objeto y de workflow, validaciones, Commerce) y configuración como código. Funcionan en **todos** los modelos de despliegue y se desacoplan de las actualizaciones.
4. **Módulos OSGi**: lógica dentro del servidor que lo anterior no cubre (portlets, model listeners, indexadores, APIs con REST Builder, Template Context Contributors, integraciones de bajo nivel). **No disponibles en SaaS.**
5. **Overrides del núcleo**: `ServiceWrapper`, overrides de JSP, de comandos MVC o de traducciones del portal. **Último recurso**: se rompen con las actualizaciones. Justifícalos, documéntalos y añade un test que detecte la rotura.

**Nunca**: plugins Ext, modificar a mano ficheros del bundle de Liferay ni cambiar tablas de Liferay con SQL directo.

## Qué admite cada modelo de despliegue
| Modelo | Señales | Admite |
|---|---|---|
| SaaS | sin acceso al servidor; solo client extensions | client extensions y configuración. Ni módulos OSGi, ni `portal-ext.properties` |
| PaaS (Liferay Cloud) | ficheros `LCP.json` por servicio | todo, pero la configuración va en el repositorio y en las variables del servicio, no en el servidor |
| Self-hosted Docker/Kubernetes | `Dockerfile`, Helm, `configs/docker` | todo; configuración por variables `LIFERAY_*` y volúmenes |
| Self-hosted clásico | bundle Tomcat o servidor de aplicaciones | todo |

Si las señales no son concluyentes, pregunta: condiciona qué se puede construir. Nunca propongas algo que el modelo detectado no admite.

## Reglas transversales
- **Versión real**: solo APIs, propiedades y tipos de client extension de la versión de `liferay.workspace.product` (mínimo 2025.Q1). No mezcles APIs de distintas versiones ni de 7.4 anteriores a los releases trimestrales.
- **Sin SQL directo** sobre tablas de Liferay: servicios, APIs headless, batch o upgrade steps.
- **Permisos** en toda operación sobre datos (`liferay-security`).
- **Configuración como código**: lo que deba existir igual en todos los entornos (objects, picklists, client extensions, OAuth2, workflow, configuración) se despliega desde el repositorio con ERC estables.
- **Secretos** nunca en el repositorio: variables de entorno, secretos de Kubernetes o del servicio PaaS.
- **Sin funciones experimentales**: no actives feature flags beta/dev ni uses APIs experimentales salvo petición expresa, e indícalo.

## Nomenclatura (valores concretos en `## Convenciones Liferay` del `CLAUDE.md`: `base-package`)
Carpetas en kebab-case (`send-emails`); Symbolic Name y paquetes con el nombre separado por puntos.

| Tipo de módulo | Sufijo de carpeta | Symbolic Name |
|---|---|---|
| Widget (portlet) | `-web` | `<base>.<modulo>.web` |
| Service Builder | genera `-api` y `-service` | `<base>.<modulo>.api` y `.service` |
| API / implementación | `-api` / `-impl` | `<base>.<modulo>.api` / `.impl` |
| Resource bundle | `-resource-bundle` | `<base>.<modulo>` |
| Indexador / REST | `-indexer` / `-rest` | `<base>.<modulo>.indexer` / `.rest` |
| Override de JSP / Tests | `-override` / `-test` | `<base>.<modulo>.override` / `.test` |
| Tema / themelet | `-theme` / `-themelet` | — |

Client extensions: kebab-case con prefijo del proyecto (`acme-orders-custom-element`). Objects: PascalCase singular (`Order`; Liferay añade `C_`). ERC estables y legibles (`acme-order-status-picklist`).

Clases: `[Portlet]Portlet`, `[Portlet]PortletKeys`, `[Portlet]DefaultMVCRenderCommand`, `[Funcionalidad]MVCRenderCommand|MVCActionCommand|MVCResourceCommand`, `[Portlet]PortletConfiguration`, `[Portlet]PanelApp`, `[Funcionalidad]DisplayContext`, `[Funcionalidad]Helper`/`HelperImpl`, `[Funcionalidad]Api`/`ApiImpl`, `[Portlet]RestApplication`, `[Funcionalidad]DispatchTaskExecutor`, `[Proyecto]TemplateContextContributor`. Sin sufijo `Util` en componentes OSGi.
