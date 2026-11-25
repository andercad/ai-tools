---
name: nestjs-api
description: 'Capa HTTP de NestJS. Usar al crear endpoints REST, controladores, rutas, códigos de estado, paginación, documentación OpenAPI/Swagger, DTOs de entrada y salida con class-validator, ValidationPipe, serialización, interceptores, pipes, middleware, filtros de excepciones y formato de error. No usar para GraphQL (nestjs-graphql), mensajería (nestjs-microservices) ni autenticación (nestjs-security).'
---

# API REST: controladores, DTOs, pipeline y errores

## Reglas clave
- Controladores sin lógica de negocio: parsean, delegan en el servicio y devuelven DTOs.
- Toda entrada (body, query, params) pasa por DTOs; `ValidationPipe` global con `whitelist` y `forbidNonWhitelisted`; sin `any` en DTOs.
- `ParseUUIDPipe` para ids públicos; códigos de estado explícitos; documenta con `@nestjs/swagger` si `api-docs: swagger`.
- Orden de ejecución: middleware → guards → interceptores → pipes → handler → interceptores → filtros.
- Un formato de error único; no expongas stack traces, mensajes de BD ni variables de entorno.
- Guards, interceptores y filtros globales deben funcionar en todos los contextos del proyecto (HTTP, GraphQL, microservicios).

## Referencias
| Tema | Fichero |
|---|---|
| Rutas, códigos, paginación, Swagger | [controllers.md](references/controllers.md) |
| DTOs, validación, transformación, serialización | [dto-validation.md](references/dto-validation.md) |
| Middleware, guards, interceptores, pipes | [request-pipeline.md](references/request-pipeline.md) |
| Excepciones, filtros, formato de error | [error-handling.md](references/error-handling.md) |
