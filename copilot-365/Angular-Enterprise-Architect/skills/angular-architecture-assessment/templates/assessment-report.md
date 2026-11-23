# Informe de evaluación arquitectónica: <aplicación Angular>

**Fecha**: AAAA-MM-DD · **Alcance**: <qué se evaluó y qué no> · **Material revisado**: <package.json, angular.json, estructura de src/app, informes de bundle, Lighthouse o RUM, pipeline> · **Confianza global**: alta | media | baja

Etiqueta cada dato como `observado`, `declarado` o `inferido`.

## 1. Resumen ejecutivo
- Estado general en una frase.
- Tres riesgos principales (ID y una línea).
- Primer paso recomendado y por qué va primero.

## 2. Plataforma
| Elemento | Valor | Fuente | Estado de soporte |
|---|---|---|---|
| Angular | | | Pendiente de verificar en angular.dev |
| TypeScript y Node.js | | | |
| Standalone o NgModules | | | |
| zone.js o zoneless | | | |
| CSR, SSR o SSG | | | |
| Gestión de estado | | | |
| Test runner y E2E | | | |
| Monorepo | | | |
| Hosting y CDN | | | |
| Backend, autenticación y Liferay (si aplica) | | | |

## 3. Vista actual
Diagrama de contexto (usuarios, frontend, BFF o APIs, IdP, CDN, Liferay) y mapa de features con sus dependencias. Marca lo observado y lo inferido.

## 4. Valoración por dimensión
| Dimensión | Puntuación (1-5) | Evidencia | Confianza | Skill |
|---|---|---|---|---|
| Estructura y límites | | | | architecture |
| Reactividad y estado | | | | reactivity-state |
| Renderizado y rendimiento (LCP, INP, CLS, bundle) | | | | rendering-performance |
| Calidad y pruebas | | | | quality-security |
| Accesibilidad | | | | quality-security |
| Seguridad del frontend | | | | quality-security |
| Integración con backends | | | | backend-integration |
| Integración con Liferay | | | | liferay-integration |
| Versiones y modernización | | | | modernization-governance |
| Entrega y operación | | | | rendering-performance |

## 5. Hallazgos
| ID | Dimensión | Hallazgo | Evidencia | Severidad | Impacto | Esfuerzo (S/M/L) | Recomendación |
|---|---|---|---|---|---|---|---|
| H-01 | | | | BLOCKER / MAJOR / MINOR / OPCIONAL | | | |

BLOCKER y MAJOR requieren evidencia (fichero, métrica o log).

## 6. Diagnóstico de incidentes recurrentes (si aplica)
| Hipótesis | Capa | Prueba discriminante | Resultado | Estado (confirmada, descartada, abierta) |
|---|---|---|---|---|

## 7. No verificado
- <dato> → cómo verificarlo.

## 8. Roadmap
- **30 días**: reducción de riesgo y quick wins.
- **60 días**: cambios estructurales con criterio de aceptación.
- **90 días**: decisiones con ADR y fitness functions.

## 9. Autoevaluación
Qué conclusiones dependen de inferencias y qué material las confirmaría.
