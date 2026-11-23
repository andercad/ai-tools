# Prompts de prueba (manuales, en un proyecto NestJS de ejemplo)

Instala el plugin y lanza cada prompt en sesión limpia. Marca el resultado.

| # | Prompt | Debe cargar / hacer | Resultado |
|---|---|---|---|
| 1 | Crea un CRUD de `products` con TypeORM | `nestjs-modules-services`, `nestjs-api`, `nestjs-persistence`; DTOs validados, DTO de respuesta, migración, sin `any`; ejecuta build/lint | |
| 2 | Guardamos el JWT secret en el `.env` del repo, ¿vale? | `nestjs-security`/`nestjs-workspace`; lo desaconseja; `ConfigService` y secretos fuera del repo | |
| 3 | Añade `GET /orders/:id` | autorización por recurso (el usuario solo ve lo suyo), `ParseUUIDPipe`; no confía en el UUID | |
| 4 | Endpoint de actualización de perfil que hace `repo.save(body)` | detecta asignación masiva y copia campo a campo desde el DTO | |
| 5 | Sube de avatar de usuario | `nestjs-security`; límite de tamaño, tipo real, nombre generado, sin path traversal | |
| 6 | Resuelve el N+1 del resolver `orders` | `nestjs-graphql`; DataLoader por petición | |
| 7 | Consumidor de `order.created` que envía un email | `nestjs-microservices`; idempotente, ack tras procesar, reintentos/DLQ, timeout | |
| 8 | ¿Microservicios o monolito modular para 3 equipos? | agente `nestjs-architect`; modo Estándar, alternativa simple, drivers | |
| 9 | Evalúa la arquitectura de este repo | `nestjs-architecture-assessment`; lee ficheros, cita rutas, no escribe | |
| 10 | Planifica el upgrade a la última versión mayor de Nest | `nestjs-modernization-governance`; comprueba versión actual, plantilla de ADR | |
| 11 | Arregla el test roto de `X.service.ts` | `nestjs-testing-quality`; ejecuta el test antes de informar | |
| 12 | `/nestjs:nestjs-review` con cambios pendientes | `nestjs-architect` solo lectura; hallazgos con `fichero:línea` | |
| 13 | Configura las convenciones de este proyecto | `nestjs-project-guidelines`; escribe `## Convenciones NestJS` en `CLAUDE.md`, enseña diff | |
| 14 | Con `tests: required`: crea `OrdersService` | crea `orders.service.spec.ts`; el hook Stop no bloquea; ejecuta `verify` | |
| 15 | Con `tests: required`, pedir un servicio y cortar antes del spec (simulado) | el hook Stop bloquea con la lista de ficheros sin spec; `*.module.ts`, `*.dto.ts` y `*.entity.ts` no cuentan | |
| 16 | Con `e2e: required`: añade `POST /orders` | crea `test/orders.e2e-spec.ts` en el mismo paso | |
| 17 | En monorepo Nx: añade una librería compartida con el frontend | `nestjs-workspace`; contratos de solo tipos, import por entrada pública, `nx affected` | |
| 18 | `/spec` para una feature y luego `/spec-impl` (instalados aparte) | la spec incluye diseño de clases, contrato de API y plan de tests; la implementación aplica SOLID previo, crea specs en el mismo paso y ejecuta `verify` | |

Criterios transversales: informa qué verificó y qué no; no usa APIs experimentales sin avisar; `nestjs-architect` nunca edita ficheros.
