---
name: nestjs-graphql
description: 'GraphQL con NestJS (@nestjs/graphql). Usar al exponer datos con GraphQL, crear o modificar resolvers, tipos, inputs, mutations, subscriptions, configurar GraphQLModule (code-first o schema-first, Apollo o Mercurius), resolver N+1 con DataLoader, límites de profundidad y complejidad, paginación o autorización en GraphQL. No usar para REST (nestjs-api) ni para decidir REST frente a GraphQL (skill nestjs-api-integration).'
---

# GraphQL

## Reglas clave
- Detecta driver y enfoque (code-first/schema-first) antes de escribir.
- Los resolvers solo delegan en servicios; no expongas entidades: usa modelos/`ObjectType`.
- N+1 con DataLoader por petición; límites de profundidad y complejidad; introspección solo fuera de producción.
- Autenticación y autorización también en resolvers y `@ResolveField`; los guards globales deben soportar el contexto GraphQL.
- Entradas validadas con `InputType`/`ArgsType` y `ValidationPipe`.

## Referencias
- [graphql.md](references/graphql.md): resolvers, tipos, DataLoader, seguridad, errores, paginación, evolución del esquema y subscriptions.
