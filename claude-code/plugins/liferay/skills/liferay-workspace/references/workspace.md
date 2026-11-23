# Liferay Workspace

Los proyectos son siempre **Liferay Workspace con Gradle**. El workspace fija la versión de Liferay contra la que se compila todo, y de esa versión dependen las APIs disponibles.

## 1. Detectar la versión

```properties
# gradle.properties
liferay.workspace.product=dxp-2025.q1.0
```

- `liferay.workspace.product` es la **fuente de verdad** de la versión. El formato es `dxp-<año>.q<trimestre>.<actualización>`; las releases LTS pueden llevar sufijo (`-lts`). Lista los valores válidos con `blade init -l`.
- **Mínimo soportado por este agente: 2025.Q1.** Si encuentras una versión 7.4 `uXX` o un trimestral anterior, avisa y pregunta antes de generar código.
- Otras propiedades que conviene leer: `liferay.workspace.docker.image.liferay` (imagen del contenedor), `liferay.workspace.environment` (entorno por defecto), `liferay.workspace.home.dir` (bundle local), `liferay.workspace.node.package.manager` (client extensions de frontend).
- El plugin del workspace está en `settings.gradle` (`com.liferay.gradle.plugins.workspace`). Una versión del plugin muy antigua puede no soportar la versión del producto: actualízalo siguiendo la guía oficial.

### JDK y espacio de nombres

- Desde 2024.Q3 Liferay soporta **JDK 17 y 21** (JDK 11 eliminado). Compila y ejecuta con el **mismo** JDK.
- La plataforma está migrando de `javax.*` a `jakarta.*` (la documentación de Workspace incluye una guía *Upgrading to Jakarta*). **Comprueba qué espacio de nombres usa tu versión** (dependencias resueltas o código de `liferay-portal` en esa etiqueta) y no mezcles imports de ambos.

## 2. Detectar el modelo de despliegue

| Señal en el repositorio | Modelo | Restricciones principales |
|---|---|---|
| Carpetas de servicio con `LCP.json` (`liferay/`, `database/`, `search/`, `webserver/`, `backup/`, `ci/`) | **PaaS** (Liferay Cloud) | Módulos OSGi permitidos; configuración por repositorio y variables del servicio (ver `liferay-config-operations`) |
| Solo `client-extensions/`, uso de la CLI `lcp` para desplegar, sin `modules/` | **SaaS** | **Solo client extensions y configuración**; sin módulos OSGi ni `portal-ext.properties` (ver `liferay-config-operations`) |
| `Dockerfile`/`Dockerfile.ext`, manifiestos de Kubernetes, valores de Helm, `configs/docker` usado en producción | **Self-hosted con contenedores** | Imagen oficial de Liferay; configuración por variables de entorno y ficheros montados (ver `liferay-config-operations`) |
| `configs/<entorno>/` con `portal-ext.properties`, bundle Tomcat, scripts de despliegue sobre servidores | **Self-hosted clásico** | Bundle o servidor de aplicaciones (ver `liferay-config-operations`) |

Si las señales no son concluyentes (por ejemplo, un workspace nuevo), **pregunta** antes de diseñar: un módulo OSGi no sirve en SaaS.

## 3. Estructura

```
gradle.properties
settings.gradle
gradlew / gradlew.bat
modules/                 ← módulos OSGi (subcarpetas según guidelines)
client-extensions/       ← un proyecto por carpeta, con client-extension.yaml
themes/                  ← temas clásicos (preferir temas como client extension)
configs/
  common/                ← se aplica a todos los entornos
  local/ dev/ uat/ prod/ ← se superpone a common según liferay.workspace.environment
  docker/                ← contenedor de desarrollo
```

- Dentro de `configs/<entorno>/` se replica la estructura de Liferay Home: `portal-ext.properties`, `osgi/configs/*.config`, `tomcat/bin/setenv.sh`...
- Las subcarpetas de `modules/` (APIs genéricos, proyecto, Service Builder) y la carpeta de recursos no Java (estructuras, plantillas, ADT, fragments) siguen las guidelines del proyecto.
- No pongas secretos en `configs/`: usa variables de entorno (ver `liferay-config-operations`).

## 4. Crear proyectos con Blade

