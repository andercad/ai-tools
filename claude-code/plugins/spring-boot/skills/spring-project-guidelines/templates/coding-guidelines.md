# Coding Guidelines Spring Boot — Plantilla de proyecto

Convenciones **específicas de un proyecto** para añadir al `CLAUDE.md` (tras el bloque `## Convenciones Spring Boot`). Rellena cada sección; elimina ejemplos y secciones que no apliquen.

---

## Cliente y contexto

**Qué necesita**: para quién es el proyecto, qué hace la aplicación y si maneja datos sensibles (personales, sanitarios, financieros). Indica restricciones de tratamiento de forma accionable.

**Ejemplo**:
- **Cliente**: ACME Seguros
- **Aplicación**: API de gestión de pólizas para agentes comerciales
- **Dominio sensible**: datos personales y bancarios. No los registres en logs; cífralos en reposo; no los incluyas en URLs.

---

## Estructura de paquetes

**Qué necesita**: organización vigente de `src/main/java` (paquete raíz, funcionalidades, `common`) y, en multi-módulo, el propósito de cada módulo. Por defecto, paquetes por funcionalidad.

**Ejemplo**:

| Paquete / módulo | Propósito |
|---|---|
| `com.acme.policies.policy` | Funcionalidad de pólizas (controller, service, repository, entity, dto) |
| `com.acme.policies.claim` | Funcionalidad de siniestros |
| `com.acme.policies.common` | Configuración global, errores, seguridad, utilidades web |

Al crear una funcionalidad, usa un paquete nuevo bajo el raíz; ninguna funcionalidad usa el repositorio o la entidad de otra.

---

## Base de datos y persistencia

**Qué necesita**: motor, tecnología (Spring Data JPA, JDBC, MongoDB...), herramienta de migraciones, convenciones de nombres y política de borrado.

**Ejemplo**: PostgreSQL con Spring Data JPA; migraciones Flyway en `db/migration`, `ddl-auto: validate`; `open-in-view` desactivado; borrado lógico con `deleted_at`; ids UUID.

---

## Autenticación y autorización

**Qué necesita**: mecanismo (OAuth2 Resource Server con JWT, OIDC/Entra ID, sesión, API keys), endpoints públicos, modelo de roles/permisos y reglas de autorización por recurso.

**Ejemplo**: JWT validado contra Entra ID (Resource Server); públicos solo `/actuator/health` y `/auth/login`; roles `ADMIN|AGENT`; un agente solo ve sus pólizas (`ownerId`) mediante `@PreAuthorize` en el servicio.

---

## Formato de errores y logging

**Qué necesita**: formato único de error de la API, logger usado, campos obligatorios (id de correlación) y datos que nunca se registran.

**Ejemplo**: `ProblemDetail` (RFC 9457) con propiedad `correlationId`; SLF4J con logs JSON y cabecera `X-Correlation-Id`; nunca tokens, contraseñas ni PII.

---

## Documentación de API y contratos

**Qué necesita**: si se publica OpenAPI y dónde, política de versionado y, si existe, la librería o módulo de contratos compartidos.

**Ejemplo**: springdoc en `/swagger-ui.html` solo fuera de producción; versionado por ruta (`/api/v1`); contratos en el módulo `api-contracts`.

---

## Librerías y herramientas

**Qué necesita**: uso de Lombok, MapStruct, Testcontainers, Spotless/Checkstyle, JaCoCo y versiones de Java y Spring Boot objetivo.

**Ejemplo**: Java 21, Spring Boot 3.5; sin Lombok (records y constructores explícitos); MapStruct con `unmappedTargetPolicy = ERROR`; Spotless con `google-java-format`; JaCoCo con umbral del 80 %.

---

## Documentación y estilo de clases

**Qué necesita**: reglas de Javadoc y orden de miembros en clases.

**Ejemplo**: Javadoc en API pública, nada sobre lo evidente. Orden: constantes, logger, dependencias `final`, constructor, métodos públicos de lectura, métodos públicos de escritura, métodos privados.
