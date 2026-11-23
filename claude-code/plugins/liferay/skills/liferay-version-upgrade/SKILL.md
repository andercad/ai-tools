---
name: liferay-version-upgrade
description: 'Asesoría arquitectónica sobre releases y upgrades de Liferay DXP: modelo de Quarterly Releases y LTS, política de soporte, Compatibility Matrix (Java, servidor de aplicaciones, base de datos, motor de búsqueda), Liferay Workspace y Gradle, breaking changes y deprecaciones, feature flags, inventario y adaptación de customizaciones, upgrade de base de datos, ensayos, criterios go/no-go y rollback. Usar cuando se pregunte a qué release ir, cuál es la última o la LTS, qué riesgo tiene quedarse en una versión, cómo planificar un upgrade o qué impacto tendrá en las customizaciones e integraciones. No usar para ejecutar el upgrade ni como generador de código.'
---

# Releases y upgrades

## Objetivo
Decidir la release objetivo y planificar un upgrade con riesgo controlado, ensayado y reversible, basado en fuentes oficiales y en el inventario real de customizaciones.

## Modelo de releases
- Liferay DXP publica Quarterly Releases; algunas se designan LTS con soporte más largo. Las versiones 7.x anteriores usaban otro modelo de actualizaciones.
- No infieras compatibilidad ni fechas: consulta las notas de la release, la política de soporte y la Compatibility Matrix vigentes.
- No mezcles Quarterly Releases con actualizaciones de 7.4 ni APIs de generaciones distintas.

## Criterios de decisión: release objetivo
| Opción | Encaja cuando | Cuidado con |
|---|---|---|
| Última LTS | Estabilidad y ciclos de upgrade largos | Capacidades más recientes no incluidas |
| Última Quarterly Release | Necesidad de capacidades nuevas y equipo que actualiza con frecuencia | Upgrades más frecuentes |
| Mantener la actual | Dentro de soporte y sin drivers | Acumular distancia aumenta el coste futuro |

## Feature flags
Algunas capacidades se publican tras feature flags (por ejemplo, Beta o Release). No diseñes sobre una capacidad Beta en producción sin aceptar el riesgo de forma explícita.

Distingue **maintenance mode** (sigue soportado, sin evolución funcional) de **deprecado** (se retirará en una release futura). Algunas capacidades deprecadas solo siguen disponibles mediante deprecation feature flags, que pueden estar activados en instalaciones actualizadas y desactivados en las nuevas: verifícalo flag a flag e inventárialos antes del upgrade.

## Evaluación de impacto
1. Origen, destino y modalidad.
2. Compatibilidad de Java, servidor de aplicaciones, base de datos y motor de búsqueda en la Compatibility Matrix.
3. Inventario de customizaciones: módulos OSGi, Service Builder, overrides, temas, Client Extensions, Objects, Fragments e integraciones.
4. Breaking changes, capacidades en maintenance mode y deprecaciones que afectan a cada customización y al contenido.
5. Clasificación: compatible, requiere cambio, requiere rediseño (sustituir por capacidad estándar o Client Extension), retirar.
Matriz `Customización | Impacto | Acción | Esfuerzo | Riesgo`.

## Plan de upgrade
- Actualiza Liferay Workspace, versión de producto y dependencias de Gradle; usa las herramientas oficiales de ayuda al upgrade de código.
- Upgrade de base de datos con la herramienta oficial sobre una copia reciente de producción; mide la duración.
- Reindexación tras el upgrade y validación de búsqueda.
- Ensayos completos (al menos uno) con datos reales: contenido, permisos, workflows, integraciones, búsqueda, rendimiento.
- Pruebas de regresión y de caracterización de los recorridos críticos.
- Criterios go/no-go explícitos y ventana de corte con comunicación.

## Rollback
El upgrade de base de datos no es reversible: el rollback consiste en volver al backup previo y a la versión anterior. Define el punto de no retorno, la retención de backups y el tiempo de vuelta atrás medido en el ensayo.

## Antipatrones
- Asumir compatibilidad entre releases sin consultar la matriz.
- Mezclar el upgrade con nuevas funcionalidades.
- Upgrade sin ensayo con datos reales.
- Mantener overrides cuando existe alternativa estándar en el destino.
- Ignorar la reindexación y el rendimiento tras el upgrade.

## Salida
Usa `templates/upgrade-assessment.md` para la evaluación y el plan.
Recomendación de release objetivo, matriz de compatibilidad, inventario y clasificación de customizaciones, plan por fases con ensayos, criterios go/no-go, plan de rollback, riesgos y ADR.

## Autoevaluación
¿He verificado release, soporte y compatibilidades en fuentes oficiales? ¿El inventario de customizaciones está completo? ¿Hay al menos un ensayo con datos reales? ¿El rollback y el punto de no retorno están definidos? ¿He separado upgrade y nuevas funcionalidades?
