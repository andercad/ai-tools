---
name: nestjs-architecture-assessment
description: 'Evaluación arquitectónica y descubrimiento de un sistema NestJS existente o propuesto. Usar cuando se pida revisar, auditar o diagnosticar una arquitectura, hacer un architecture review o health check, evaluar deuda técnica, mapear contexto y dependencias, detectar antipatrones (dependencias circulares, god services, módulo shared), valorar madurez o priorizar riesgos y decisiones pendientes. No usar para diseñar una solución nueva concreta ni como generador de código.'
---

# Evaluación arquitectónica y descubrimiento

## Objetivo
Producir un diagnóstico basado en evidencia: qué hay, qué riesgos tiene y qué decidir primero. Distingue **hechos** (observados en el material aportado), **inferencias** y **recomendaciones**. No confundas la estructura de carpetas con la arquitectura.

## 1. Descubrimiento
Sin acceso al repositorio, pide al usuario este material (por orden de valor) y trabaja con lo que haya, marcando lo que falta como no verificado:
1. Contexto: propósito del sistema, usuarios, criticidad, SLA/SLO, equipos, restricciones (cumplimiento, coste, plazos).
2. `package.json` y lockfile, `nest-cli.json`, `tsconfig.json`, versiones de Node/NestJS.
3. `main.ts`, `app.module.ts` y la estructura de módulos (árbol de carpetas a 2-3 niveles).
4. Diagrama o descripción de integraciones: BD, brokers, APIs externas, identidad, plataforma.
5. Pipeline CI/CD, estrategia de pruebas y cobertura, métricas e incidentes recientes.
Para código local, sugiere comandos de solo lectura: `npm ls @nestjs/core`, `npx madge --circular --extensions ts src`, `npm audit`, recuento de `forwardRef` y de providers con `Scope.REQUEST`. Pregunta antes de pedir cualquier dato sensible: no pidas secretos.

## 2. Qué examinar
- **Estructura y límites**: ¿módulos por dominio o por capa técnica? ¿API pública por módulo? ¿ciclos, `forwardRef`, `@Global()` abusivo, `SharedModule` con negocio, "god services" con muchas dependencias?
- **Dominio y transporte**: ¿hay lógica de negocio en controllers, resolvers o entidades ORM acopladas al API? ¿DTO distintos de entidades?
- **Datos**: propiedad de tablas, transacciones, migraciones, consultas N+1, base de datos compartida, esquema versionado.
- **Integración**: llamadas síncronas en cadena, timeouts, reintentos, idempotencia, outbox, contratos y versionado.
- **Seguridad**: autenticación y autorización (denegación por defecto, autorización por recurso), validación de entrada, secretos, dependencias.
- **Operación**: configuración, probes, shutdown, observabilidad (logs, métricas, trazas), despliegue y rollback.
- **Calidad y evolución**: pruebas (pirámide, aislamiento), tipos estrictos, lint, versiones soportadas (EOL de Node/NestJS), automatización de dependencias.
- **Equipo y proceso**: propiedad de módulos, ritmo de cambio, puntos de fricción, conocimiento concentrado.

## 3. Antipatrones frecuentes en NestJS
Módulo que importa todo; servicios que mezclan HTTP, negocio y persistencia; entidades ORM expuestas como respuesta; `Scope.REQUEST` extendido sin necesidad; lógica en guards/interceptores; configuración leída con `process.env` repartido por el código; `synchronize: true` en producción; ausencia de timeouts; DTO sin validación; microservicios con BD compartida; hexagonal aplicada a CRUD trivial (interfaces vacías).

## 4. Valoración
Puntúa cada dimensión (por ejemplo 1-5) con **evidencia citada** y nivel de confianza (alta/media/baja según el material disponible). Prioriza hallazgos por **impacto x probabilidad** y por esfuerzo de remediación. Separa "quick wins" (días), mejoras estructurales (semanas) y decisiones de arquitectura (necesitan ADR). Recomienda empezar por lo que reduce riesgo o desbloquea el resto.

## 5. Atributos de calidad
Convierte necesidades vagas en escenarios medibles (estímulo, entorno, respuesta, medida). Ejemplo: "p95 < 300 ms con 200 req/s", "RTO 1 h". Si el usuario no los tiene, propón valores provisionales claramente marcados como supuestos.

## Salida
En evaluaciones completas, sigue la estructura de `templates/assessment-report.md`. En revisiones rápidas, entrega solo el resumen y la tabla de hallazgos.
Resumen ejecutivo con los 3-5 hallazgos principales, mapa de contexto y de contenedores/componentes (texto o Mermaid), tabla de hallazgos (ID, evidencia, impacto, probabilidad, esfuerzo, recomendación), mapa de calor de dimensiones, supuestos y datos no verificados, decisiones pendientes con propietario sugerido, y roadmap incremental de 30/60/90 días.

## Autoevaluación
¿Cada hallazgo tiene evidencia o está marcado como inferencia? ¿Se declara qué no se pudo ver? ¿Se evita proponer rediseños completos cuando bastan cambios pequeños? ¿Las prioridades son consistentes con los drivers del negocio?
