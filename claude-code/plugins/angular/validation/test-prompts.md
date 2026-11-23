# Prompts de prueba (manuales, en un proyecto Angular de ejemplo)

Instala el plugin y lanza cada prompt en sesión limpia. Marca el resultado.

| # | Prompt | Debe cargar / hacer | Resultado |
|---|---|---|---|
| 1 | Crea un componente de tarjeta de usuario con input `user` | skill `angular-components`; `input()`, OnPush según versión; ejecuta build/lint | |
| 2 | Añade un buscador con autocompletado contra `/api/items` | `angular-data`; debounce, cancelación; sin `any` | |
| 3 | Guardamos el JWT en localStorage, ¿está bien? | `angular-security`; lo desaconseja y propone alternativa | |
| 4 | ¿Monorepo o microfrontends para 4 equipos? | agente `angular-architect`; modo Estándar, alternativa simple, drivers | |
| 5 | Evalúa la arquitectura de este repo | `angular-architecture-assessment`; lee ficheros, cita rutas, no escribe | |
| 6 | Planifica el upgrade a la última versión mayor | `angular-modernization-governance`; plantilla upgrade-plan, comprueba versión actual | |
| 7 | Activa SSR | `angular-performance-ssr`; pregunta/confirma driver, código universal | |
| 8 | Arregla el test roto de `X.service.ts` | `angular-testing-quality`; ejecuta el test antes de informar | |
| 9 | `/angular:angular-review` con cambios pendientes | `angular-architect` solo lectura; hallazgos con `fichero:línea` | |
| 10 | Configura las convenciones de este proyecto | `angular-project-guidelines`; escribe el bloque `## Convenciones Angular` en `CLAUDE.md`, enseña diff | |
| 11 | Con `tests: required`: crea un servicio `OrderService` | crea `order-service.spec.ts`; el hook Stop no bloquea; ejecuta `verify` | |
| 12 | Con `tests: required`, pedir un componente y cortar antes del spec (simulado) | el hook Stop bloquea con la lista de ficheros sin spec | |
| 13 | Sin `a11y` definido: crea un formulario de login | lee `angular-quality-a11y` igualmente; cumple WCAG-2.2-AA (`label`, `aria-describedby`, foco, tamaño de objetivo, entrada redundante); sin rehacer | |
| 14 | Con `a11y: WCAG-2.1-AA` en el CLAUDE.md: crea un botón de icono | usa el nivel del proyecto; nombre accesible y teclado | |
| 15 | Servicio con 3 responsabilidades pedido en una frase | mini-diseño SOLID previo; divide en piezas; no crea abstracciones vacías | |
| 16 | Con `docs: jsdoc`: crea un componente con inputs/outputs | JSDoc en clase, inputs/outputs y métodos públicos, sin comentarios triviales | |
| 17 | `/spec` para una feature y luego `/spec-impl` (instalados aparte) | la spec incluye diseño de clases, criterios a11y y plan de tests; la implementación aplica SOLID previo, crea specs en el mismo paso y ejecuta `verify` | |

Criterios transversales: informa qué verificó y qué no; no usa APIs experimentales sin avisar; `angular-architect` nunca edita ficheros.
