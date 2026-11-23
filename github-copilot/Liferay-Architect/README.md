# Liferay Architect — v2

Agente de desarrollo de Liferay DXP para GitHub Copilot, con 22 skills. Pensado para proyectos con **Liferay Workspace (Gradle)** y **Liferay DXP 2025.Q1 o posterior**. Incluye la metodología de desarrollo del equipo (nomenclatura, portlets, plantillas, literales, librerías).

## Instalación

1. Copia en la raíz del workspace:

   ```
   .github/agents/Liferay Architect.agent.md
   .github/skills/                 ← las 22 carpetas liferay-*
   guidelines/coding-guidelines.md ← plantilla: adáptala al proyecto
   ```

2. Revisa `guidelines/coding-guidelines.md`. Viene rellenada con los datos de InmoCaixa (paquete `com.caixa.inmo`, carpetas, castellano y catalán, librerías, GitFlow). Ajusta las rutas reales, el modelo de despliegue y las versiones.

3. La carpeta `validation/` sirve para comprobar el agente cuando lo modifiques; no hace falta en el repositorio del proyecto.

## Dónde está cada parte de la metodología

| Metodología | Dónde |
|---|---|
| Nomenclatura de módulos, paquetes y clases | Agente (reglas generales con `<base>`) y guidelines (paquete `com.caixa.inmo`) |
| Estructura de carpetas (`apis`, `cservicios`, recursos) | Guidelines |
| Dependencias entre módulos | `liferay-workspace`: `compileOnly project(...)` o repositorio Maven corporativo (sustituye a `mavenLocal`) |
| Constantes, render por defecto, preferencias, JSP, `portletNamespace`, `ParamUtil`, panel de control | `liferay-osgi` |
| Consumo de Service Builder y clases de utilidad por referencia | `liferay-osgi` y `liferay-service-builder` |
| Plantillas de resumen y detalle, bloques, ADT, valores por nombre, `JournalConverter` | `liferay-content` |
| Literales (portlet y resource bundle) | `liferay-osgi` |
| Lombok, Jackson, POI | `liferay-osgi` y guidelines |
| GitFlow | Guidelines (el agente no hace operaciones de Git que modifiquen el repositorio) |

## Cambios respecto a la metodología v1.2

Acordados en la revisión:

- **`serviceLocator`** → **Template Context Contributor** con helpers. `serviceLocator` solo como excepción documentada en las guidelines. Se elimina el bloque *Services* de las plantillas.
- **Utilidades** → `[Funcionalidad]Helper` / `[Funcionalidad]HelperImpl`. Los APIs pasan a `[Funcionalidad]Api` / `[Funcionalidad]ApiImpl`, para que no compartan el sufijo `UtilImpl`.
- **JSON** → Jackson (versión de la instalación), en lugar de GSON.
- **Dependencias** → sin `mavenLocal()` ni plugin `maven` (eliminado en Gradle 7).
- **Entidades nuevas** → Objects por defecto; Service Builder con los criterios de `liferay-service-builder`.

## Criterio de extensión

1. Funcionalidad y configuración estándar.
2. Objects y contenido.
3. Client extensions.
4. Módulos OSGi (no en SaaS).
5. Overrides del núcleo, solo como último recurso y documentados.

## Skills

| Área | Skills |
|---|---|
| Proyecto y despliegue | `liferay-workspace`, `liferay-deployment`, `liferay-cloud`, `liferay-configuration`, `liferay-upgrades` |
| Desarrollo | `liferay-osgi`, `liferay-service-builder`, `liferay-objects`, `liferay-client-extensions`, `liferay-headless` |
| Contenido y experiencia | `liferay-content`, `liferay-fragments`, `liferay-sites`, `liferay-workflow`, `liferay-search` |
| Negocio y marketing | `liferay-commerce`, `liferay-personalization`, `liferay-analytics` |
| Transversal | `liferay-security`, `liferay-testing`, `liferay-troubleshooting`, `liferay-quality` |
