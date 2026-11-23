---
name: liferay-deployment
description: 'Liferay DXP. Despliegue self-hosted: bundle Tomcat clásico o servidor de aplicaciones, imagen Docker oficial (liferay/dxp), carpetas montadas (/mnt/liferay), variables LIFERAY_*, Kubernetes con el Helm chart oficial liferay-default (AKS, EKS, GKE, OpenShift), clúster (Cluster Link, sesiones persistentes), almacén de documentos (S3, Advanced File System Store) y JVM. Usar cuando: dockerizar Liferay, desplegar en Kubernetes o AKS, preparar un bundle para producción, configurar un clúster, montar ficheros en el contenedor, ajustar memoria y JVM, elegir el almacén de documentos.'
argument-hint: 'Describe el entorno: bundle clásico, Docker o Kubernetes, número de nodos y servicios externos.'
---

# Despliegue self-hosted

Para Liferay PaaS y SaaS ver `liferay-cloud`. Esta skill cubre los despliegues que gestiona tu organización.

## Piezas de cualquier entorno de producción

| Pieza | Producción | Notas |
|---|---|---|
| Liferay DXP | Bundle Tomcat, servidor de aplicaciones o contenedor | Mismo JDK con el que se compila |
| Base de datos | Base de datos soportada por la versión (matriz de compatibilidad) | Nunca la base de datos embebida |
| Búsqueda | Elasticsearch u OpenSearch **remoto** | El modo de desarrollo (sidecar/embebido) no es para producción (ver `liferay-search`) |
| Documentos | Almacén compartido entre nodos: S3 (u otro almacenamiento de objetos) o Advanced File System Store en almacenamiento compartido | Con varios nodos, nunca disco local de cada nodo |
| Proxy / balanceador | Con sesiones persistentes si hay varios nodos | TLS terminado en el proxy o en el ingress |

## Self-hosted clásico (bundle)

```powershell
./gradlew distBundleZip -Pliferay.workspace.environment=prod
```

- Genera un bundle con los módulos, client extensions y la configuración de `configs/common` + `configs/prod`.
- Estructura de **Liferay Home**: `deploy/` (despliegue en caliente), `osgi/` (módulos y `configs/`), `data/` (incluido el almacén de documentos por defecto), `logs/`, `portal-ext.properties`, y la carpeta del servidor (`tomcat/`).
- JVM en `tomcat/bin/setenv.sh` (memoria, codificación `UTF-8`, zona horaria **GMT**, opciones de GC). Parte de las recomendaciones de la guía oficial de configuración de la JVM de tu versión.
- Si se instala sobre un servidor de aplicaciones existente (WAR + dependencias), sigue la guía de instalación de ese servidor para tu versión.
- Despliegue de cambios: copia los artefactos a `deploy/` o reinstala el bundle; en producción, preferir despliegues completos y reproducibles desde CI.

## Docker

```bash
docker run -it -m 8g -p 8080:8080 \
  -e LIFERAY_JVM_OPTS=-Xms4g\ -Xmx6g \
  -e LIFERAY_JDBC_PERIOD_DEFAULT_PERIOD_USERNAME=liferay \
  -e LIFERAY_JDBC_PERIOD_DEFAULT_PERIOD_PASSWORD="${DB_PASSWORD}" \
  -v $(pwd)/mnt:/mnt/liferay \
  liferay/dxp:<tag>
```

