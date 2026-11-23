# Evaluación de preparación para microservicios

Usa esta matriz antes de recomendar dividir un sistema. Puntúa cada pregunta de 0 a 2 (0 = no, 1 = parcialmente, 2 = sí, con evidencia).

## A. Drivers (¿hay motivo?)
| # | Pregunta | 0-2 | Evidencia |
|---|---|---|---|
| A1 | ¿Hay partes con necesidades de escalado medidas muy distintas? | | |
| A2 | ¿Hay equipos autónomos que se bloquean entre sí al desplegar? | | |
| A3 | ¿Hay requisitos de aislamiento (seguridad, fallos, cumplimiento) entre partes? | | |
| A4 | ¿Hay SLO o ritmos de cambio claramente diferenciados? | | |
| A5 | ¿Las fronteras de dominio son estables y conocidas (bounded contexts claros)? | | |

## B. Capacidades (¿podemos asumirlo?)
| # | Pregunta | 0-2 | Evidencia |
|---|---|---|---|
| B1 | CI/CD automatizado por servicio con despliegue y rollback seguros | | |
| B2 | Observabilidad distribuida (trazas, logs correlados, métricas) | | |
| B3 | Experiencia en consistencia eventual, outbox, idempotencia, sagas | | |
| B4 | Plataforma de ejecución y de mensajería gestionada o con equipo propio | | |
| B5 | Pruebas de contrato y gestión de versiones de API/eventos | | |

## Interpretación
- **A < 4**: no hay drivers suficientes. Recomienda monolito modular con límites reforzados.
- **A ≥ 4 y B < 6**: drivers reales pero falta capacidad. Monolito modular o varias aplicaciones, y plan para construir las capacidades B antes de extraer.
- **A ≥ 4 y B ≥ 6**: extracción incremental (strangler), empezando por el contexto con mayor driver y menor acoplamiento de datos.
Es una heurística: cuenta la evidencia y no solo la puntuación.

## Señales de alerta
- Varios servicios comparten tablas o base de datos.
- Una petición de usuario atraviesa más de 3 servicios de forma síncrona.
- Los cambios funcionales habituales requieren desplegar varios servicios a la vez.
- No se sabe qué equipo es dueño de cada servicio.
Cualquiera de ellas sugiere un monolito distribuido: revisa fronteras antes de seguir dividiendo.

## Orden de extracción sugerido
1. Reforzar límites dentro del monolito (API pública por módulo, reglas de dependencias, datos por módulo).
2. Comunicar módulos por eventos internos donde haya acoplamiento temporal innecesario.
3. Extraer el primer contexto con su propia base de datos, outbox y contrato versionado.
4. Medir (lead time, incidentes, coste) antes de extraer el siguiente.
