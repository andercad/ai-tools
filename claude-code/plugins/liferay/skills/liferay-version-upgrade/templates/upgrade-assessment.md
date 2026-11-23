# Evaluación y plan de upgrade de Liferay: <origen> → <destino>

## 1. Release objetivo
| Opción | Soporte (fuente) | Capacidades necesarias | Decisión |
|---|---|---|---|
| Última LTS | | | |
| Última Quarterly Release | | | |
| Mantener la actual | | | |

## 2. Compatibilidad
| Componente | Actual | Requerido por el destino (Compatibility Matrix) | Acción |
|---|---|---|---|
| Java | | | |
| Servidor de aplicaciones | | | |
| Base de datos | | | |
| Motor de búsqueda | | | |
| Liferay Workspace y Gradle | | | |

## 3. Customizaciones
| Customización | Tipo | Breaking changes o deprecaciones que la afectan | Clasificación (compatible, requiere cambio, rediseño, retirar) | Esfuerzo | Riesgo |
|---|---|---|---|---|---|

## 4. Feature flags, capacidades Beta y deprecaciones
| Capacidad | Estado en el destino (Beta, maintenance mode, deprecada, activa por deprecation feature flag) | ¿Se usa en producción? | Alternativa | Riesgo aceptado por |
|---|---|---|---|---|

## 5. Ensayos
| Ensayo | Fecha | Copia de datos (fecha) | Duración del upgrade de base de datos | Duración de la reindexación | Incidencias | Resultado |
|---|---|---|---|---|---|---|

## 6. Validación
Contenido, permisos, workflows, integraciones, búsqueda, rendimiento comparado con la línea base y recorridos críticos.

## 7. Go/no-go
| Criterio | Umbral | Resultado |
|---|---|---|
| Recorridos críticos | 100 % en verde | |
| Rendimiento | ≤ línea base + <x> % | |
| Incidencias abiertas | Ninguna BLOCKER ni MAJOR | |
| Rollback ensayado | Sí | |

## 8. Rollback
- Punto de no retorno: <...>
- Backups previos y retención: <...>
- Tiempo de vuelta atrás medido en el ensayo: <...>

## 9. Riesgos
| Riesgo | Probabilidad | Impacto | Mitigación | Responsable |
|---|---|---|---|---|
