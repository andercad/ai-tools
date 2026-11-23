---
name: angular-backend-integration
description: 'Asesoría arquitectónica sobre la integración de Angular con backends Spring Boot y NestJS: responsabilidad del backend y patrón BFF, flujos OAuth2/OIDC para SPA (BFF con cookies frente a Authorization Code con PKCE en el navegador), Microsoft Entra ID, contratos OpenAPI y generación de clientes, capa HTTP e interceptores, modelo de errores (Problem Details), timeouts, reintentos e idempotencia, paginación, tiempo real (WebSocket, SSE), CORS y funcionalidades con IA generativa (llamadas a través del BFF, streaming de respuestas). Usar cuando se pregunte cómo conectar el frontend con una API, qué flujo de autenticación usar en una SPA, si hace falta un BFF, cómo tipar y versionar el contrato, cómo gestionar errores y reintentos en el cliente o cómo integrar un asistente de IA generativa. No usar para diseñar el interior del backend ni como generador de código.'
---

# Integración con backends

## Objetivo
Definir cómo el frontend se comunica con sus backends de forma segura, tipada y resiliente, con responsabilidades claras entre cliente, BFF y servicios. El diseño interno del backend corresponde a los agentes de Spring Boot o NestJS.

## Criterios de decisión: ¿hace falta BFF?
| Opción | Encaja cuando | Coste |
|---|---|---|
| SPA contra APIs directamente | Una API, tokens de vida corta, riesgo aceptado de tokens en el navegador | Gestión de tokens en cliente, CORS |
| BFF (NestJS o Spring Boot) | Datos sensibles, requisito de no exponer tokens al navegador, agregación para la UI, varios backends | Una pieza más que operar y escalar |
| API gateway | Políticas transversales (rate limiting, enrutado) sin lógica de UI | No sustituye al BFF para sesiones |
Un BFF debe tener responsabilidad real (sesión, agregación, adaptación a la UI). Un proxy sin responsabilidad es un antipatrón.

## Autenticación en SPA
| Flujo | Ventajas | Riesgos |
|---|---|---|
| BFF con cookie de sesión (`HttpOnly`, `Secure`, `SameSite`) | Tokens fuera del navegador; recomendado por las guías actuales de OAuth para aplicaciones de navegador | Requiere CSRF y BFF |
| Authorization Code con PKCE en el navegador | Sin BFF; soportado por Entra ID y la mayoría de IdP | Tokens accesibles por XSS; renovación silenciosa afectada por cookies de terceros |
Nunca uses el flujo implícito. Con PKCE, tokens en memoria y de vida corta. No inventes claims, scopes ni endpoints del IdP: verifica en su documentación.

## Contratos
- Contract-first con OpenAPI cuando hay varios equipos o consumidores; genera el cliente y los tipos en lugar de duplicar DTO a mano (verifica el generador elegido y su mantenimiento).
- Versionado: cambios aditivos por defecto, deprecación anunciada, versión nueva solo ante ruptura.
- Pruebas de contrato (esquema o consumer-driven) en el pipeline de ambos lados.
- Mapea DTO a modelos de vista solo si la forma de la UI difiere de forma estable de la API.

## Capa HTTP
- Interceptores funcionales para autenticación, correlación (traceparent o id de correlación) y traducción de errores; sin lógica de negocio.
- Acceso a datos por feature, separado de los componentes.
- Errores: el backend devuelve Problem Details (RFC 9457); el cliente los traduce a mensajes y estados de UI coherentes.
- Timeouts explícitos y cancelación al abandonar la pantalla.
- Reintentos con backoff solo en operaciones idempotentes; para escrituras críticas, clave de idempotencia acordada con el backend.
- Paginación por cursor para listados grandes o cambiantes; offset para listados pequeños y estables.

## Tiempo real
| Opción | Encaja cuando |
|---|---|
| Polling | Cambios poco frecuentes, simplicidad |
| Server-Sent Events | Flujo servidor → cliente, notificaciones |
| WebSocket | Bidireccional y baja latencia |
Considera reconexión, autenticación del canal, escalado del servidor y comportamiento detrás de proxies.

## Funcionalidades con IA generativa
- El navegador nunca llama al proveedor del modelo con credenciales: la llamada pasa por el BFF o el backend, que decide qué datos ve el modelo, aplica cuotas por usuario y registra el coste.
- Streaming de respuestas (SSE o `fetch` con streams) con cancelación al abandonar la pantalla o al enviar otra pregunta.
- UX de latencia y error: respuesta parcial, opción de detener y reintentar, y mensajes claros cuando el servicio de IA no está disponible.
- Contrato explícito también aquí: formato de mensajes, citas a las fuentes y salida estructurada validada. Presentación segura del contenido generado en `angular-quality-security`.

## CORS
Es una política del servidor, no una medida de seguridad del cliente. Evítalo con mismo origen (BFF o reverse proxy). Si es necesario, lista explícita de orígenes, nunca comodín con credenciales.

## Antipatrones
- BFF que solo reenvía peticiones.
- Tokens en `localStorage`; flujo implícito.
- Reintentar POST sin idempotencia.
- Lógica de negocio duplicada en el frontend.
- APIs muy conversacionales (chatty) que obligan a la UI a orquestar muchas llamadas.

## Salida
Para revisar una integración, usa `reference/integration-contract-checklist.md`.
Decisión sobre BFF con matriz, diagrama de secuencia de autenticación, gobierno del contrato (formato, generación, versionado, pruebas), política de errores, timeouts y reintentos, riesgos y qué debe decidir el equipo de backend (con remisión al agente correspondiente).

## Autoevaluación
¿El BFF tiene responsabilidad real o lo he descartado con motivo? ¿El flujo de autenticación evita tokens en almacenamiento persistente? ¿Los reintentos son solo idempotentes? ¿El contrato tiene dueño y pruebas? ¿He inventado algún dato del IdP?
