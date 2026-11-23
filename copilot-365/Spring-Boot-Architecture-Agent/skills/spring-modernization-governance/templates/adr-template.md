# ADR-NNN: <título corto de la decisión>

- **Estado**: Propuesto | Aceptado | Rechazado | Sustituido por ADR-XXX
- **Fecha**: AAAA-MM-DD
- **Responsables**: <roles> · **Consultados**: <equipos>
- **Versiones afectadas**: Java <v>, Spring Boot <v>, Spring Framework <v>, otras <...>

## Contexto
Problema, fuerzas y restricciones. Separa hechos verificados (versiones, métricas, incidentes) de supuestos.

## Drivers y NFR
- <driver medible: p. ej. p95 < 300 ms, despliegue independiente del equipo X>
- <restricciones: plazo, presupuesto, cumplimiento, habilidades>

## Alternativas consideradas (máximo tres, incluida la más simple)
| Criterio (peso 1-3) | Opción A (mantener o más simple) | Opción B | Opción C |
|---|---|---|---|
| <driver 1> | | | |
| Coste operativo | | | |
| Riesgo de migración | | | |
| Reversibilidad | | | |
| Total ponderado | | | |

## Decisión
Se elige **<opción>** porque <criterios>. Criterio que decide: <...>. Cambio de peso que invertiría el resultado: <...>.

## Consecuencias
- **Positivas**:
- **Negativas y costes asumidos**:
- **Riesgos**: <riesgo → mitigación → responsable>

## Verificación
- Fitness functions o pruebas que vigilan la decisión en CI (ArchUnit, Spring Modulith, contrato, rendimiento).
- Pasos incrementales con criterio de aceptación y rollback.

## Criterios de revisión
Cuándo reabrir la decisión (p. ej. más de N equipos, volumen superior a X, nueva línea mayor de Spring Boot).

## Pendiente de verificar
- <compatibilidades, fechas de soporte o costes no confirmados>
