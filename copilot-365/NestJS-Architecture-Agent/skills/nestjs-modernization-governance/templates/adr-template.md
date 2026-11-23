# ADR-NNN: <título corto en imperativo>

- **Estado**: Propuesta | Aceptada | Rechazada | Sustituida por ADR-XXX
- **Fecha**: AAAA-MM-DD
- **Decisores**: <roles>
- **Consultados**: <roles/equipos>
- **Ámbitos relacionados**: <seguridad, datos, despliegue...>

## Contexto
Qué problema se resuelve y por qué ahora. Hechos verificados (versiones, métricas, incidentes) separados de supuestos.

## Drivers de decisión
- <driver 1, medible si es posible: p. ej. p95 < 300 ms, despliegue independiente del equipo X>
- <driver 2>
- <restricciones: plazo, presupuesto, cumplimiento, habilidades>

## Opciones consideradas
1. **<Opción A, la más simple>**
2. **<Opción B>**
3. **<Opción C>** (máximo tres)

## Decisión
Se elige **<opción>** porque <criterios que la favorecen frente a los drivers>.

### Condiciones que harían revisar esta decisión
- <p. ej. más de N equipos, volumen superior a X, nuevo requisito regulatorio>

## Comparación
| Criterio | Opción A | Opción B | Opción C |
|---|---|---|---|
| <driver 1> | | | |
| Coste operativo | | | |
| Complejidad / curva de aprendizaje | | | |
| Riesgo de migración | | | |
| Reversibilidad | | | |

## Consecuencias
- **Positivas**: <...>
- **Negativas / costes asumidos**: <...>
- **Riesgos y mitigaciones**: <riesgo → mitigación → responsable>

## Implementación y verificación
- Pasos incrementales y criterio de aceptación de cada uno.
- Pruebas o fitness functions que verifican la decisión en CI.
- Plan de rollback.

## Pendiente de verificar
- <datos, compatibilidades o costes no confirmados>
