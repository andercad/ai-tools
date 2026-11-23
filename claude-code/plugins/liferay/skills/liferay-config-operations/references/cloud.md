# Liferay PaaS y SaaS

| | PaaS (Liferay Cloud) | SaaS |
|---|---|---|
| Quién opera la infraestructura | Liferay; tú controlas la configuración de los servicios | Liferay por completo |
| Módulos OSGi y temas clásicos | Sí | **No** |
| `portal-ext.properties` / `.config` | Sí, desde el repositorio | **No**: configuración por la interfaz o client extensions de configuración |
| Client extensions | Sí | Sí: es la forma principal de extender |
| Despliegue | CI del proyecto o CLI `lcp` | CLI `lcp` con el archivo de la client extension |

## PaaS

### Repositorio

```
liferay/
  LCP.json
  gradle.properties            ← liferay.workspace.product y liferay.workspace.docker.image.liferay
  modules/ client-extensions/ themes/
  configs/
    common/ dev/ uat/ prd/     ← portal-ext.properties, osgi/configs... por entorno
database/LCP.json
search/LCP.json                ← con su propia carpeta configs/ (por ejemplo, plugins o ajustes de Elasticsearch)
webserver/LCP.json             ← nginx: configuración de rutas, cabeceras, WAF
backup/LCP.json
ci/LCP.json                    ← Jenkins; Jenkinsfile del proyecto
```

- Cada servicio tiene su `LCP.json` con la imagen del servicio, CPU, memoria, réplicas, variables de entorno, volúmenes, probes y overrides por entorno (`environments`).
- La imagen del servicio de Liferay Cloud (`liferaycloud/liferay-dxp:...`) se fija en `liferay/LCP.json`, y la imagen de DXP (`liferay/dxp:<versión>`) en `liferay/gradle.properties` con `liferay.workspace.docker.image.liferay`. Mantén ambas alineadas con `liferay.workspace.product`.
- Las versiones de las imágenes de servicio se actualizan siguiendo el registro de cambios de servicios de Liferay Cloud.

```json
{
  "id": "liferay",
  "image": "liferaycloud/liferay-dxp:7.4-5.9.0",
  "memory": 8192,
  "cpu": 8,
  "scale": 1,
  "env": {
    "LIFERAY_JVM_OPTS": "-Xms4096m -Xmx6144m"
  },
  "environments": {
    "prd": { "memory": 16384, "cpu": 12, "scale": 2 },
    "dev": { "memory": 8192, "cpu": 8 }
  }
}
```

(Valores de ejemplo: la imagen y los recursos dependen de tu suscripción y del registro de cambios de servicios.)

### Configuración y secretos

- `configs/<entorno>/` del servicio `liferay` se superpone a `configs/common/`, igual que en el workspace (ver `liferay-config-operations`).
- **Secretos** (contraseñas, claves de API, tokens) como **secretos o variables de entorno en la consola de Liferay Cloud**, nunca en `LCP.json` ni en `configs/` del repositorio.
- La conexión a la base de datos y a la búsqueda la configura la plataforma: no la redefinas salvo indicación de la documentación.

### Construir y desplegar

- Un *push* o una *pull request* lanzan el CI (Jenkins) que compila el workspace y genera un build; el despliegue a un entorno se hace desde la consola, automáticamente desde CI o con la CLI:

```powershell
lcp login
lcp deploy --project <proyecto> --environment <entorno>   # desde la carpeta del servicio
```

- Despliega en este orden: `dev` → `uat` → `prd`, el **mismo build** promocionado entre entornos.
- Copias de seguridad: el servicio `backup` las gestiona; antes de un upgrade de versión, comprueba que hay una reciente y cómo restaurarla.
- Los upgrades de versión de DXP siguen `liferay-workspace` y la guía de upgrade de Liferay Cloud.

## SaaS

- **Solo client extensions** (ver `liferay-client-extensions`) y configuración funcional. No hay módulos OSGi, `portal-ext.properties`, ficheros `.config`, temas WAR, acceso al servidor ni a la base de datos.
- La configuración que en self-hosted iría en ficheros se hace por la interfaz o, si debe versionarse, con **client extensions de configuración** (instance settings, OAuth2) y **batch/site initializer** para datos y objetos.
- **Microservicios**: las client extensions de tipo microservicio (Spring Boot, Node...) se empaquetan en el archivo de la client extension (LUFFA) y Liferay las aloja. Respeta los límites y cuotas del plan.
- **Despliegue** con la CLI `lcp` del archivo de la client extension en cada entorno.
- **Recuperación ante desastres**: si se contrata el entorno DR, desplegar las client extensions también en él es **responsabilidad del cliente**.
- Las actualizaciones de versión las aplica Liferay según su calendario: por eso solo se usan APIs headless versionadas y client extensions, que no dependen de APIs internas.

### ¿Se puede hacer en SaaS?

| Necesidad | En SaaS |
|---|---|
| Lógica al crear o actualizar un registro | Acción de objeto (client extension de microservicio) |
| Validación compleja de un objeto | Validación de objeto como client extension, o reglas de validación del propio objeto |
| Interfaz a medida | Custom element o IFrame |
| Cambiar el aspecto | Theme CSS, CSS/JS globales, favicon, sprite map |
| Integrar un sistema externo | Microservicio + APIs headless + OAuth2 |
| Datos o configuración iniciales | Batch o site initializer |
| Model listener, indexador, `ServiceWrapper`, override de JSP, Template Context Contributor | **No**: rediseña con lo anterior |
