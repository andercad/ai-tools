# Plan de upgrade de Angular: <aplicación> de <origen> a <destino>

## 1. Línea base
| Componente | Actual | Destino | Rango compatible verificado | Fuente |
|---|---|---|---|---|
| Angular | | | | angular.dev (versiones y guía de actualización) |
| TypeScript | | | | |
| Node.js | | | | |
| Librería de UI | | | | |
| Gestión de estado | | | | |
| Monorepo (si aplica) | | | | |
| Test runner y E2E | | | | |

Fin de soporte de la versión actual: <fecha verificada o «Pendiente de verificar»>.

## 2. Matriz de bloqueos
| Dependencia | Versión actual | ¿Compatible con el destino? | Alternativa | Riesgo | Acción |
|---|---|---|---|---|---|

## 3. Etapas
| # | Cambio | Criterio de aceptación | Rollback |
|---|---|---|---|
| 0 | Pruebas de caracterización de los recorridos críticos | En verde y estables | — |
| 1 | <mayor N → N+1> con `ng update` y migraciones automáticas | Build, pruebas y presupuestos en verde | Versión anterior desplegada |
| 2 | <mayor N+1 → N+2> | | |
| … | Migraciones opcionales priorizadas (standalone, control flow, zoneless…) | Métrica de beneficio | |

Una versión mayor por etapa; sin refactors funcionales mezclados.

## 4. Migraciones opcionales
| Migración | Beneficio esperado | Métrica | Estado de la API en el destino | Prioridad |
|---|---|---|---|---|

## 5. Riesgos
| Riesgo | Probabilidad | Impacto | Mitigación | Señal de alerta | Responsable |
|---|---|---|---|---|---|

## 6. Go/no-go
Pruebas, presupuestos de bundle, Web Vitals comparados con la línea base, errores en cliente y rollback ensayado.
