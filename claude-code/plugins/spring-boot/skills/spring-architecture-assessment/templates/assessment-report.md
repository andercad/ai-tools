# Informe de evaluación arquitectónica: <sistema Spring Boot>

**Fecha**: AAAA-MM-DD · **Alcance**: <qué se evaluó y qué no> · **Material revisado**: <pom.xml o build.gradle, application.yml, código, diagramas, métricas> · **Confianza global**: alta | media | baja

Etiqueta cada dato como `observado`, `declarado por el usuario`, `inferido` o `desconocido`.

## 1. Resumen ejecutivo
- Estado general en una frase.
- Tres conclusiones principales (ID del hallazgo y una línea).
- Primer paso recomendado y por qué va primero.

## 2. Plataforma y contexto
| Elemento | Valor | Fuente | Soporte / fin de soporte |
|---|---|---|---|
| Java | | | Pendiente de verificar |
| Spring Boot | | | Pendiente de verificar |
| Spring Framework, Security y Cloud | | | |
| Build y BOM | Maven / Gradle | | |
| Estilo web | MVC / WebFlux | | |
| Persistencia y migraciones | | | |
| Mensajería | | | |
| Plataforma de despliegue | | | |

Propósito, usuarios, criticidad y restricciones (cumplimiento, plazos, equipo, coste).

## 3. Vista arquitectónica actual
Diagrama de contexto y de contenedores (Mermaid) con una descripción breve. Marca qué es observado y qué inferido.

## 4. Valoración por dimensión
| Dimensión | Puntuación (1-5) | Evidencia | Confianza | Skill |
|---|---|---|---|---|
| Modularidad y límites (ciclos, paquetes por dominio) | | | | modularity-domain |
| Dominio independiente del framework | | | | modularity-domain |
| APIs, contratos y eventos | | | | api-integration |
| Datos y transacciones | | | | data-transactions |
| Seguridad e identidad | | | | security-identity |
| Runtime, configuración y despliegue | | | | cloud-runtime |
| Observabilidad y resiliencia | | | | observability-resilience |
| Pruebas, CI y versiones | | | | modernization-governance |

## 5. Hallazgos y deuda
| ID | Hallazgo | Evidencia | Impacto (A/M/B) | Esfuerzo (S/M/L) | Riesgo de no actuar | Bloquea a | Recomendación |
|---|---|---|---|---|---|---|---|
| H-01 | | | | | | | |

Prioriza por impacto/esfuerzo y por lo que desbloquea otras decisiones (por ejemplo, el upgrade de versión antes que las optimizaciones).

## 6. Hechos, supuestos y desconocidos
| Dato | Tipo | Cómo verificarlo |
|---|---|---|

## 7. Decisiones pendientes
| Decisión | Por qué importa | Opciones | Skill | Responsable | Fecha límite |
|---|---|---|---|---|---|

## 8. Roadmap
- **30 días**: reducción de riesgo y quick wins.
- **60 días**: mejoras estructurales con criterios de aceptación.
- **90 días**: decisiones de arquitectura con ADR.

## 9. Autoevaluación
Qué conclusiones dependen de datos inferidos, qué material cambiaría el diagnóstico y qué riesgos podrían faltar.
