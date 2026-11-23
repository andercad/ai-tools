---
name: liferay-solution-architecture
description: 'Asesoría arquitectónica para seleccionar el mecanismo de solución en Liferay DXP y diseñar la arquitectura global: configuración estándar, Objects, Fragments y páginas, Headless APIs, Client Extensions, servicios externos (Spring Boot, NestJS), módulos OSGi o Service Builder; decidir qué se ejecuta dentro o fuera de la JVM del portal, restricciones de cada modalidad (self-hosted, PaaS, SaaS), diagramas C4, matrices de decisión y ADR. Usar cuando se pregunte cómo resolver un requisito en Liferay, qué mecanismo usar, si algo debe vivir dentro o fuera del portal o cómo encaja Liferay con otros sistemas. No usar para el diseño detallado de un mecanismo ya elegido ni como generador de código.'
---

# Selección de mecanismo y arquitectura de solución

## Objetivo
Elegir el mecanismo más simple que cumple el requisito, minimizando código dentro del portal y coste de upgrade, y describir la arquitectura global con sus fronteras.

## Criterios de decisión: escalera de mecanismos
1. **Configuración estándar** (instancia, site, permisos, workflow, plantillas): siempre primero.
2. **Low-code**: Objects para modelos de datos con API generada; Liferay CMS para contenido estructurado (GA desde 2026.Q3); Fragments, plantillas y Style Books para experiencia.
3. **Client Extensions**: frontend, configuración, microservicio, batch y acciones; código fuera de la JVM del portal.
4. **Servicio externo** (Spring Boot, NestJS) integrado por Headless y OAuth2 cuando hay responsabilidad propia.
5. **OSGi**: SPI, ciclo de vida o capacidad interna que no puede externalizarse.
6. **Service Builder**: persistencia interna con dominio complejo que Objects no cubre; solo donde la modalidad lo permite.
Cada salto debe justificarse con un requisito que el peldaño anterior no cumple.

## Dentro o fuera de la JVM
| Criterio | Dentro (OSGi) | Fuera (Client Extension o servicio) |
|---|---|---|
| Necesita SPI o ciclo de vida interno | Sí | No posible |
| Escalado y despliegue independientes | No | Sí |
| Impacto en upgrades | Alto | Bajo si usa APIs públicas |
| Disponible en SaaS | No para módulos personalizados | Sí, según tipos soportados |
| Latencia y transaccionalidad con datos del portal | Mejor | Llamadas remotas, consistencia eventual |

## Restricciones por modalidad
- **Self-hosted**: libertad total y responsabilidad total de operación y upgrades.
- **Liferay PaaS**: personalización amplia con operación compartida; revisa las restricciones de la plataforma.
- **Liferay SaaS**: extensión mediante Client Extensions y capacidades low-code; sin módulos OSGi personalizados.
Verifica en la documentación de la modalidad contratada antes de cerrar la decisión.

## Criterios de evaluación
Para cada alternativa: acoplamiento con el portal, ubicación de datos y dueño, consistencia y transacciones, permisos, volumen y latencia, seguridad, operación y quién la opera, despliegue, coste de upgrade y rollback. Para puntuarlas, ejecuta `scripts/decision_matrix.py` con un JSON de criterios (peso 1-3) y valoraciones (1-5): devuelve el total ponderado, el criterio que decide, la sensibilidad y un veredicto de robustez; si no puedes ejecutar scripts, muestra el cálculo paso a paso.

## Arquitectura global
- Diagrama de contexto: usuarios, Liferay, IdP, backends, motor de búsqueda, almacenamiento y terceros.
- Diagrama de contenedores: portal, Client Extensions, servicios externos, datos.
- Contratos: APIs Headless u OpenAPI de servicios, eventos y sus dueños.
- Una responsabilidad clara por pieza; si un servicio externo solo reenvía llamadas, sobra.

## Antipatrones
- Código para lo que resuelve la configuración estándar.
- OSGi o Client Extensions por defecto, sin pasar por la escalera.
- Objects como sustituto universal de un dominio complejo y transaccional.
- Acceso directo a tablas de Liferay.
- Microservicios sin responsabilidad ni equipo que los opere.

## Salida
Documenta la decisión con `templates/adr-template.md`.
Recomendación con el peldaño elegido y por qué se descartan los anteriores, matriz de decisión, diagramas de contexto y contenedores en Mermaid, contratos y dueños, impacto en upgrade, riesgos, plan incremental y ADR.

## Autoevaluación
¿He empezado por la configuración estándar? ¿La decisión dentro o fuera de la JVM está justificada? ¿He verificado lo que permite la modalidad? ¿Cada pieza tiene responsabilidad y dueño? ¿He estimado el coste de upgrade?
