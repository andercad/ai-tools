# Checklist de preparación para producción de Liferay

Marca cada punto como Cumple / No cumple / No verificado / No aplica y cita la evidencia. «No verificado» nunca equivale a «Cumple».

## Plataforma y versiones
- [ ] Modalidad elegida con justificación (SaaS, PaaS, self-hosted en VM o en Kubernetes).
- [ ] Java, servidor de aplicaciones, base de datos y motor de búsqueda dentro de la Compatibility Matrix de la release.

## Estado y topología
- [ ] Nodos sin estado local: documentos en almacenamiento compartido, búsqueda externa, base de datos gestionada o redundante.
- [ ] Cluster configurado según la release y verificado con varios nodos.
- [ ] Afinidad de sesión, o alternativa soportada por la release, verificada.
- [ ] Búsqueda en modo remoto, con autenticación y TLS.

## Configuración y despliegue
- [ ] Una imagen por versión promovida entre entornos; configuración por entorno externa.
- [ ] Secretos en almacén gestionado; nada en `portal-ext.properties` versionado ni en la imagen.
- [ ] Configuración e infraestructura como código; sin cambios manuales en producción.
- [ ] Probes: de arranque tolerante al arranque largo, readiness para recibir tráfico y liveness conservadora.
- [ ] Despliegue gradual con criterios de salud y rollback compatible con el esquema.

## Rendimiento y capacidad
- [ ] SLO definidos por tipo de página o API.
- [ ] Pruebas de carga con escenarios reales (usuarios autenticados, búsqueda, documentos).
- [ ] Ajustes de JVM, GC y pools basados en evidencia; pools totales dentro de la capacidad de la base de datos.
- [ ] CDN y caché para recursos estáticos y páginas públicas.

## Observabilidad
- [ ] Logs centralizados y estructurados, sin datos sensibles.
- [ ] Métricas de JVM, pools, peticiones y búsqueda; trazas con correlación hacia servicios externos.
- [ ] Alertas por síntoma con runbook y responsable.

## Continuidad
- [ ] Backup coherente de base de datos y documentos.
- [ ] Restore probado con RPO y RTO medidos; tiempo de reindexación conocido.
- [ ] Procedimiento de DR documentado y ensayado según la criticidad.

## Resultado
Bloqueantes para producción, riesgos aceptados con responsable y acciones con fecha.