```powershell
blade create -l                                   # plantillas disponibles en tu versión de Blade
blade create -t mvc-portlet -p com.acme.orders.web -c OrdersPortlet orders-web
blade create -t api -p com.acme.send.emails.api send-emails-api
blade create -t service -p com.acme.send.emails.impl send-emails-impl
blade create -t service-builder -p com.acme.orders orders   # solo si se justifica (ver liferay-osgi)
blade create -t rest-builder -p com.acme.orders.rest orders-rest
blade create -t client-extension acme-orders-custom-element  # pregunta por el tipo
```

- Comprueba la lista de plantillas y sus opciones con `blade create -l` y `blade create --help`: cambian entre versiones de Blade.
- Tras crear un módulo, ajusta el nombre de carpeta y el `Bundle-SymbolicName` a la nomenclatura del agente.

## 5. Dependencias

### APIs de Liferay

```groovy
// modules/orders/orders-web/build.gradle
dependencies {
	compileOnly group: "com.liferay.portal", name: "release.dxp.api"
}
```

- `release.dxp.api` aporta las APIs de la versión del producto **sin indicar versión**: la fija `liferay.workspace.product`. No añadas versiones sueltas de artefactos de Liferay que ya incluye.
- Solo `compileOnly` para APIs de Liferay: la implementación la proporciona el contenedor OSGi.

### Entre módulos del mismo workspace

```groovy
dependencies {
	compileOnly group: "com.liferay.portal", name: "release.dxp.api"
	compileOnly project(":modules:apis:send-emails:send-emails-api")
}
```

- Referencia el módulo por su **ruta Gradle** (`project(":modules:...")`): se compila en el orden correcto y no hay que instalar nada.
- El consumidor depende solo del módulo **API**, nunca de la implementación.
- **No uses `mavenLocal()`** ni publiques en el repositorio local de Maven: el build depende de lo que haya instalado cada desarrollador y falla en CI. El plugin `maven` de Gradle (`apply plugin: "maven"`) además ya no existe: se eliminó en Gradle 7 y los workspaces actuales usan Gradle 8.

### Entre workspaces distintos

Si un API se reutiliza desde otro workspace (por ejemplo, APIs genéricos del cliente en un repositorio propio):

1. El workspace que lo produce lo publica con el plugin `maven-publish` en el **repositorio Maven corporativo** (Nexus, Artifactory...), desde CI.
2. El consumidor declara ese repositorio en `settings.gradle`/`build.gradle` y la dependencia con versión fija:

```groovy
dependencies {
	compileOnly group: "com.acme", name: "com.acme.send.emails.api", version: "1.2.0"
}
```

- Credenciales del repositorio por variables de entorno o propiedades de Gradle del usuario (`~/.gradle/gradle.properties`), nunca en el repositorio.

### Librerías de terceros

- Primero comprueba si Liferay ya la proporciona (`release.dxp.api`, o en Gogo Shell `lb <nombre>`). Si la exporta, `compileOnly` con esa versión y **sin incluirla** en tu módulo: dos copias de la misma librería en OSGi causan errores difíciles de diagnosticar.
- Si no la proporciona, inclúyela en el módulo (`compileInclude`) y revisa licencia y vulnerabilidades.
- Lombok y Jackson: ver `liferay-osgi`.

## 6. Tareas habituales

```powershell
./gradlew initBundle                              # descarga y prepara el bundle local en bundles/
./gradlew deploy                                  # compila y despliega todo al bundle local
./gradlew :modules:orders:orders-web:deploy       # un solo módulo
./gradlew :client-extensions:acme-orders-custom-element:deploy
./gradlew buildService                            # Service Builder (en el módulo service)
./gradlew buildREST                               # REST Builder (en el módulo impl)
./gradlew distBundleZip -Pliferay.workspace.environment=prod   # bundle con la configuración del entorno
./gradlew buildDockerImage                        # imagen con módulos, client extensions y configs/docker
./gradlew formatSource                            # Source Formatter (ver liferay-testing-quality)
./gradlew testIntegration                         # tests de integración (ver liferay-testing-quality)
```

- Comprueba los nombres exactos con `./gradlew tasks`: dependen de la versión del plugin.
- Para desplegar a un contenedor en ejecución: `./gradlew deploy -Ddeploy.docker.container.id=<id>`.

## 7. Actualizar la versión

1. Cambiar `liferay.workspace.product` a la nueva versión y, si hace falta, la versión del plugin del workspace en `settings.gradle`.
2. Compilar todo y corregir las incompatibilidades.
3. Seguir el procedimiento de `liferay-workspace` (base de datos, módulos, client extensions, pruebas).
