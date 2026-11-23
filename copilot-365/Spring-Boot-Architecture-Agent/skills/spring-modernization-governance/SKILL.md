---
name: spring-modernization-governance
description: 'Asesoría sobre modernización y gobierno de arquitectura Spring Boot: planificación de upgrades entre versiones de Java, Spring Boot y Spring Framework (incluidos saltos de línea mayor), migración desde versiones antiguas, patrón strangler, ADR, estándares y quality gates, gestión de dependencias, fitness functions, estrategia de pruebas (pirámide, Testcontainers, contrato, arquitectura) y roadmap incremental, selección de tecnología backend (Spring Boot o NestJS) y matrices de decisión. Usar cuando se pregunte cómo actualizar, migrar o modernizar una aplicación Spring, cómo priorizar y secuenciar el cambio, cómo documentar decisiones con ADR, cómo diseñar la estrategia de pruebas, si construir un servicio con Spring Boot o con NestJS o cómo evitar la erosión arquitectónica. No usar para ejecutar el upgrade ni como generador de código por defecto.'
---

# Modernización, gobierno y ADR

## Objetivo
Planificar cambios de plataforma y arquitectura de forma incremental, verificable y reversible, y mantener las decisiones documentadas y vigiladas.

## Planificar un upgrade
1. **Línea base**: versión actual de Java, Boot, Framework, Security, Spring Cloud, Hibernate y librerías clave; cobertura y fiabilidad de pruebas; fecha de fin de soporte (verificar en la documentación oficial, no de memoria).
2. **Destino**: la línea soportada más reciente que el ecosistema y el equipo toleren; consulta las notas de versión y la guía de migración de cada línea.
3. **Ruta**: pasa por la última versión menor de la línea actual antes de saltar de línea mayor; resuelve ahí los avisos de deprecación. Evita saltos que acumulen varias líneas mayores sin etapas intermedias.
4. **Cambios típicos de un salto mayor** (verifica por versión): baseline de Java, cambio `javax.*` → `jakarta.*` (Boot 2→3), eliminación de APIs deprecadas, cambios en propiedades, en Spring Security, Hibernate y librerías JSON o de pruebas. Spring Boot 4 / Framework 7 introduce, entre otros, una reorganización modular de starters y de autoconfiguración y cambios de ecosistema; revisa la guía oficial de migración antes de estimar.
5. **Dependencias de terceros**: matriz de compatibilidad (librerías, drivers, agentes, plugins de build). Identifica las que bloquean.
6. **Ejecución por etapas**: un cambio principal por paso (Java → Boot → librerías), cada etapa desplegable y con pruebas en verde; ramas de vida corta.
7. **Red de seguridad**: pruebas de caracterización/contrato antes de tocar; pruebas de integración con las dependencias reales (Testcontainers); despliegue canary y rollback preparado.
8. **Herramientas**: OpenRewrite o asistentes de migración pueden automatizar partes; trátalos como ayuda, revisa el resultado y no sustituyen el plan.

## Estrategias de modernización
- **Mantener y parchear**: si el sistema es estable, de bajo cambio y el riesgo es bajo.
- **Refactor incremental / monolito modular**: primera opción cuando el problema es acoplamiento interno.
- **Strangler fig**: extraer capacidades por fachada cuando exista un límite claro y un driver real; cada extracción reversible.
- **Reescritura**: solo con justificación explícita (coste, riesgo, paridad funcional, plan de coexistencia). Evita big bang.
Compara siempre contra «no hacer nada» con coste y riesgo de esa opción.

## ADR
Formato: **Título**, **Estado** (propuesto/aceptado/sustituido), **Contexto** (fuerzas y restricciones), **Decisión**, **Alternativas consideradas**, **Consecuencias** (positivas, negativas, riesgos), **Criterios de revisión** (cuándo reabrirla), **Fecha y responsables**. Un ADR por decisión; breve; enlazado a los NFR que la motivan. Marca «Pendiente de verificar» donde falten datos.

## Estrategia de pruebas
Las pruebas son la red de seguridad de cualquier cambio arquitectónico. Define la proporción por tipo según el riesgo, no por un porcentaje fijo de cobertura.
| Tipo | Qué protege | Herramienta habitual |
|---|---|---|
| Unitarias de dominio y casos de uso | Reglas de negocio, sin contexto Spring | JUnit, AssertJ |
| Slices | Adaptadores aislados (web, JPA, JSON) | `@WebMvcTest`, `@DataJpaTest`, `@JsonTest` |
| Integración con dependencias reales | Persistencia, mensajería, migraciones | Testcontainers |
| Contrato | Compatibilidad entre proveedor y consumidor | Spring Cloud Contract, Pact, validación OpenAPI |
| Arquitectura | Capas, módulos, ciclos | ArchUnit, Spring Modulith |
| Extremo a extremo | Flujos críticos de negocio, pocos | Entorno desplegado |
| No funcionales | Carga, resiliencia, seguridad | Ver skills de observabilidad y seguridad |
Reglas: rápidas y deterministas en cada commit; evita entornos compartidos y mocks del framework; en sistemas heredados empieza con pruebas de caracterización antes de refactorizar; mide la estabilidad (tests intermitentes) como deuda.

## Selección de tecnología y matrices de decisión
- Para decidir si un servicio se construye con Spring Boot o con NestJS, usa `reference/backend-technology-selection.md`.
- Para cualquier matriz de decisión, ejecuta `scripts/decision_matrix.py` con un JSON de criterios (peso 1-3) y valoraciones (1-5): devuelve el total ponderado, el criterio que decide, la sensibilidad a pesos y valoraciones y un veredicto de robustez. Si no puedes ejecutar scripts, haz el cálculo y muéstralo paso a paso.

## Gobierno y estándares
- **Fitness functions** automatizadas: reglas ArchUnit o Spring Modulith para dependencias, límites de módulos y capas, en CI.
- **Quality gates**: pruebas, cobertura útil (no solo porcentaje), análisis estático, vulnerabilidades de dependencias, SBOM, licencias.
- **Gestión de dependencias**: BOM, versiones centralizadas, actualización automatizada (p. ej. Dependabot o Renovate) y cadencia definida.
- **Estándares mínimos y pocos**: plantillas de proyecto, convenciones, observabilidad y seguridad base; revisión de arquitectura ligera para decisiones de alto impacto.
- **Medición**: tiempo de ciclo, frecuencia de despliegue, tasa de fallos de cambio, edad de dependencias, deuda priorizada.

## Salida
Usa `templates/upgrade-plan.md` para planes de upgrade y `templates/adr-template.md` para ADR.
Línea base, ruta de upgrade por etapas, matriz de riesgos y bloqueos, estrategia de pruebas y rollback, roadmap incremental con criterios de aceptación por etapa, ADR y quality gates propuestos.

## Autoevaluación
Comprueba que cada etapa es reversible y desplegable, que las fechas de soporte y cambios de versión están verificados o marcados como pendientes, que no se propone reescritura sin análisis de alternativas y que el gobierno propuesto es proporcional al tamaño del equipo.
