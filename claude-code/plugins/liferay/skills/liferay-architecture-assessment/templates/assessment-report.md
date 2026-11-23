# Informe de evaluación arquitectónica: <instalación Liferay>

**Fecha**: AAAA-MM-DD · **Alcance**: <qué se evaluó y qué no> · **Material revisado**: <gradle.properties, portal-ext.properties sin secretos, inventario de módulos y Client Extensions, topología, métricas, incidentes> · **Confianza global**: alta | media | baja

Etiqueta cada dato como `observado`, `declarado` o `inferido`.

## 1. Resumen ejecutivo
- Estado general en una frase.
- Tres riesgos principales (ID y una línea).
- Primer paso recomendado y por qué va primero.

## 2. Plataforma
| Elemento | Valor | Fuente | Compatibilidad o soporte |
|---|---|---|---|
| Producto y modalidad | DXP o Portal CE · self-hosted, PaaS o SaaS | | |
| Release actual | | | Pendiente de verificar |
| Java y servidor de aplicaciones | | | Compatibility Matrix |
| Base de datos | | | Compatibility Matrix |
| Motor de búsqueda | | | Compatibility Matrix |
| Almacenamiento de documentos | | | |
| Nodos, balanceo y sesiones | | | |
| IdP y SSO | | | |

## 3. Inventario de customizaciones
| Customización | Tipo (módulo OSGi, Service Builder, override, tema, Client Extension, Object, Fragment) | Motivo | Alternativa estándar actual | Coste de upgrade (A/M/B) | Recomendación (mantener, sustituir, retirar) |
|---|---|---|---|---|---|

| Capacidad en uso | Estado (maintenance mode o deprecada) | Desde | Alternativa propuesta por Liferay | Plan de transición |
|---|---|---|---|---|

## 4. Valoración por dimensión
| Dimensión | Puntuación (1-5) | Evidencia | Confianza | Skill |
|---|---|---|---|---|
| Mecanismos y customizaciones | | | | solution-architecture |
| Integraciones y Client Extensions | | | | client-extensions-integration |
| Modelo de datos y extensiones internas | | | | platform-customization |
| Contenido y búsqueda | | | | content-search |
| Seguridad y permisos | | | | security-identity |
| Operación, rendimiento y DR | | | | cloud-operations |
| Release y deuda de upgrade | | | | version-upgrade |

## 5. Hallazgos
| ID | Dimensión | Hallazgo | Evidencia | Severidad | Impacto | Esfuerzo (S/M/L) | Recomendación |
|---|---|---|---|---|---|---|---|
| H-01 | | | | BLOCKER / MAJOR / MINOR / OPCIONAL | | | |

BLOCKER y MAJOR requieren evidencia (fichero, métrica, log o thread dump).

## 6. Diagnóstico de incidentes recurrentes (si aplica)
| Hipótesis | Capa (portal, OSGi, Client Extension, base de datos, búsqueda, almacenamiento, red, terceros) | Prueba discriminante | Resultado | Estado |
|---|---|---|---|---|

## 7. No verificado
- <dato> → cómo verificarlo.

## 8. Roadmap
- **30 días**: reducción de riesgo y quick wins.
- **60 días**: sustitución de las customizaciones con mayor coste de upgrade.
- **90 días**: decisiones con ADR y plan de upgrade.

## 9. Autoevaluación
Qué conclusiones dependen de inferencias y qué material las confirmaría.
