---
name: angular-architecture-assessment
description: 'Evalúa la arquitectura de una aplicación Angular existente o propuesta: descubrimiento, inventario de features y dependencias, deuda técnica, riesgos, NFR, production readiness y diagnóstico basado en evidencia de problemas recurrentes de arquitectura (rendimiento, SSR, despliegue, integración). Usar cuando se pida revisar, auditar o diagnosticar una aplicación Angular, evaluar su salud arquitectónica, priorizar deuda técnica, preparar un due diligence técnico, decidir por dónde empezar un cambio o analizar un incidente recurrente que apunte a un problema de diseño. No usar para decisiones de patrón concretas (estado, renderizado, integración), para depurar código línea a línea ni como generador de código.'
---

# Evaluación y diagnóstico de arquitectura Angular

## Objetivo
Obtener una imagen fiable del sistema, separando hechos con evidencia de supuestos, identificar riesgos y deuda con impacto real y priorizar acciones incrementales. No prescribas patrones antes de conocer el sistema.

## Descubrimiento
Material que pedir, en orden de valor:
1. `package.json` y lockfile, salida de `ng version`.
2. `angular.json` o `project.json`, `tsconfig.json` (flags `strict`).
3. Árbol de `src/app` (2–3 niveles), `app.config.ts` y definición de rutas.
4. Informe de bundle, Lighthouse y, si existen, datos de campo (CrUX o RUM).
5. Pipeline de CI/CD, Dockerfile o configuración de hosting.
6. Contrato de las APIs consumidas y flujo de autenticación.
Sin material: como máximo 3 preguntas aclaratorias y supuestos etiquetados.

## Dimensiones de evaluación
| Dimensión | Qué revisar | Señales de alerta |
|---|---|---|
| Versión y soporte | Versión mayor frente a soporte activo/LTS; dependencias que bloquean el upgrade | Versión fuera de soporte, librerías abandonadas |
| Estructura y límites | Organización por feature, dependencias entre features, `shared` | Ciclos, `shared` como cajón de sastre, componentes de miles de líneas |
| Reactividad y estado | Fuente de verdad, mezcla de patrones, limpieza de suscripciones | Estado remoto duplicado, `effect` para derivar estado, suscripciones anidadas |
| Renderizado y rendimiento | Bundle inicial, lazy loading, LCP/INP/CLS, SSR real frente a declarado | Sin presupuestos, todo en el bundle inicial, optimizaciones sin baseline |
| Integración | Contratos tipados o generados, errores, reintentos, autenticación | `any` en DTO, tokens en `localStorage`, reintentos de escrituras |
| Calidad | Estrategia de pruebas, flakiness, lint, accesibilidad | Solo un porcentaje de cobertura como objetivo, E2E inestables |
| Seguridad | `bypassSecurityTrust*`, `innerHTML`, CSP, secretos, dependencias | Secretos en `environment.ts`, vulnerabilidades sin gestionar |
| Entrega y operación | Build único promovido entre entornos, configuración runtime, observabilidad del frontend, rollback | Build distinto por entorno, sin captura de errores en cliente |

## Diagnóstico de problemas recurrentes
1. Impacto, alcance y timeline (qué cambió y cuándo).
2. Separa capas: navegador, aplicación, red y CDN, servidor SSR, backend, infraestructura.
3. Hipótesis ordenadas por probabilidad y coste de prueba.
4. Prueba discriminante por hipótesis; causa confirmada solo con evidencia.
5. Cambio mínimo reversible y prevención (fitness function, alerta o ADR).
No atribuyas causa por correlación ni conviertas hipótesis en hechos.

## Antipatrones a detectar
- Reescritura propuesta sin diagnóstico ni drivers.
- Store global para todo o, al contrario, estado compartido mutable sin dueño.
- Microfrontends o monorepo sin autonomía de equipos que lo justifique.
- Guards como única protección de datos.
- Configuración de entorno compilada en el bundle.

## Criterios de decisión: priorización
Clasifica hallazgos como BLOCKER, MAJOR, MINOR u OPCIONAL. BLOCKER y MAJOR requieren evidencia (fichero, métrica o log). Ordena por impacto frente a esfuerzo y separa quick wins de cambios estructurales. Asigna cada hallazgo a la skill que desarrolla la solución.

## Salida
Usa `templates/assessment-report.md` como estructura del informe.
- Resumen ejecutivo: estado general y los tres riesgos principales.
- Tabla `ID | Dimensión | Hallazgo | Evidencia | Severidad | Impacto | Recomendación | Skill`.
- Lista de lo no verificado y cómo verificarlo.
- Deuda técnica priorizada y roadmap 30/60/90 días con criterios de aceptación.

## Autoevaluación
¿Cada hallazgo grave tiene evidencia? ¿He separado hechos de supuestos? ¿He propuesto reescritura o patrones sin drivers? ¿He omitido seguridad, accesibilidad u operación? ¿El roadmap es incremental y reversible?
