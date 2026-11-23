---
name: liferay-project-guidelines
description: Liferay DXP. Crea o actualiza en el CLAUDE.md del proyecto el bloque "Convenciones Liferay" (política de tests, docs, modelo de despliegue, versión, paquete base, formato, verify) y las reglas de implementación y de specs que aplican en cualquier flujo, incluido /spec y /spec-impl. Usar cuando el proyecto no tiene ese bloque, el usuario pide configurar los agentes Liferay para su proyecto o cambiar la política de calidad. No usar para implementar código.
---

# Política del proyecto → `CLAUDE.md`

Claude Code carga el `CLAUDE.md` en cada sesión y en cualquier flujo (también `/spec` y `/spec-impl`); un plugin no puede aportarlo. Por eso las reglas van ahí. El agente `liferay-dev` y los hooks leen el bloque `## Convenciones Liferay`.

## Bloque a escribir (adapta las claves; borra comentarios)

````markdown
## Convenciones Liferay
- tests: required | optional | none      # *Test.java por componente con lógica (MVC command, helper, listener, impl, contributor, recurso REST)
- it: required | optional | none         # Arquillian (testIntegration) por servicio o endpoint que requiera un Liferay real
- docs: javadoc | none                   # Javadoc en clases y métodos públicos
- deployment: saas | paas | self-hosted-docker | self-hosted-k8s | self-hosted-bundle
- product: dxp-2025.q1.0                 # de liferay.workspace.product en gradle.properties
- base-package: com.acme.portal          # paquete base del proyecto (y de APIs genéricos si los hay)
- format: source-formatter | none        # si source-formatter, un hook ejecuta formatSource del módulo editado
- verify: ./gradlew build                # o ./gradlew :modules:<modulo>:build

### Al implementar código Liferay
Aplica siempre, también al implementar una spec:
1. Elige el mecanismo con el orden de `liferay-extension-model` (configuración → Objects/contenido → client extensions → OSGi → overrides) y justifica los saltos. Respeta lo que admite el modelo de `deployment`.
2. Solo APIs de la versión `product`; consulta learn.liferay.com ante la duda. Sin funciones beta/experimentales.
3. Permisos en toda operación sobre datos; sin SQL directo; sin secretos en el repositorio; valores por nombre o clave, nunca por ID.
4. Componentes DS con `@Reference`; sin `*ServiceUtil`; helpers `Helper`/`HelperImpl`; `Log` de Liferay.
5. `docs: javadoc` → Javadoc conciso en API pública, nada sobre lo evidente.
6. `tests: required` → crea el `*Test.java` junto a cada pieza nueva o modificada, en el mismo paso. `it: required` → test de integración por servicio o endpoint que lo necesite.
7. Antes de dar un paso por terminado, ejecuta `verify` y comprueba en el log que los módulos pasan a `STARTED`. Informa qué verificaste y qué no.

### Al redactar specs de este proyecto
Además de lo que pida la plantilla de `/spec`, cada spec Liferay incluye:
- **Mecanismo de extensión** elegido, alternativa descartada y compatibilidad con `deployment`.
- **Diseño de módulos**: nombre, tipo, Symbolic Name y dependencias (o client extension / Object con ERC).
- **Permisos y datos**: recursos protegidos, roles, ámbito (company/site).
- **Plan de tests** por pieza si `tests` ≠ none, y de integración si `it` ≠ none, en el mismo paso del plan que la pieza.
- **Comando `verify`** como criterio de aceptación final.
````

Defaults si falta una clave: `tests: none`, `it: none`, `docs: javadoc`, `format: none`, `product` y `verify` deducibles de `gradle.properties` y del wrapper (`gradlew`).

## Pasos
1. Lee el `CLAUDE.md`; si ya existe el bloque, actualízalo, no lo dupliques.
2. Deduce valores del repo: `gradle.properties` (`liferay.workspace.product`), `settings.gradle`, estructura de `modules/` y `client-extensions/`, `LCP.json`/`Dockerfile`/Helm (modelo de despliegue), paquete base de los módulos existentes, uso de Source Formatter.
3. Pregunta solo lo no deducible (máx. 3): política de tests, modelo de despliegue si no es concluyente y si se quiere formato automático.
4. Escribe el bloque con los valores reales; elimina las líneas que no apliquen. Añade, solo si aporta, carpetas del workspace, idiomas, librerías y excepciones documentadas, con [templates/coding-guidelines.md](templates/coding-guidelines.md) como guía.
5. Muestra el diff; no inventes datos de cliente ni de dominio.
