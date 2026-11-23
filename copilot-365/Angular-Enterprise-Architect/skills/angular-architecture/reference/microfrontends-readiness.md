# Preparación para monorepo o microfrontends

Puntúa de 0 a 2 (0 = no, 1 = parcialmente, 2 = sí, con evidencia) antes de recomendar dividir el frontend.

## A. Drivers
| # | Pregunta | 0-2 | Evidencia |
|---|---|---|---|
| A1 | ¿Hay equipos autónomos que se bloquean entre sí al publicar? | | |
| A2 | ¿Necesitan ciclos de release independientes de verdad, no solo deseables? | | |
| A3 | ¿Hay que integrar aplicaciones en un host heterogéneo (por ejemplo, Liferay u otro portal)? | | |
| A4 | ¿Conviven tecnologías o versiones que no pueden alinearse a corto plazo? | | |
| A5 | ¿Los dominios del producto son estables y tienen dueño claro? | | |

## B. Capacidades
| # | Pregunta | 0-2 | Evidencia |
|---|---|---|---|
| B1 | Design system versionado y adoptado por todos los equipos | | |
| B2 | Política de dependencias compartidas (versión de Angular, librerías) y quién la decide | | |
| B3 | Pipeline por aplicación con despliegue y rollback independientes | | |
| B4 | Pruebas de integración de la composición y observabilidad en cliente por aplicación | | |
| B5 | Presupuesto de rendimiento para la página compuesta | | |

## Interpretación
- **A < 4**: aplicación única por features con límites verificados en CI; si varias aplicaciones comparten código, monorepo con librerías.
- **A ≥ 4 y B < 6**: monorepo con límites estrictos mientras se construyen las capacidades B.
- **A ≥ 4 y B ≥ 6**: microfrontends, empezando por el dominio con más driver y menos dependencias compartidas.

Pesa la evidencia, no solo la suma.

## Mecanismos de composición
| Mecanismo | Ventaja | Coste |
|---|---|---|
| Federación de módulos (en build o en runtime) | Comparte dependencias; integración nativa entre aplicaciones Angular | Acoplamiento de versiones y configuración |
| Web Components (Angular Elements) | Independiente del host; encaja con Liferay | Runtime duplicado si no se comparte; estilos |
| Composición por rutas o iframes | Aislamiento total | UX, SSO y rendimiento |

Verifica herramientas y soporte en la versión instalada antes de recomendar una.

## Señales de alerta
- Cambios habituales que obligan a publicar varias aplicaciones a la vez.
- Dependencias compartidas en versiones distintas sin política.
- Inconsistencias de UX entre aplicaciones.
- Páginas que cargan varias copias del runtime de Angular.
