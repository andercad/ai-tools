---
name: spring-api
description: Backend Spring Boot. Capa HTTP REST. Usar al crear endpoints, controladores, rutas, códigos de estado, paginación, OpenAPI con springdoc, DTOs y records con Bean Validation y Jackson, @Valid, @RestControllerAdvice, ProblemDetail, filtros, interceptores, AOP y ResponseBodyAdvice. No usar para GraphQL (spring-graphql), mensajería (spring-integration) ni autenticación (spring-security).
---

# API REST: controladores, DTOs, errores y pipeline

## Reglas clave
- Controladores sin lógica de negocio: parsean, delegan en el servicio y devuelven DTOs; un controlador por recurso; códigos de estado explícitos.
- Toda entrada (body, query, path) pasa por DTOs (records) validados con `@Valid`/`@Validated`; nunca enlaces entidades JPA a la petición ni las expongas en la respuesta.
- Documenta con springdoc si `api-docs: springdoc`.
- Un formato de error único: `ProblemDetail` (RFC 9457) desde un `@RestControllerAdvice`; sin stack traces, mensajes de BD ni configuración en las respuestas; nunca `catch` vacío.
- Filtros para preocupaciones HTTP de bajo nivel, interceptores para MVC, AOP solo para preocupaciones transversales reales; un envoltorio global de respuesta solo si el proyecto lo define.
- Las excepciones de un filtro no llegan al `@RestControllerAdvice`: escribe el error en el propio filtro con el mismo formato.

## Referencias
| Tema | Fichero |
|---|---|
| Rutas, códigos, paginación, OpenAPI | [controllers.md](references/controllers.md) |
| DTOs, records, Bean Validation, Jackson | [dto-validation.md](references/dto-validation.md) |
| Excepciones, `@RestControllerAdvice`, `ProblemDetail` | [error-handling.md](references/error-handling.md) |
| Filtros, interceptores, AOP, `ResponseBodyAdvice` | [web-pipeline.md](references/web-pipeline.md) |
