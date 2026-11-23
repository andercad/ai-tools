---
name: liferay-cloud-operations
description: 'Asesoría arquitectónica sobre operación de Liferay DXP: elección de modalidad (self-hosted, Liferay PaaS, Liferay SaaS), contenedores Docker, Kubernetes y AKS, cluster, sesiones y balanceo, almacenamiento compartido, base de datos, motor de búsqueda, configuración por entorno, probes (liveness, readiness, startup), dimensionado de JVM y pools, rendimiento y pruebas de carga, observabilidad, CI/CD, backup, restore, DR y rollback. Usar cuando se pregunte dónde y cómo ejecutar Liferay, cómo escalarlo, cómo desplegarlo con seguridad, cómo dimensionarlo, cómo observarlo o cómo recuperarse ante un desastre. No usar como generador de manifiestos ni para presuponer Kubernetes.'
---

# Operación, plataforma y continuidad

## Objetivo
Elegir la plataforma y la topología que cumplen los NFR con el menor coste operativo, y garantizar escalado, observabilidad, despliegues seguros y recuperación probada.

## Criterios de decisión: modalidad y plataforma
| Opción | Encaja cuando | Coste |
|---|---|---|
| Liferay SaaS | Se acepta el modelo de extensión por Client Extensions y low-code; se prioriza no operar | Menos libertad de customización |
| Liferay PaaS | Customización amplia con operación compartida | Restricciones de la plataforma |
| Self-hosted en VM | Equipo con experiencia en Java y poca experiencia en contenedores | Automatización propia |
| Self-hosted en Kubernetes (por ejemplo, AKS) | Plataforma de contenedores existente y equipo que la opera | Complejidad: estado, almacenamiento, upgrades |
No presupongas Kubernetes: empieza por la opción más simple que cumple disponibilidad y escalado.

## Topología
- Componentes: nodos del portal, base de datos, motor de búsqueda externo, almacenamiento de documentos compartido, balanceador, Client Extensions de microservicio y sus dependencias.
- Cluster: nodos sin estado local; caché y comunicación de cluster configuradas según la release; afinidad de sesión en el balanceador, o la alternativa que soporte la release, verificada.
- Estado: base de datos, almacenamiento de documentos y búsqueda fuera de los nodos. No escales pods sin resolver antes el estado compartido.
- Versiones de Java, base de datos y motor de búsqueda según la Compatibility Matrix.

## Configuración y despliegue
- Una imagen por versión, promovida entre entornos; configuración por entorno con variables y ficheros de configuración externos; secretos en un almacén gestionado.
- Configuración como código e infraestructura como código.
- Probes: `startup` para el arranque largo, `readiness` para recibir tráfico y `liveness` conservadora para no reiniciar nodos sanos en cascada.
- Despliegues graduales con criterios de salud; rollback de aplicación compatible con el esquema de base de datos.
- Las Client Extensions de microservicio tienen su propio ciclo de despliegue y observabilidad.

## Rendimiento y capacidad
- Define SLO (latencia, disponibilidad, errores) por tipo de página o API.
- Pruebas de carga con escenarios reales (usuarios autenticados, búsqueda, documentos) antes de ajustar.
- No ajustes JVM, GC ni pools sin evidencia (métricas, GC logs, thread dumps); el pool de conexiones total no debe superar la capacidad de la base de datos.
- Caché de contenido y CDN para recursos estáticos y páginas públicas.

## Observabilidad
Logs estructurados centralizados, métricas de JVM, pools, peticiones y búsqueda, trazas con correlación entre portal y servicios externos, dashboards por SLO y alertas por síntoma.

## Backup, restore y DR
- Backup coherente de base de datos y almacenamiento de documentos; la búsqueda se reconstruye por reindexación (mide cuánto tarda).
- Restore probado periódicamente con RPO y RTO medidos.
- DR: región secundaria o procedimiento de reconstrucción según criticidad y coste.

## Antipatrones
- Escalar nodos con estado local.
- Build distinto por entorno o cambios manuales en producción.
- Liveness agresiva que reinicia nodos durante el arranque.
- Ajustes de JVM copiados sin medición.
- Backups nunca restaurados.

## Salida
Antes de producción, revisa `reference/production-readiness-checklist.md`.
Decisión de modalidad y plataforma con matriz, diagrama de topología, configuración y secretos, estrategia de probes y despliegue, SLO y dashboards, plan de capacidad y pruebas de carga, backup, restore, DR y rollback, riesgos y ADR.

## Autoevaluación
¿He elegido la plataforma más simple que cumple? ¿Los nodos son realmente sin estado? ¿Las versiones están verificadas en la Compatibility Matrix? ¿Hay evidencia para cada ajuste de rendimiento? ¿El restore está probado con RPO y RTO?
