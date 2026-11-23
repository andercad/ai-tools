---
name: nestjs-runtime-deployment
description: 'Asesoría arquitectónica sobre runtime Node.js, contenedores, cloud y despliegue de aplicaciones NestJS. Usar cuando se pida elegir plataforma (Azure Container Apps, App Service, AKS/Kubernetes, Functions/serverless), diseñar Docker, escalado, alta disponibilidad, probes de health, graceful shutdown, configuración y secretos por entorno, estrategia de despliegue (rolling, blue/green, canary), CI/CD, recuperación ante desastres, tamaño de instancias o uso de memoria/CPU en Node. No usar como generador de código por defecto.'
---

# Runtime Node, cloud y despliegue

## Objetivo
Elegir plataforma y estrategia de ejecución según NFR (disponibilidad, escalado, coste, equipo de operaciones). No presupone Kubernetes.

## Elección de plataforma
| Plataforma | Encaja cuando | Cuidado con |
|---|---|---|
| App Service / PaaS web | Una o pocas APIs, equipo pequeño, poca operación | Menos control de red y de runtime, límites del plan |
| Container Apps / servicios de contenedores gestionados | Varias APIs/workers, escalado por eventos o HTTP, sin querer operar un clúster | Límites de la plataforma, networking avanzado |
| AKS/Kubernetes | Muchos servicios, requisitos de plataforma propios, equipo de plataforma | Coste operativo alto: exige equipo y madurez. No lo recomiendes por defecto |
| Serverless (Functions/Lambda) | Cargas esporádicas o guiadas por eventos | Cold start, límites de duración, conexiones a BD, empaquetado de NestJS (cachea la instancia de la app entre invocaciones) |
Criterios: perfil de tráfico, estado, latencia, cumplimiento y residencia de datos, habilidades del equipo, coste total y portabilidad real necesaria. Compara siempre con la opción gestionada más simple.

## Node.js como runtime
- Node ejecuta JavaScript en un hilo: el trabajo intensivo de CPU bloquea el event loop. Sácalo a worker threads, un proceso/cola de trabajo o un servicio aparte.
- Escala **horizontalmente con réplicas** (contenedores/instancias). Usa `cluster` o PM2 solo si la plataforma no puede escalar réplicas. Dentro de un contenedor, una réplica por proceso suele ser lo más simple.
- Usa solo versiones **LTS soportadas** de Node: consulta el calendario oficial de releases, porque el fin de soporte condiciona la versión de NestJS y la imagen base.
- Memoria: fija el límite del contenedor y alinea el heap de V8 (`--max-old-space-size`) con él, dejando margen para memoria nativa. Monitoriza heap, RSS y GC.
- Fastify frente a Express: Fastify suele dar más rendimiento. Valora el cambio solo con medición y comprobando compatibilidad de librerías.

## Contenedores
- Build multietapa, imagen base mínima y fijada (por digest o versión), usuario no root, `NODE_ENV=production`, solo dependencias de producción, `.dockerignore`.
- Arranca con `node dist/main.js` (no `npm start`) para que las señales lleguen al proceso. Usa `--init`/tini si hace falta.
- Escaneo de vulnerabilidades de la imagen en CI, SBOM, tags inmutables.

## Ciclo de vida: probes y shutdown
- `app.enableShutdownHooks()` y gestión de `SIGTERM`: dejar de aceptar tráfico, terminar peticiones en curso, cerrar conexiones (BD, broker) y consumidores, dentro del `terminationGracePeriod`.
- **Liveness** barata: solo indica que el proceso responde, sin comprobar dependencias. **Readiness** verifica lo imprescindible para servir tráfico. **Startup probe** para arranques lentos. `@nestjs/terminus` ofrece indicadores. Si la liveness comprueba la BD, una caída de BD reinicia todas las réplicas en cascada.
- Los workers de colas deben poder pausarse y drenar antes de detenerse.

## Configuración y secretos
Configuración externa por entorno (12-factor) con `@nestjs/config` y validación al arranque (falla rápido si falta algo). Misma imagen en todos los entornos. Secretos desde Key Vault/secret store con identidad gestionada, nunca en la imagen ni en variables versionadas.

## Escalado y disponibilidad
Aplicación sin estado (sesiones y caché fuera del proceso). Escalado por CPU, concurrencia HTTP, longitud de cola o lag del consumidor según el patrón. Mínimo de 2 réplicas en distintas zonas de disponibilidad para alta disponibilidad. Define RTO/RPO, backups y restauración probada, y pruebas de recuperación. Multi-región solo si el NFR lo exige y se asume el coste de datos.

## Despliegue y CI/CD
Pipeline: lint, tests, build, escaneo, imagen, despliegue a entorno de pruebas, smoke tests, promoción. Estrategias: rolling (por defecto), blue/green o canary si el riesgo lo justifica. Rollback automático por métricas. **Migraciones de BD compatibles hacia atrás** (expand/contract) para poder revertir la aplicación. Infraestructura como código (Bicep/Terraform) y entornos reproducibles.

## Salida
Para revisar si un servicio está listo para producción, usa `reference/production-readiness-checklist.md`.
Plataforma recomendada con criterios y alternativa más simple, topología (diagrama de despliegue), dimensionado inicial a validar con pruebas, probes y shutdown, configuración, pipeline y estrategia de despliegue/rollback, HA/DR, coste relativo (marcando cifras como pendientes de verificar) y ADR.

## Autoevaluación
¿Se justifica la complejidad de la plataforma? ¿Hay graceful shutdown y probes correctas? ¿Es sin estado? ¿Hay rollback con esquema compatible? ¿Se han marcado como pendientes los costes y límites no verificados?
