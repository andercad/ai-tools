---
name: liferay-client-extensions-integration
description: 'Asesoría arquitectónica sobre Client Extensions e integraciones de Liferay DXP: tipos de Client Extension (frontend, configuración, microservicio, batch y acciones de Objects, Workflow o notificaciones), aplicaciones Angular como custom elements, servicios Spring Boot y NestJS, Headless REST y GraphQL, OpenAPI, perfiles OAuth2 (User Agent, Headless Server), webhooks, idempotencia, resiliencia, empaquetado, despliegue e integración con IA generativa (enriquecimiento de contenido, RAG). Usar cuando se pregunte qué tipo de Client Extension usar, cómo integrar Liferay con un servicio externo o un frontend Angular, cómo autenticar esas integraciones, cómo desplegarlas y versionarlas o cómo añadir IA generativa al portal. No usar para el diseño interno de Objects u OSGi ni como generador de código.'
---

# Client Extensions e integraciones

## Objetivo
Diseñar integraciones fuera de la JVM del portal con contrato, seguridad, operación y versionado explícitos, usando el tipo de Client Extension adecuado.

## Criterios de decisión: tipo de Client Extension
| Familia | Uso | Cuidado con |
|---|---|---|
| Frontend (custom element, iframe, JS, CSS, tema) | UI en páginas del portal | Convivencia de varias aplicaciones, tamaño del bundle, CSP |
| Configuración (perfiles OAuth2, ajustes de instancia, inicialización de site) | Configuración transportable entre entornos | Secretos fuera del repositorio |
| Microservicio | Lógica externa invocada por acciones o APIs | Operación, disponibilidad, idempotencia |
| Batch | Carga o exportación masiva de datos | Volumen, orden, reintentos, impacto en búsqueda |
| Acciones (Object Action, Workflow Action, Notification Type) | Reaccionar a eventos del portal | Entrega al menos una vez, latencia |
Verifica los tipos y propiedades disponibles en la release y modalidad; la lista evoluciona.

## Integración con Angular
Liferay define mecanismo, contexto (site, idioma, usuario), OAuth2 y permisos; el agente de Angular define la aplicación. Contrato del custom element: atributos o propiedades por instancia, eventos, configuración runtime y dependencias compartidas. Detalle en el agente Angular.

## Integración con Spring Boot y NestJS
Un servicio externo debe aportar responsabilidad real. Requisitos mínimos:
- Contrato OpenAPI versionado y pruebas de contrato.
- OAuth2 con scopes mínimos; perfil User Agent para llamadas en nombre del usuario y Headless Server para servicio a servicio.
- Validación de la firma o del token en las llamadas que Liferay hace al servicio (acciones, webhooks).
- Idempotencia en consumidores de acciones y batch: la entrega puede repetirse.
- Timeouts, reintentos con backoff solo en operaciones idempotentes, circuit breaker y degradación.
- Health checks, métricas, trazas con correlación y logs sin datos sensibles.
- Secretos en un almacén externo, nunca en `client-extension.yaml` ni en la imagen.

## Headless APIs
REST y GraphQL públicos de Liferay aplican permisos del usuario autenticado. Diseña filtros, paginación, campos y agregación para evitar llamadas excesivas. Usa APIs batch para volumen. No uses APIs internas si existe Headless.

## Integración con IA generativa
- Ejecuta la lógica de IA fuera de la JVM del portal (Client Extension de microservicio o servicio externo) y comprueba antes qué capacidades de IA ofrecen la release y la modalidad.
- Enriquecimiento de contenido (resumen, clasificación, traducción) disparado por acciones de Objects o de workflow, con revisión humana antes de publicar.
- **RAG** sobre contenido de Liferay: recupera mediante Headless con la identidad del usuario o filtra por sus permisos; no copies contenido a un almacén vectorial sin trasladar los permisos.
- Mismos requisitos que cualquier integración: OAuth2 con scopes mínimos, idempotencia, timeouts, cuotas y coste. Seguridad en `liferay-security-identity`.

## Empaquetado y despliegue
- Client Extensions definidas en `client-extension.yaml` dentro de Liferay Workspace; build reproducible y versionado.
- No agrupes en un mismo proyecto cargas con ciclos de vida o escalado incompatibles.
- Despliegue y rollback según modalidad: en self-hosted, el cliente opera los servicios externos; en PaaS y SaaS, revisa qué gestiona la plataforma.
- Promoción entre entornos con la misma build y configuración externa.

## Antipatrones
- Servicios proxy sin responsabilidad.
- Credenciales compartidas o un único cliente OAuth2 con todos los scopes.
- Consumidores no idempotentes de acciones o batch.
- Uso de APIs internas existiendo Headless.
- Autorización resuelta solo en el frontend.

## Salida
Para revisar una integración, usa `reference/integration-checklist.md`.
Tipo de Client Extension con justificación, diagrama de integración y de secuencia OAuth2, contratos y dueños, política de seguridad, resiliencia e idempotencia, despliegue, versionado y rollback, riesgos y ADR.

## Autoevaluación
¿El tipo elegido es el más simple que cumple? ¿Cada servicio externo tiene responsabilidad y operador? ¿Los scopes son mínimos? ¿Los consumidores son idempotentes? ¿He verificado los tipos disponibles en la release y la modalidad?