- **Imagen oficial** `liferay/dxp:<tag>`, con la etiqueta de la versión del workspace. El workspace puede construir una imagen propia con `./gradlew buildDockerImage` a partir de `liferay.workspace.docker.image.liferay`.
- **Propiedades del portal como variables de entorno**: prefijo `LIFERAY_`, mayúsculas, `.` → `_PERIOD_` y las mayúsculas internas → `_UPPERCASE<letra>_` (por ejemplo, `jdbc.default.driverClassName` → `LIFERAY_JDBC_PERIOD_DEFAULT_PERIOD_DRIVER_UPPERCASEC_LASS_UPPERCASEN_AME`). **Copia el nombre exacto** que documenta `portal.properties` (`Env:`) en lugar de construirlo. Las variables de entorno tienen prioridad sobre `portal-ext.properties`.
- `LIFERAY_JVM_OPTS` se añade a `CATALINA_OPTS`: escapa los espacios con `\`, sin comillas.
- **Carpetas que procesa el contenedor**:
  - `/mnt/liferay/files` → se copia a `/opt/liferay` antes de arrancar (por ejemplo `portal-ext.properties`, `osgi/configs/*.config`, `tomcat/bin/setenv.sh`).
  - `/mnt/liferay/deploy` → artefactos a desplegar.
  - `/mnt/liferay/scripts` → scripts que se ejecutan antes de arrancar.
  - `/usr/local/liferay/scripts/{pre-configure,pre-startup,post-shutdown}` → ganchos del ciclo de vida.
  - `/mnt/liferay/patching` → parches, si aplica.
- **Secretos** (contraseñas de base de datos, claves) siempre por variables de entorno o secretos del orquestador, nunca en la imagen ni en ficheros versionados.
- Una misma imagen para todos los entornos; lo que cambia entre entornos va en variables y ficheros montados.
- Los contenedores son efímeros: `data/` y el almacén de documentos deben estar en volúmenes o servicios externos.

## Kubernetes

- Liferay publica el Helm chart oficial **`liferay-default`** (en `liferay-portal/cloud/helm/default`) dentro de su *Cloud Native Experience*, para cualquier clúster compatible con CNCF: AKS, EKS, GKE, OpenShift o clústeres propios. Despliega Liferay como **StatefulSet** y se conecta a base de datos, búsqueda y almacenamiento de objetos externos mediante *Secrets*. Úsalo como punto de partida en lugar de manifiestos propios, y consulta su documentación para la versión del chart.
- Tú gestionas el clúster y los servicios: base de datos, Elasticsearch/OpenSearch, almacenamiento de objetos, ingress y observabilidad.
- **Probes**: la de *readiness* no debe dar el pod por listo hasta que Liferay haya arrancado por completo; el arranque es largo, así que usa una *startup probe* o un retraso inicial generoso para que *liveness* no reinicie pods que siguen arrancando.
- **Recursos**: `requests`/`limits` coherentes con la memoria de la JVM (deja margen fuera del heap).
- **Varias réplicas**: clúster de Liferay (ver abajo), sesiones persistentes en el ingress y almacén de documentos compartido.
- **Despliegues**: los cambios de módulos o client extensions generan una imagen nueva (o se montan), con despliegue progresivo. Cuidado con las actualizaciones que requieren upgrade de base de datos: no hagas un *rolling update* sobre ellas (ver `liferay-upgrades`).

## Clúster

```properties
# portal-ext.properties (común a todos los nodos)
cluster.link.enabled=true
```

- Todos los nodos comparten base de datos, búsqueda remota y almacén de documentos.
- Cluster Link sincroniza cachés entre nodos; el transporte (multicast o unicast) depende de la red. En Kubernetes y en la nube suele hacer falta descubrimiento unicast; sigue la guía de clustering de tu versión.
- **Sesiones persistentes** (*sticky sessions*) en el balanceador o ingress.
- El despliegue en caliente debe hacerse en **todos** los nodos (o mediante imagen nueva).
- Las tareas programadas y la indexación están coordinadas por el clúster; no programes trabajos propios que asuman un único nodo sin comprobarlo.

## Almacén de documentos

| Almacén | Cuándo |
|---|---|
| S3 o almacenamiento de objetos compatible | Contenedores, Kubernetes y nube |
| Advanced File System Store | Servidores con almacenamiento compartido (NFS, SAN) |
| Simple File System Store (por defecto) | Solo un nodo o desarrollo |

- El cambio de almacén con datos existentes requiere migración: usa la herramienta de migración de almacenes de la versión, nunca copias a mano.
- Configuración mediante su fichero `.config` (ver `liferay-configuration`); credenciales por variables de entorno.

## Checklist

- [ ] Base de datos externa y soportada; búsqueda remota; almacén compartido si hay varios nodos
- [ ] Mismo JDK en compilación y ejecución; JVM con UTF-8 y GMT
- [ ] Imagen oficial con la etiqueta de la versión del workspace
- [ ] Variables `LIFERAY_*` copiadas de `portal.properties`; secretos fuera de la imagen y del repositorio
- [ ] Probes de Kubernetes adaptadas al arranque de Liferay
- [ ] Clúster con Cluster Link, sesiones persistentes y despliegues en todos los nodos
- [ ] Upgrades de base de datos fuera de *rolling updates*
