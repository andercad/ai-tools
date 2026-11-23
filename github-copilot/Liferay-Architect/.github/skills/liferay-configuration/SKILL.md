---
name: liferay-configuration
description: 'Liferay DXP. Configuración del portal: portal-ext.properties y su prioridad, variables de entorno LIFERAY_*, ficheros .config de OSGi (formato, PIDs, configuraciones de fábrica), ámbitos System, Instance, Site y Portlet Settings, configuración por entorno en configs/ del workspace, configuración como código con client extensions, y feature flags. Usar cuando: cambiar una propiedad del portal, configurar un módulo OSGi por fichero, saber dónde va una configuración, separar configuración por entorno, exportar una configuración de System Settings, activar o desactivar una funcionalidad.'
argument-hint: 'Describe qué quieres configurar y en qué entornos.'
---

# Configuración

## Dónde va cada configuración

| Tipo | Mecanismo | Ejemplos |
|---|---|---|
| Arranque del portal, base de datos, clúster, rutas | `portal-ext.properties` o variables `LIFERAY_*` | JDBC, `cluster.link.enabled`, `locales.enabled` |
| Configuración de un módulo OSGi | Fichero `.config` en `osgi/configs/` o System Settings | Conector de búsqueda, almacén de documentos, módulos propios |
| Configuración por instancia (virtual instance) | Instance Settings (interfaz o client extension de instance settings) | Correo, autenticación, Analytics Cloud |
| Configuración por site | Site Settings | Idiomas del site, SEO |
| Configuración de un widget | Portlet/widget configuration | Opciones de una instancia de widget |

- En **SaaS** no hay `portal-ext.properties` ni `.config`: solo interfaz y client extensions de configuración (ver `liferay-cloud`).
- Las propiedades del portal se leen **al arrancar**: cambiar `portal-ext.properties` requiere reinicio. Los `.config` se aplican en caliente.
- Los valores que dependen del entorno se guardan **por nombre o clave**, no por ID (ver `liferay-content`).

## portal-ext.properties

```properties
# configs/common/portal-ext.properties
locales.enabled=es_ES,ca_ES
company.default.locale=es_ES
cluster.link.enabled=true

# configs/prod/portal-ext.properties — solo lo que cambia en producción
web.server.protocol=https
```

- **Nunca** edites `portal.properties` dentro de `portal-impl.jar`: sobrescribe en `portal-ext.properties`.
- Para cada propiedad, copia el bloque correspondiente de la referencia de `portal.properties` **de tu versión**: nombre exacto, valor por defecto y su variable de entorno (`Env:`).
- Prioridad: las variables de entorno `LIFERAY_*` prevalecen sobre `portal-ext.properties`. El asistente de instalación genera `portal-setup-wizard.properties`; no mezcles ambos sin saber cuál gana.
- Ya **no** existen ficheros por instancia `portal-<companyId>.properties` (eliminados en 7.3).

### Variables de entorno

- Formato: `LIFERAY_` + nombre en mayúsculas, `.` → `_PERIOD_`, mayúscula interna → `_UPPERCASE<letra>_`. Ejemplo: `locales.enabled` → `LIFERAY_LOCALES_PERIOD_ENABLED`.
- Úsalas para **secretos y valores que cambian por entorno**; deja en `portal-ext.properties` lo común.

## Ficheros .config (OSGi)

```config
# configs/common/osgi/configs/com.acme.orders.configuration.OrdersConfiguration.config
maxItemsPerPage=I"50"
notificationsEnabled=B"true"
allowedCountries=["ES","PT"]
```

- Nombre del fichero: el **PID** de la configuración + `.config`. Para configuraciones de fábrica (varias instancias), `<PID>~<nombre>.config`.
- Formato tipado: `I"..."` entero, `L"..."` long, `B"..."` booleano, cadenas entre comillas, listas entre corchetes. Sigue el formato que genera **Exportar** en System Settings.
- La forma más fiable de obtener un `.config` correcto es configurarlo en System Settings y usar **Exportar**: el PID y los tipos salen exactos.
- Los `.config` se colocan en `osgi/configs/` de Liferay Home (en el workspace, `configs/<entorno>/osgi/configs/`).
- **Secretos**: no los pongas en `.config` versionados. Algunas configuraciones admiten referencias a variables de entorno; comprueba la documentación de cada una, o inyéctalos en el despliegue.

## Configuración por entorno

- `configs/common/` + `configs/<entorno>/`, seleccionado con `liferay.workspace.environment` al generar el bundle o la imagen.
- En Docker, monta los ficheros en `/mnt/liferay/files` (ver `liferay-deployment`); en PaaS, `liferay/configs/<entorno>/` (ver `liferay-cloud`).
- Mantén `prod` mínimo: solo lo que realmente difiere.

## Configuración propia de un módulo

Ver `liferay-osgi` (interfaz `@Meta.OCD` + `ConfigurationProvider`). Elige el ámbito (`SYSTEM`, `COMPANY`, `GROUP`, `PORTLET_INSTANCE`) según quién debe poder cambiarla.

## Configuración como código

- Lo que debe ser igual en todos los entornos (objects, picklists, OAuth2, workflow, instance settings) se despliega desde el repositorio: client extensions de configuración y batch (ver `liferay-client-extensions`).
- Evita crear a mano en cada entorno lo que podría versionarse.

## Feature flags

- Liferay usa *feature flags* para funcionalidades en preparación: **release** (disponibles), **beta** y **dev**.
- No actives flags beta o dev en producción ni las uses en soluciones salvo petición explícita (restricción del agente). Si una funcionalidad necesaria está tras una flag, indícalo y deja la decisión al usuario.

## Checklist

- [ ] Cada configuración en su mecanismo y ámbito
- [ ] Propiedades copiadas de la referencia de la versión; ninguna modificación de `portal.properties`
- [ ] Variables `LIFERAY_*` para secretos y valores por entorno
- [ ] `.config` con PID y tipos exactos (exportados desde System Settings)
- [ ] `configs/common` + `configs/<entorno>`; `prod` mínimo
- [ ] Sin feature flags beta/dev salvo petición explícita
