# Preparación para modularizar o extraer servicios

Úsalo antes de recomendar monolito modular, extracción de servicios o microservicios. Puntúa de 0 a 2 (0 = no, 1 = parcialmente, 2 = sí, con evidencia).

## A. Drivers para separar el despliegue
| # | Pregunta | 0-2 | Evidencia |
|---|---|---|---|
| A1 | ¿Hay partes con necesidades de escalado medidas muy distintas? | | |
| A2 | ¿Hay equipos que se bloquean entre sí al desplegar? | | |
| A3 | ¿Hay requisitos de aislamiento (seguridad, fallos, regulación) entre partes? | | |
| A4 | ¿Hay SLO o ritmos de cambio claramente distintos? | | |
| A5 | ¿Los bounded contexts son estables y conocidos? | | |

## B. Límites dentro del monolito
| # | Pregunta | 0-2 | Evidencia |
|---|---|---|---|
| B1 | Paquetes de primer nivel por dominio, sin ciclos | | |
| B2 | `ApplicationModules.of(...).verify()` o reglas ArchUnit en CI y en verde | | |
| B3 | Cada módulo es dueño de sus tablas; sin joins ni repositorios cruzados | | |
| B4 | Comunicación entre módulos por su API pública o por eventos de aplicación | | |
| B5 | Pruebas de módulo aisladas (`@ApplicationModuleTest` o equivalente) | | |

## C. Capacidades para operar servicios
| # | Pregunta | 0-2 | Evidencia |
|---|---|---|---|
| C1 | CI/CD por servicio con despliegue y rollback seguros | | |
| C2 | Trazas distribuidas, logs correlados y métricas por servicio | | |
| C3 | Experiencia en outbox, idempotencia y sagas | | |
| C4 | Plataforma de ejecución y mensajería gestionada o con equipo propio | | |
| C5 | Pruebas de contrato y gestión de versiones de APIs y eventos | | |

## Interpretación
- **A < 4**: sin drivers suficientes. Monolito modular y refuerzo de los límites (B).
- **A ≥ 4 y B < 6**: primero límites internos; extraer ahora produciría un monolito distribuido.
- **A ≥ 4, B ≥ 6 y C < 6**: construir las capacidades C antes de extraer.
- **A ≥ 4, B ≥ 6 y C ≥ 6**: extracción incremental (strangler) del contexto con más driver y menos acoplamiento de datos.

Es una heurística: pesa la evidencia, no solo la suma.

## Señales de monolito distribuido
- Servicios que comparten base de datos o tablas.
- Peticiones de usuario que atraviesan más de tres servicios de forma síncrona.
- Cambios habituales que obligan a desplegar varios servicios a la vez.
- Servicios sin equipo dueño.

## Orden sugerido
1. Módulos verificados en CI y datos por módulo.
2. Eventos de aplicación entre módulos donde sobra acoplamiento temporal (con registro de publicación si se usa Spring Modulith).
3. Extracción del primer contexto con su base de datos, outbox y contrato versionado.
4. Medición de lead time, incidentes y coste antes de extraer el siguiente.
