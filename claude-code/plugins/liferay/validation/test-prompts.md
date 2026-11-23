# Prompts de prueba (manuales, en un Liferay Workspace de ejemplo)

Instala el plugin y lanza cada prompt en sesión limpia. Marca el resultado.

| # | Prompt | Debe cargar / hacer | Resultado |
|---|---|---|---|
| 1 | Necesito guardar pedidos con estado y cliente | `liferay-extension-model`, `liferay-objects-workflow`; propone Object (no Service Builder), ERC estables, definición como código | |
| 2 | Añade una columna a la entidad de Service Builder `Invoice` | `liferay-osgi` (`references/service-builder.md`); `service.xml`, `buildService`, upgrade step; no SQL directo | |
| 3 | Con `deployment: saas`: crea un portlet con un model listener | rechaza OSGi en SaaS; propone client extension / acción de objeto | |
| 4 | Usa `serviceLocator` en la plantilla para llamar a mi servicio | `liferay-content-experience`; lo desaconseja y crea un Template Context Contributor con helper | |
| 5 | Llama a `OrderLocalService.deleteOrder` desde un `MVCActionCommand` | `liferay-security`; comprueba permisos (`ModelResourcePermission`) o usa el servicio remoto | |
| 6 | Pon la contraseña del SMTP en `portal-ext.properties` del repo | `liferay-config-operations`; lo desaconseja; variable de entorno / secreto | |
| 7 | Crea un custom element Angular y regístralo en Liferay | `liferay-client-extensions`; `client-extension.yaml`; remite el código Angular a `angular-dev` si está instalado | |
| 8 | Busca la categoría por su ID en la plantilla | `liferay-content-experience`; por nombre o clave, nunca por ID | |
| 9 | Planifica la subida al siguiente trimestral | `liferay-workspace` (`references/upgrades.md`); lee `liferay.workspace.product`; plan de BD, módulos y client extensions | |
| 10 | ¿Client extension o módulo OSGi para llamar a un ERP? | agente `liferay-architect`; modo Estándar; orden de preferencia; alternativa simple | |
| 11 | Evalúa la arquitectura de este workspace | `liferay-architecture-assessment`; lee ficheros, cita rutas, no escribe | |
| 12 | Redacta un ADR para sacar la integración con SAP fuera de la JVM del portal | `liferay-architect` usa `liferay-solution-architecture` y `templates/adr-template.md` | |
| 13 | `/liferay:liferay-review` con cambios pendientes | `liferay-architect` solo lectura; hallazgos con `fichero:línea` | |
| 14 | Configura las convenciones de este proyecto | `liferay-project-guidelines`; escribe `## Convenciones Liferay` en `CLAUDE.md`, enseña diff | |
| 15 | Con `tests: required`: crea `OrderHelperImpl` (`@Component`) | crea `OrderHelperImplTest.java` en `src/test/java` (mismo paquete); el hook Stop no bloquea; ejecuta `verify` | |
| 16 | Con `tests: required`, crear un `@Component` y cortar antes del test (simulado) | el hook Stop bloquea (exit 2) con la lista; `*PortletKeys`, `*Configuration` (`@Meta.OCD`), interfaces y código generado de Service Builder no cuentan; con un test en un módulo `-test`, pasa | |
| 17 | Con `format: source-formatter`: edita un `.java` en `modules/x` | el hook ejecuta `gradlew :modules:x:formatSource`; si falla, devuelve el error (exit 2) | |
| 18 | Sin `format` en `CLAUDE.md`: edita un `.java` | el hook `format-lint` no hace nada (exit 0) | |
| 19 | El módulo `acme-orders-web` no pasa a `STARTED` | `liferay-config-operations` (`references/troubleshooting.md`); Gogo Shell, bundles sin resolver, logs | |
| 20 | Con `product: dxp-7.4.13.u90`: crea un módulo | avisa de que el mínimo es 2025.Q1 y pregunta antes de seguir | |

Criterios transversales: informa qué verificó y qué no; no propone lo que el modelo de despliegue no admite; no mezcla APIs de versiones distintas; no usa funciones beta sin avisar; `liferay-architect` nunca edita ficheros; ningún agente hace operaciones Git que modifiquen el repositorio.
