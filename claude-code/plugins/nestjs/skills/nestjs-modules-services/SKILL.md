---
name: nestjs-modules-services
description: 'Módulos, servicios y convenciones de código NestJS. Usar al crear o modificar un módulo de dominio, forRoot/forRootAsync/forFeature, imports/exports, dependencias circulares, servicios con lógica de negocio, mapeo entidad a DTO, transacciones de caso de uso, scopes de providers, o al decidir estructura de carpetas, naming, orden de miembros, barrels y alias. No usar para controladores o DTOs (nestjs-api) ni para elegir entre monolito modular y microservicios (agente nestjs-architect).'
---

# Módulos, servicios y convenciones

## Reglas clave
- Un módulo por dominio; exporta solo lo que otros necesitan; sin módulos `shared` cajón de sastre.
- Inyección **solo por constructor**; nunca `new` sobre providers.
- Los servicios contienen el negocio; controladores, resolvers y handlers solo delegan.
- Mapea entidad → DTO en el servicio; nunca devuelvas entidades.
- La transacción del caso de uso vive en el servicio, no en el controlador.
- Errores de negocio con excepciones de dominio/HTTP, sin `catch` vacío.
- Ficheros kebab-case, sin prefijo `I`, imports por alias de `tsconfig`, barrels sin ciclos.

## Referencias
| Tema | Fichero |
|---|---|
| Módulos, módulos dinámicos, ciclos | [modules.md](references/modules.md) |
| Servicios, scopes, eventos, mapeo | [services.md](references/services.md) |
| Estructura, naming, orden de miembros, JSDoc | [conventions.md](references/conventions.md) |
