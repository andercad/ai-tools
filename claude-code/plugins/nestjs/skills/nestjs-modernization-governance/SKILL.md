---
name: nestjs-modernization-governance
description: 'Asesoría arquitectónica sobre modernización, migración y gobierno técnico de aplicaciones NestJS. Usar cuando se pida planificar la actualización de Node.js, NestJS o TypeScript, migrar de CommonJS a ESM, de Express a Fastify, de TypeORM a otro ORM o de monolito a módulos, estrategia strangler, redactar un ADR, definir estándares, quality gates, fitness functions, gestión de dependencias, deuda técnica, roadmap de modernización, elegir entre NestJS y Spring Boot para un servicio o calcular una matriz de decisión. No usar como generador de código por defecto.'
---

# Modernización, gobierno y ADR

## Objetivo
Planificar cambios grandes de forma incremental y reversible, y dejar decisiones y reglas verificables.

## 1. Estrategia de modernización
- Punto de partida: inventario de versiones (Node, NestJS, TypeScript, librerías clave), soporte (fin de vida/EOL de Node y de NestJS), vulnerabilidades, cobertura de pruebas y estado del pipeline. Sin red de seguridad de pruebas, el primer paso es crearla (pruebas de caracterización de los flujos críticos).
- **Actualizaciones**: una versión mayor cada vez, no saltos múltiples. Lee la guía de migración oficial de NestJS de cada versión y las notas de ruptura de las dependencias (ORM, Passport, GraphQL, Swagger). Alinea `@nestjs/*` en la misma versión mayor. Verifica la compatibilidad Node↔NestJS↔TypeScript con la documentación vigente. Marca como pendiente lo que no puedas comprobar.
- **Express → Fastify**: cambio de adaptador con impacto en middleware, `req/res` usados directamente, uploads y librerías. Aíslalo en un spike y mide antes de comprometerte.
- **CommonJS → ESM**: verifica soporte de ESM en NestJS, herramientas de test (Jest, Vitest), bundler/SWC y todas las dependencias. Suele ser un cambio de alto coste y bajo beneficio funcional: justifícalo con un driver real.
- **Cambio de ORM, de monolito a módulos o extracción de servicios**: patrón **strangler fig** (fachada que redirige por funcionalidad), ejecución en paralelo y comparación de resultados cuando proceda, migración de datos por fases y feature flags.
- **Priorización**: riesgo (seguridad/EOL) x valor x esfuerzo. Divide en hitos de 1-2 semanas, cada uno desplegable y reversible.

## 2. Plan de migración
Para cada hito: alcance, criterio de aceptación, pruebas necesarias, métricas de salud (errores, latencia), plan de **rollback** y ventana de congelación. Mantén una rama o rama de release estable para hotfixes. Comunica a los equipos. Deja de aceptar nuevo código del patrón antiguo (regla "no empeorar").

## 3. Gobierno técnico
- **ADR**: un documento corto por decisión relevante (formato MADR o similar): contexto, drivers, opciones consideradas, decisión, consecuencias (positivas y negativas), estado (propuesta/aceptada/sustituida) y fecha. Se versionan junto al código y no se editan: se sustituyen. Decisión reversible → ADR ligero. Decisión costosa de revertir → ADR completo con revisión.
- **Estándares**: un conjunto pequeño y aplicable (estructura de módulos, convenciones de API, logging, errores, seguridad base, estrategia de pruebas). Si no se puede automatizar o revisar, simplifícalo.
- **Quality gates y fitness functions** en CI: lint, tipos estrictos, tests con umbrales realistas, límites de dependencias entre módulos (Nx/ESLint/Dependency Cruiser), ausencia de ciclos, auditoría de dependencias, escaneo de secretos, comprobación de breaking changes de API, presupuestos de rendimiento. Distingue gates bloqueantes de avisos.
- **Dependencias**: lockfile, actualizaciones automatizadas (Renovate/Dependabot) agrupadas, política de versiones soportadas, criterios para añadir una librería (mantenimiento, licencia, seguridad), control de licencias.
- **Deuda técnica**: registro visible con impacto y coste del retraso, presupuesto fijo de capacidad por iteración, y revisión periódica.
- **Cultura y modelo operativo**: propiedad por equipos de cada módulo/servicio, comité ligero de arquitectura que asesora (no bloquea) y revisiones de arquitectura asíncronas.

## 4. Pruebas durante el cambio
Pirámide equilibrada: unitarias de dominio, integración con dependencias reales (Testcontainers), contrato de API, e2e de flujos críticos y smoke tests post-despliegue. Pruebas de caracterización antes de refactorizar código sin tests.

## 5. Selección de tecnología y matrices de decisión
- Para decidir si un servicio se construye con NestJS o con Spring Boot, usa `reference/backend-technology-selection.md`.
- Para cualquier matriz de decisión, ejecuta `scripts/decision_matrix.py` con un JSON de criterios (peso 1-3) y valoraciones (1-5): devuelve el total ponderado, el criterio que decide, la sensibilidad a pesos y valoraciones y un veredicto de robustez. Si no puedes ejecutar scripts, haz el cálculo y muéstralo paso a paso.

## Salida
Usa la plantilla `templates/adr-template.md` para cada ADR.
Inventario y diagnóstico, estrategia elegida con alternativas, roadmap por hitos con criterios de aceptación y rollback, riesgos, plan de pruebas, gates propuestos, plantilla de ADR rellenada con la decisión y decisiones abiertas.

## Autoevaluación
¿Cada hito es reversible y desplegable? ¿Hay red de pruebas antes de tocar código? ¿Se evita saltar versiones mayores y migrar por moda (ESM, Fastify)? ¿Las reglas se pueden automatizar? ¿Las compatibilidades no verificadas están marcadas como pendientes?
