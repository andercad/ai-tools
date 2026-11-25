---
name: spring-project-guidelines
description: 'Backend Spring Boot. Crea o actualiza en el CLAUDE.md del proyecto el bloque "Convenciones Spring Boot" (política de tests unitarios y de integración, docs, API docs, build, workspace, verify) y las reglas de implementación y de specs que aplican en cualquier flujo, incluido /spec y /spec-impl. Usar cuando el proyecto no tiene ese bloque, el usuario pide configurar los agentes Spring Boot para su proyecto o cambiar la política de calidad. No usar para implementar código.'
---

# Política del proyecto → `CLAUDE.md`

Claude Code carga el `CLAUDE.md` en cada sesión y en cualquier flujo (también `/spec` y `/spec-impl`); un plugin no puede aportarlo. Por eso las reglas van ahí. El agente `spring-boot-dev` y el hook de parada leen el bloque `## Convenciones Spring Boot`.

## Bloque a escribir (adapta las claves; borra comentarios)

````markdown
## Convenciones Spring Boot
- tests: required | optional | none      # *Test.java por servicio, controlador, componente, listener, advice nuevos
- it: required | optional | none         # *IT.java (Testcontainers / @SpringBootTest) por endpoint o repositorio con consultas propias
- coverage: 80                           # JaCoCo, opcional
- docs: javadoc | none                   # Javadoc en API pública (clases, métodos públicos)
- api-docs: springdoc | none             # anotaciones springdoc-openapi en controladores y DTOs
- build: maven | gradle
- workspace: single | multi-module
- verify: ./mvnw verify                  # o ./gradlew build

### Al implementar código Spring Boot
Aplica siempre, también al implementar una spec:
1. Antes de escribir una pieza >30 líneas o que toque varias clases, decide en 5–8 líneas piezas, responsabilidad única, dependencias y extensión (SOLID; skill `spring-solid`). Sin capas ni abstracciones prematuras. No generes para luego rehacer.
2. Controladores, controladores GraphQL y listeners sin lógica de negocio; inyección solo por constructor; toda entrada validada con DTOs y `@Valid`; no expongas entidades.
3. Seguridad desde el primer borrador (skill `spring-security`): autorización por recurso, sin asignación masiva, consultas parametrizadas, sin secretos en el repo.
4. `docs: javadoc` → Javadoc conciso en API pública, nada sobre lo evidente.
5. `tests: required` → crea el `*Test.java` junto a cada pieza nueva o modificada, en el mismo paso, no en uno posterior. `it: required` → `*IT.java` por endpoint o repositorio con consultas propias.
6. Solo APIs estables de la versión instalada de Spring Boot; ante la duda, consulta docs.spring.io.
7. Antes de dar un paso por terminado, ejecuta `verify` y corrige. Informa qué verificaste y qué no.

### Al redactar specs de este proyecto
Además de lo que pida la plantilla de `/spec`, cada spec Spring Boot incluye:
- **Diseño de clases**: paquetes, piezas, responsabilidad de cada una y dependencias (SOLID).
- **Contrato de API**: rutas, DTOs de entrada/salida, códigos de estado y errores, y reglas de autorización por recurso.
- **Plan de tests** por pieza (casos y límites) si `tests` ≠ none, y de integración si `it` ≠ none, en el mismo paso del plan que la pieza.
- **Comando `verify`** como criterio de aceptación final.
````

Defaults si falta una clave: `tests: none`, `it: none`, `docs: javadoc`, `api-docs: springdoc` si `springdoc-openapi` está en el build, `build` y `verify` deducibles de `pom.xml`/`build.gradle(.kts)` y del wrapper (`mvnw`/`gradlew`).

## Pasos
1. Lee el `CLAUDE.md`; si ya existe el bloque, actualízalo, no lo dupliques.
2. Deduce valores del repo: `pom.xml` o `build.gradle(.kts)` (versión de Boot y Java, JaCoCo, `springdoc-openapi`, Lombok, MapStruct, Flyway/Liquibase), `application.yml`, módulos (`workspace`), wrapper y estructura de `src/`.
3. Pregunta solo lo no deducible (máx. 3): política de tests unitarios y de integración, documentación de API y si hay normativa o datos sensibles.
4. Escribe el bloque con los valores reales; elimina las líneas que no apliquen. Añade, solo si aporta, estructura de paquetes, base de datos, autenticación y formato de errores con [templates/coding-guidelines.md](templates/coding-guidelines.md) como guía.
5. Muestra el diff; no inventes datos de cliente ni de dominio.
