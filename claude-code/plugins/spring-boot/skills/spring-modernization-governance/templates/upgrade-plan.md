# Plan de upgrade: <aplicación> de <origen> a <destino>

## 1. Línea base
| Componente | Versión actual | Destino | Fin de soporte (fuente) |
|---|---|---|---|
| Java | | | Pendiente de verificar |
| Spring Boot | | | |
| Spring Framework, Security y Cloud | | | |
| Hibernate y drivers | | | |
| Plugins de build y agentes | | | |

Estado de las pruebas: cobertura útil de recorridos críticos, pruebas intermitentes y tiempo de ejecución.

## 2. Matriz de bloqueos
| Dependencia | Versión actual | ¿Compatible con el destino? | Alternativa | Riesgo | Acción |
|---|---|---|---|---|---|

## 3. Etapas
| # | Cambio principal | Criterio de aceptación | Despliegue | Rollback |
|---|---|---|---|---|
| 0 | Pruebas de caracterización y de contrato de los recorridos críticos | En verde y estables | — | — |
| 1 | Última versión menor de la línea actual; resolver deprecaciones | Sin avisos de deprecación relevantes | Canary | Versión anterior |
| 2 | Java <destino> | Build y pruebas en verde | | |
| 3 | Spring Boot <destino> según la guía oficial de migración | | | |
| 4 | Librerías de terceros | | | |

Un cambio principal por etapa y cada etapa desplegable. No mezclar con refactors funcionales.

## 4. Automatización
Herramientas de ayuda (p. ej. OpenRewrite) y qué revisar manualmente después.

## 5. Riesgos
| Riesgo | Probabilidad | Impacto | Mitigación | Señal de alerta | Responsable |
|---|---|---|---|---|---|

## 6. Go/no-go
Criterios para pasar a producción: pruebas, rendimiento comparado con la línea base, errores, observabilidad y rollback ensayado.
