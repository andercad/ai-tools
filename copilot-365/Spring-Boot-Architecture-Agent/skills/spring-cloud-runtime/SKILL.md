---
name: spring-cloud-runtime
description: 'Asesoría arquitectónica sobre runtime, empaquetado y despliegue de Spring Boot: JVM frente a native image, contenedores, Kubernetes/AKS, Azure Container Apps, App Service, serverless, configuración externa, perfiles, probes, graceful shutdown, escalado, dimensionado, alta disponibilidad, estrategias de despliegue y disaster recovery; y cuándo Spring Cloud aporta valor. Usar cuando se pregunte dónde y cómo ejecutar una aplicación Spring Boot, cómo configurarla por entorno, cómo escalarla o cómo desplegarla sin downtime. No usar como generador de código ni para presuponer Kubernetes.'
---

# Runtime, cloud y despliegue

## Objetivo
Elegir plataforma y forma de ejecución adecuadas al equipo, la carga y la criticidad, con despliegues seguros y reversibles.

## Plataforma: criterios de decisión
| Opción | Encaja cuando | Coste principal |
|---|---|---|
| PaaS simple (App Service, equivalente) | Pocas apps, equipo pequeño, requisitos estándar | Menos control de red y runtime |
| Contenedores gestionados (Azure Container Apps, equivalente) | Varias apps, escalado por eventos/HTTP, sin querer operar Kubernetes | Menos flexibilidad que K8s |
| Kubernetes/AKS | Muchos servicios, necesidades de red/políticas avanzadas, plataforma interna con equipo dedicado | Complejidad operativa alta |
| Serverless (funciones) | Cargas esporádicas y cortas | Arranque en frío, límites de runtime; Spring completo rara vez encaja |
| VM / despliegue clásico | Restricciones heredadas o de licencia | Operación manual, escalado lento |
Empieza por la opción más simple que cumpla los NFR; justifica explícitamente subir de nivel.

## JVM frente a native image
- JVM: por defecto; mejor compatibilidad, observabilidad y herramientas.
- Native (GraalVM): considera si el arranque rápido o la memoria reducida son requisitos medibles (escala a cero, funciones). Coste: tiempos de build, reflexión/proxies que requieren hints, menos compatibilidad de librerías, depuración distinta. Valida con pruebas en modo nativo; no lo asumas.
- Antes de native, valora CDS/AppCDS, ajuste de JVM y, si la versión lo soporta, hilos virtuales para concurrencia bloqueante (verifica compatibilidad en la versión instalada).

## Contenedores
- Imagen mínima y reproducible (capas de Spring Boot o buildpacks), usuario no root, sin secretos embebidos, escaneo de vulnerabilidades.
- Memoria y CPU: fija límites y deja que la JVM los respete; deja margen para memoria no-heap. Dimensiona con pruebas de carga, no por intuición.

## Configuración
- Configuración externa por entorno (variables, ConfigMap/App Configuration), secretos en gestor dedicado, misma imagen para todos los entornos.
- Perfiles solo para variaciones reales; evita lógica de negocio condicionada por perfil.
- Spring Cloud Config, Consul u otros solo si resuelven un problema que la plataforma no resuelva ya. Con Kubernetes o similares prefiere los mecanismos nativos.

## Ciclo de vida y fiabilidad
- Probes de **liveness** y **readiness** separados (Actuator health groups). Liveness no debe depender de servicios externos.
- **Graceful shutdown** (`server.shutdown=graceful`) y ventana de terminación alineada con el tiempo de petición más largo y con el balanceador.
- Mínimo dos réplicas con distribución por zonas para alta disponibilidad; presupuesto de interrupción.
- Escalado horizontal solo si la aplicación es sin estado (sesión externa o sticky justificado); define métricas de escalado y límites.
- Descubrimiento y balanceo: con plataformas que ya los ofrecen, evita duplicarlos con Spring Cloud.

## Despliegue y recuperación
- Estrategia: rolling por defecto; blue/green o canary cuando el riesgo o el coste de fallo lo justifique.
- Compatibilidad de base de datos y mensajes entre versiones (expand/contract) para poder revertir.
- Rollback probado, feature flags para desacoplar despliegue de activación.
- DR: RPO/RTO acordados, copias, región secundaria solo si el requisito de negocio lo exige; prueba periódica.
- Coste: estima de forma relativa y marca cifras concretas como pendientes de verificar con la calculadora de precios del proveedor.

## Salida
Antes de producción, revisa `reference/production-readiness-checklist.md`.
Plataforma recomendada con alternativas, modelo de runtime, configuración y secretos, topología de despliegue, estrategia de release y rollback, DR, riesgos operativos y ADR.

## Autoevaluación
Comprueba que no se impuso Kubernetes ni native sin driver, que el estado y la configuración están externalizados, que existen probes, shutdown y rollback, y que los costes no son cifras inventadas.
