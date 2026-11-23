---
name: liferay-architecture-assessment
description: 'Evalúa la arquitectura de una instalación Liferay DXP existente o propuesta: descubrimiento, inventario de customizaciones (módulos OSGi, Service Builder, overrides, temas, Client Extensions), deuda técnica y de upgrade, riesgos, NFR, production readiness y diagnóstico basado en evidencia de problemas recurrentes (rendimiento, búsqueda, despliegues, integraciones). Usar cuando se pida revisar, auditar o diagnosticar una instalación Liferay, evaluar su salud arquitectónica, priorizar deuda, preparar un due diligence técnico, decidir por dónde empezar o analizar un incidente recurrente que apunte a un problema de diseño. No usar para decisiones de mecanismo concretas, para depurar un módulo línea a línea ni como generador de código.'
---

# Evaluación y diagnóstico de arquitectura Liferay

## Objetivo
Obtener una imagen fiable de la plataforma y sus customizaciones, separando hechos con evidencia de supuestos, y priorizar riesgos y deuda según su impacto en negocio, operación y upgrades.

## Descubrimiento
Material que pedir, en orden de valor:
1. Producto, modalidad (self-hosted, PaaS, SaaS) y release exacta.
2. Inventario de customizaciones: módulos OSGi, Service Builder, overrides (JSP, servicios, `ext`), temas, Client Extensions, Objects, Fragments.
3. Topología: nodos, base de datos, motor de búsqueda, almacenamiento de documentos, balanceador y sesiones.
4. `portal-ext.properties` y configuraciones OSGi relevantes (sin secretos).
5. Integraciones (identidad, APIs externas, batch) y volumen (usuarios, contenidos, documentos).
6. Métricas, logs de incidentes y pipeline de despliegue.
Sin material: como máximo 3 preguntas aclaratorias y supuestos etiquetados.

## Dimensiones de evaluación
| Dimensión | Qué revisar | Señales de alerta |
|---|---|---|
| Release y soporte | Release frente a soporte vigente; distancia a la última LTS | Release sin soporte, upgrades aplazados |
| Capacidades en maintenance mode o deprecadas | Uso de Web Content, Documents and Media, Publications, Widget Pages, segmentos locales u otras capacidades señaladas en las notas de la release | Proyectos nuevos sobre ellas o ausencia de plan de transición |
| Customizaciones | Tipo, número, motivo y alternativa estándar actual | Overrides de JSP o `ext`, uso de APIs internas, acceso a tablas |
| Mecanismos | ¿Se usó el mecanismo más simple disponible hoy? | Service Builder para modelos que Objects cubre, OSGi para lógica externalizable |
| Integraciones | Contratos, OAuth2, idempotencia, resiliencia | Credenciales compartidas, llamadas síncronas en cadena |
| Contenido y búsqueda | Modelo de contenido, taxonomía, salud de índices | Estructuras duplicadas, reindexaciones frecuentes |
| Seguridad y permisos | Roles, mínimo privilegio, SSO, auditoría | Administradores en exceso, permisos por usuario individual |
| Operación | Cluster, sesiones, almacenamiento compartido, observabilidad, backup y restore probados | Estado local en nodos, sin restore probado |
| Entrega | Build reproducible, configuración como código, rollback | Cambios manuales en producción |

## Diagnóstico de problemas recurrentes
1. Impacto, alcance y timeline.
2. Separa capas: navegador, portal, OSGi, Client Extensions, base de datos, búsqueda, almacenamiento, red, infraestructura y terceros.
3. Correlaciona logs, thread dumps, métricas y trazas en la misma ventana temporal.
4. Hipótesis ordenadas y prueba discriminante para cada una; causa confirmada solo con evidencia.
5. Cambio mínimo reversible y prevención.

## Antipatrones a detectar
- Customización que sustituye una capacidad estándar disponible.
- Acceso directo a tablas de Liferay o uso de APIs internas.
- Estado en disco local de nodos en cluster.
- Microservicios sin responsabilidad clara.
- Deuda de upgrade acumulada por overrides.

## Criterios de decisión: priorización
Hallazgos BLOCKER, MAJOR, MINOR u OPCIONAL; BLOCKER y MAJOR con evidencia. Ordena por impacto frente a esfuerzo y por coste de upgrade evitado. Asigna cada hallazgo a la skill que desarrolla la solución.

## Salida
Usa `templates/assessment-report.md` como estructura del informe.
Resumen ejecutivo con los tres riesgos principales; inventario de customizaciones `Customización | Tipo | Motivo | Alternativa estándar | Coste de upgrade | Recomendación`; tabla de hallazgos con evidencia y severidad; lo no verificado; deuda priorizada y roadmap 30/60/90 con criterios de aceptación.

## Autoevaluación
¿Cada hallazgo grave tiene evidencia? ¿He separado hechos de supuestos? ¿He propuesto alternativas estándar para las customizaciones? ¿He considerado el coste de upgrade? ¿El roadmap es incremental y reversible?
