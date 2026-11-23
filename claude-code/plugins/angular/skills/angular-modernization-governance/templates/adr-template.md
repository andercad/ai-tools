# ADR-NNN: <título corto de la decisión>

- **Estado**: Propuesto | Aceptado | Rechazado | Sustituido por ADR-XXX
- **Fecha**: AAAA-MM-DD
- **Responsables**: <roles> · **Consultados**: <equipos>
- **Versiones**: Angular <v>, TypeScript <v>, Node.js <v>

## Contexto
Problema y por qué ahora. Hechos verificados (métricas, incidentes, versiones) separados de supuestos.

## Drivers
- <driver medible: p. ej. INP p75 < 200 ms, publicación independiente del equipo X>
- <restricciones: plazo, equipo, cumplimiento, host (p. ej. Liferay)>

## Alternativas (máximo tres, incluida la más simple)
| Criterio (peso 1-3) | Opción A (más simple) | Opción B | Opción C |
|---|---|---|---|
| <driver> | | | |
| Coste de adopción y mantenimiento | | | |
| Impacto en accesibilidad, seguridad y rendimiento | | | |
| Riesgo de migración y reversibilidad | | | |
| Estado de las APIs implicadas (estable, preview, experimental) | | | |
| Total ponderado | | | |

## Decisión
Se elige **<opción>** porque <criterios>. Criterio que decide: <...>. Cambio de peso que invertiría el resultado: <...>.

## Consecuencias
- **Positivas**:
- **Negativas y costes asumidos**:
- **Riesgos**: <riesgo → mitigación → responsable>

## Verificación
Fitness functions en CI (límites, presupuestos, APIs deprecadas, accesibilidad) y criterios de aceptación por etapa con rollback.

## Criterios de revisión
<cuándo reabrir: nueva versión mayor, cambio en los equipos, métrica fuera de objetivo>

## Pendiente de verificar
- <...>
