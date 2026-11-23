---
name: nestjs-modularity-domain
description: 'Asesoría arquitectónica sobre modularidad, dominio, arquitectura hexagonal, monorepos y microservicios en NestJS. Usar cuando se pida decidir entre capas, puertos y adaptadores, monolito modular, varias aplicaciones o microservicios; definir módulos, bounded contexts, providers, contratos, ownership de datos o límites en Nest CLI/Nx; o resolver dependencias circulares, forwardRef y módulos shared. No usar como generador de código por defecto.'
---

# Modularidad, dominio y arquitectura hexagonal

## Objetivo
Decidir cómo se parte el sistema (capas, monolito modular, hexagonal, varias apps, microservicios) y definir bounded contexts, módulos NestJS, dependencias permitidas, providers exportados, ownership de datos y contratos.

## Árbol de decisión (de menos a más complejidad)
1. **Capas simples (controller, service, repository)**: CRUD, equipo pequeño, poca lógica de negocio.
2. **Monolito modular**: un despliegue, módulos por bounded context con API pública explícita. Es el punto de partida por defecto para sistemas medianos.
3. **Hexagonal dentro de los módulos con lógica compleja**: solo donde haya varias entradas/salidas o reglas de negocio ricas.
4. **Varias aplicaciones (Nest monorepo, Nx)**: cuando hay ciclos de despliegue o escalado distintos, pero con código y base de datos compartidos de forma controlada.
5. **Microservicios**: solo con drivers verificables (ver abajo).
Sube de nivel solo cuando un driver medido lo justifique. Documenta siempre por qué no basta el nivel anterior.

## Cuándo compensa hexagonal
Recomiéndala con lógica de negocio relevante, varias entradas (REST, GraphQL, mensajes, jobs), varias salidas (ORM, APIs, brokers), necesidad de probar sin NestJS o sustitución real de integraciones. Para CRUD pequeño, explica el coste: mapeos, interfaces y clases adicionales, y más ficheros por cambio.

## Modelo hexagonal
- **Dominio**: entidades, value objects, invariantes y eventos sin `@nestjs/common`, ORM, GraphQL ni transporte.
- **Aplicación**: casos de uso y puertos de entrada. No recibe `Request`, DTO GraphQL ni entidades ORM.
- **Puertos de salida**: contratos para repositorios, reloj, identidad, almacenamiento, publicación e integraciones.
- **Adaptadores de entrada**: controllers REST, resolvers GraphQL, handlers de mensajes, gateways WebSocket y cron. Validan, mapean y llaman a casos de uso.
- **Adaptadores de salida**: TypeORM/Prisma, cliente HTTP, caché, `ClientProxy` o SDK del broker.
- **Ensamblado**: los módulos NestJS registran implementaciones con tokens de inyección. El dominio no conoce el contenedor.

```text
orders/
  domain/
  application/{port/in, port/out, usecase}
  adapters/{in/rest, in/graphql, in/messaging, out/persistence, out/http, out/messaging}
  orders.module.ts
```
TypeScript borra las interfaces en runtime. Los puertos de salida necesitan un símbolo, una constante string o una clase abstracta como token. No crees una interfaz por servicio si no hay una frontera real.

## Módulos NestJS: reglas prácticas
- Un módulo por bounded context. Exporta solo lo que forma su API pública (casos de uso, no repositorios).
- Evita `SharedModule` que acumula negocio. Lo compartido debe ser técnico y estable (logging, config, utilidades) o un contrato.
- `forwardRef` y las dependencias circulares son síntoma de fronteras mal trazadas. Resuélvelas con eventos de dominio, inversión de dependencia o moviendo la responsabilidad.
- `@Global()` solo para infraestructura transversal. `Scope.REQUEST` se propaga por la cadena de inyección y penaliza el rendimiento, así que considera `AsyncLocalStorage`/nestjs-cls para el contexto de petición.
- Los módulos dinámicos (`forRoot`/`forRootAsync`) son para librerías configurables, no para cada feature.

## Microservicios
Drivers aceptables: despliegue o escalado independiente real, ownership por equipos autónomos, aislamiento de fallos o seguridad, SLO diferenciados, tecnologías distintas justificadas. "Está de moda" o "es más limpio" no son drivers.
Exige: datos propios por servicio (sin BD compartida), contratos versionados de eventos/comandos, idempotencia, outbox, timeouts, trazas distribuidas, estrategia de pruebas de contrato y plan de rollback. Evita cadenas síncronas largas y el "monolito distribuido". Compáralos siempre con monolito modular y con varias aplicaciones.

## Monorepo
Nest CLI monorepo para pocas apps y librerías compartidas. Nx cuando se necesiten grafo de proyectos, caché de builds, `affected` y reglas de límites (`@nx/enforce-module-boundaries`). Define etiquetas por dominio y capa, y prohíbe importaciones fuera de la API pública de cada librería.

## Verificación
- Tests unitarios de dominio y casos de uso sin `TestingModule` cuando sea viable.
- Tests de contrato entre puertos y adaptadores.
- Reglas automatizadas de límites y ciclos (ESLint boundaries, Nx, Dependency Cruiser, madge) en CI.
- Integración real para ORM, broker y clientes externos.

## Salida
Para decidir si dividir en microservicios, aplica la matriz de `reference/microservices-readiness.md` y muestra la puntuación con su evidencia.
Límites y módulos, puertos/adaptadores y tokens, diagrama de dependencias, alternativa más simple, trade-offs, pruebas de arquitectura, migración incremental (strangler/extracción por módulo) y ADR.

## Autoevaluación
El dominio no importa NestJS/ORM/transporte. Los módulos solo ensamblan. Los puertos no son abstracciones especulativas. Los microservicios tienen drivers verificables y se comparó con el monolito modular.
