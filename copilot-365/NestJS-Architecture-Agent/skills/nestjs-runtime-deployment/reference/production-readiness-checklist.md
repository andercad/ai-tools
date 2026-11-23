# Checklist de preparación para producción (NestJS)

Marca Cumple / No cumple / No verificado y cita la evidencia.

## Runtime
- [ ] Versión LTS de Node soportada, alineada con NestJS y la imagen base.
- [ ] Trabajo intensivo de CPU fuera del event loop (workers, colas).
- [ ] Límite de memoria del contenedor y heap de V8 alineados.
- [ ] Configuración validada al arranque. Falla rápido si falta algo.

## Contenedor
- [ ] Build multietapa, imagen mínima fijada, usuario no root.
- [ ] Solo dependencias de producción. `.dockerignore`.
- [ ] Arranque con `node dist/main.js` (señales al proceso principal).
- [ ] Escaneo de vulnerabilidades y tags inmutables.

## Ciclo de vida
- [ ] `enableShutdownHooks()` y gestión de `SIGTERM` con drenaje de peticiones, consumidores y conexiones.
- [ ] Tiempo de gracia de la plataforma mayor que el tiempo de drenaje.
- [ ] Liveness sin dependencias externas. Readiness con dependencias imprescindibles. Startup probe si el arranque es lento.

## Escalado y disponibilidad
- [ ] Aplicación sin estado. Sesión y caché fuera del proceso.
- [ ] Mínimo 2 réplicas en zonas distintas si el SLO lo requiere.
- [ ] Regla de autoescalado según el patrón (CPU, concurrencia, longitud de cola, lag).
- [ ] Pool de conexiones x réplicas máximas no supera el límite de la BD.

## Despliegue
- [ ] Pipeline con lint, tests, build, escaneo, smoke tests y promoción entre entornos.
- [ ] Estrategia (rolling/blue-green/canary) y rollback probado.
- [ ] Migraciones de BD compatibles hacia atrás (expand/contract), ejecutadas antes del código que las necesita.
- [ ] Infraestructura como código y entornos reproducibles.

## Seguridad operativa
- [ ] Secretos desde un secret store con identidad gestionada.
- [ ] Red: endpoints privados para BD/broker, exposición pública solo a través de gateway/WAF.

## Recuperación
- [ ] RTO/RPO definidos. Backups automáticos y restauración probada.
- [ ] Runbooks para fallos comunes (BD caída, broker caído, despliegue fallido).

## Observabilidad mínima
- [ ] Logs estructurados con correlación, métricas RED y de runtime, trazas.
- [ ] Alertas por síntomas/SLO con responsable.
