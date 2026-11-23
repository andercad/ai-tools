# Guía de convenciones del proyecto — Acme Portal (ejemplo ficticio)

Guía para completar el `CLAUDE.md` del proyecto (junto al bloque `## Convenciones Liferay`). Contiene **solo lo específico de este proyecto**; las reglas generales están en los agentes y sus skills. Si algo del `CLAUDE.md` contradice al plugin, prevalece el `CLAUDE.md`.

## Proyecto

- Cliente: Acme Corp (Acme Portal).
- Paquete base del proyecto: `com.acme.portal`.
- Paquete base de los APIs genéricos del cliente (reutilizables entre proyectos): `com.acme`.
- Prefijo para client extensions, ERC y clases CSS: `acme`.

## Estructura del workspace

```
modules/
  apis/                      ← APIs genéricos del cliente (una subcarpeta por API: <api>-api y <api>-impl)
    cservicios/              ← módulos de Service Builder genéricos
  acmeportal/                 ← módulos del proyecto
    apis/                    ← APIs del proyecto (por ejemplo, integración con SAP)
    cservicios/              ← módulos de Service Builder del proyecto
recursos/                    ← recursos genéricos (no Java ni temas)
  adts/ estructuras/ fragmentos/ plantillas/
acmeportal/recursos/          ← recursos del proyecto
  adts/ estructuras/ fragmentos/ plantillas/
```

(Ajusta las rutas a las reales del repositorio.)

## Nomenclatura

- Symbolic Name y paquetes: `com.acme.portal.<modulo>.<tipo>` (proyecto) y `com.acme.<modulo>.<tipo>` (APIs genéricos). Ejemplo: Send Emails → carpeta `send-emails-api`, paquete `com.acme.send.emails.api`.
- Resto de nomenclatura de módulos, paquetes y clases: la de `liferay-extension-model`.

## Idiomas

- Idiomas del portal: castellano (`es_ES`) y catalán (`ca_ES`). Idioma por defecto: `es_ES`.
- Portlets: `Language.properties` (castellano) y `Language_ca_ES.properties`.
- Resource bundles: `Language_es_ES.properties` y `Language_ca_ES.properties`; sin `Language.properties`.

## Librerías

| Uso | Librería | Notas |
|---|---|---|
| JSON | Jackson | La versión que exporta Liferay; `compileOnly`, sin incluirla en el módulo |
| Getters, setters, constructores, clases de constantes | Lombok `<versión>` | `compileOnly` + `annotationProcessor`; `@UtilityClass` en clases de constantes |
| Excel | `org.apache.servicemix.bundles.poi` | Versión fijada y auditada |

## Plantillas

- Servicios y helpers en plantillas mediante el Template Context Contributor del proyecto (`AcmeTemplateContextContributor`), con la variable `acmeTemplateHelper`.
- Excepciones documentadas de uso de `serviceLocator`: ninguna. (Añade aquí cada excepción, con la plantilla y el motivo.)

## Modelo de despliegue y entornos

- Modelo de despliegue: `<SaaS | PaaS | Docker/Kubernetes | self-hosted clásico>`.
- Entornos: `local`, `dev`, `uat`, `prod` (carpetas de `configs/`).

## Control de versiones (para el equipo)

Los agentes no ejecutan operaciones de Git que modifiquen el repositorio; esta sección es para el equipo.

- Flujo **GitFlow** con la extensión GitFlow: ramas `feature` (desde `develop`, se cierran en `develop`), `release` (desde `develop`, se cierran en `develop` y `master` con tag) y `hotfix` (desde `master`, se cierran en `develop` y `master` con tag).
- Ramas por bloques funcionales (por ejemplo, servicio y portlet de FAQs en la misma rama).
- Mensajes de commit con el nombre de la rama al inicio (`faq: ...`, `develop: ...`).
- Nunca se mergean ramas `feature` entre sí sin cerrarse y pasar por `develop`.
- Las ramas se cierran siempre desde la extensión de GitFlow. Excepción: se permite mergear `develop` en la rama de trabajo cuando se ha cerrado otra rama y sus cambios ya están en `develop`.
