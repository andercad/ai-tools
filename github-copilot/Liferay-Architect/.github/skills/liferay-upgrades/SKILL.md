---
name: liferay-upgrades
description: 'Liferay DXP. Actualizaciones: releases trimestrales y LTS, actualizar la versión del workspace, adaptar módulos OSGi y client extensions, upgrade de base de datos (herramienta db_upgrade_client, auto upgrade, Docker con LIFERAY_UPGRADE_PERIOD_DATABASE_PERIOD_AUTO_PERIOD_RUN), upgrade steps de módulos propios (UpgradeStepRegistrator), Commerce, clúster, Gogo Shell para upgrades de módulos, y modernización de código heredado hacia Objects y client extensions. Usar cuando: pasar a un trimestral nuevo, preparar un plan de upgrade, añadir o cambiar columnas de tablas de módulos propios, fallos tras actualizar, migrar portlets o Service Builder heredados.'
argument-hint: 'Indica la versión de origen y de destino, y qué tiene el proyecto (módulos, client extensions, Commerce...).'
---

# Actualizaciones y modernización

## Plan de actualización

1. **Leer las notas de la versión de destino** (cambios incompatibles, deprecaciones, requisitos de JDK, base de datos y búsqueda).
2. **Copia de seguridad** de base de datos, almacén de documentos y configuración.
3. Actualizar el **workspace** (`liferay.workspace.product`, plugin) y compilar: corrige errores de compilación y revisa los **overrides del núcleo** (JSP, `ServiceWrapper`, MVC commands), que son lo primero que se rompe.
4. Revisar las **client extensions**: dependen de APIs headless versionadas y suelen funcionar sin cambios, pero comprueba los tipos y propiedades del YAML.
5. **Upgrade de base de datos** en un entorno de pruebas con una copia de producción; mide el tiempo.
6. Probar: funcionalidad, rendimiento, integraciones, reindexado si la guía lo indica.
7. Repetir en producción con la ventana de mantenimiento medida.

- Sigue la ruta de actualización soportada (desde qué versión se puede saltar a cuál) que indique Liferay.
- En **SaaS**, Liferay aplica las actualizaciones; tu trabajo es mantener client extensions e integraciones compatibles. En **PaaS**, sigue también la guía de upgrade de Liferay Cloud (ver `liferay-cloud`).

## Upgrade de base de datos

| Método | Cuándo |
|---|---|
| **Database Upgrade Tool** (`db_upgrade_client.sh` en `tools/portal-tools-db-upgrade-client` del bundle) | Bases de datos grandes o con muchas personalizaciones; con el servidor parado |
| **Auto upgrade** al arrancar (propiedad de portal) | Instalaciones pequeñas |
| **Docker** con `LIFERAY_UPGRADE_PERIOD_DATABASE_PERIOD_AUTO_PERIOD_RUN=true` | Contenedores: un contenedor de la versión nueva ejecuta el upgrade y luego se arranca uno normal **sin** la variable |
| **Gogo Shell** | Solo upgrades de módulos (no del núcleo) con el servidor en marcha |

```bash
cd tools/portal-tools-db-upgrade-client
./db_upgrade_client.sh -j "-Xmx8000m" -l upgrade.log
```

- Antes de la 7.4 U82 el script se llamaba `db_upgrade.sh`; en las versiones trimestrales es `db_upgrade_client.sh`.
- Usa las mismas opciones de JVM que el servidor (memoria, `UTF-8`, zona horaria GMT); la herramienta aplica valores por defecto si no las indicas.
- **Clúster**: el upgrade se ejecuta con **un solo nodo** contra la base de datos; el resto se arranca después. Nunca un *rolling update* con nodos de dos versiones sobre la misma base de datos.
- Poda datos innecesarios (versiones antiguas de contenidos y documentos) antes de upgrades grandes, siguiendo la guía oficial.
- **Commerce** tiene pasos previos propios (guía *Upgrading Liferay Commerce*).

## Upgrade steps en módulos propios

```java
@Component(service = UpgradeStepRegistrator.class)
public class AcmeOrdersUpgradeStepRegistrator implements UpgradeStepRegistrator {

	@Override
	public void register(Registry registry) {
		registry.register("1.0.0", "1.1.0", new AcmeOrderReferenceUpgradeProcess());
	}

}
```

```java
public class AcmeOrderReferenceUpgradeProcess extends UpgradeProcess {

	@Override
	protected void doUpgrade() throws Exception {
		if (!hasColumn("Acme_Order", "externalReference")) {
			alterTableAddColumn("Acme_Order", "externalReference", "VARCHAR(75) null");
		}
	}

}
```

- **Requiere módulos OSGi: no aplica en SaaS.**
- Cada cambio de esquema de Service Builder sube la versión del esquema del módulo y añade un paso. Comprueba antes de alterar (`hasColumn`, `hasTable`) para que el paso sea repetible.
- Usa los métodos de `UpgradeProcess` de tu versión (alterar tablas, ejecutar consultas con parámetros); no SQL específico de un motor si existe método portable.
- Los upgrades de módulos pueden consultarse y ejecutarse con Gogo Shell (`upgrade:list`, `upgrade:execute`); comprueba los comandos en tu versión.

## Modernización de código heredado

Prioriza por **riesgo en los upgrades** y valor de negocio:

| Heredado | Destino moderno |
|---|---|
| Portlets con interfaz propia | Custom elements (client extension) o fragments |
| Entidades de Service Builder | Objects, si cumplen los criterios de `liferay-service-builder` |
| Model listeners para integrar | Acciones de objeto como client extension |
| Temas WAR | Style books + theme CSS |
| Overrides de JSP | Puntos de extensión oficiales o client extensions |
| Servicios JSON-WS consumidos fuera | APIs headless (de Objects o REST Builder) |
| `serviceLocator` en plantillas | Template Context Contributor con helpers (ver `liferay-content`) |
| Dependencias entre módulos con `mavenLocal()` | `compileOnly project(...)` o repositorio Maven corporativo (ver `liferay-workspace`) |
| Configuración manual en cada entorno | Configuración como código (batch, client extensions, `configs/`) |

- Migra por partes, con convivencia temporal y datos reales de prueba.
- Lo que deba seguir en módulos (por falta de alternativa), mantenlo con baseline, tests y sin overrides innecesarios.

## Checklist

- [ ] Notas de la versión leídas; ruta de actualización soportada
- [ ] Copia de seguridad completa y prueba con copia de producción
- [ ] Workspace actualizado, compilación limpia, overrides revisados
- [ ] Método de upgrade de base de datos adecuado; un solo nodo en clúster
- [ ] Upgrade steps repetibles para cambios de esquema propios
- [ ] Commerce, PaaS y reindexado según sus guías
- [ ] Plan de modernización priorizado por riesgo en upgrades
