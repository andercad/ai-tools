---
name: spring-graphql
description: 'Backend Spring Boot. GraphQL con Spring for GraphQL. Usar al definir esquemas .graphqls, @QueryMapping, @MutationMapping, @SchemaMapping, @BatchMapping, paginación por cursor, errores GraphQL, seguridad por campo, limitación de profundidad y pruebas con GraphQlTester. No usar para API REST (spring-api) ni mensajería (spring-integration).'
---

# GraphQL (Spring for GraphQL)

## Reglas clave
- Controladores GraphQL sin lógica de negocio: delegan en los mismos servicios que usa REST; no expongas entidades JPA como tipos.
- Resuelve el N+1 con `@BatchMapping`, no con consultas por campo.
- Autorización en servicios (`@PreAuthorize`) y por recurso, no solo en la ruta `/graphql`.
- Limita profundidad y complejidad de consultas; introspección y GraphiQL desactivados en producción.
- Errores traducidos de forma controlada, sin stack traces ni detalles internos.
- Pagina listas grandes (cursor).

## Referencias
| Tema | Fichero |
|---|---|
| Esquema, mapeos, batch, errores, seguridad, paginación, tests | [graphql.md](references/graphql.md) |
