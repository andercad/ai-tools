---
name: nestjs-security-identity
description: 'Asesoría arquitectónica sobre seguridad, identidad y exposición en NestJS. Usar cuando se pida diseñar o revisar autenticación y autorización, JWT, OAuth 2.0/OIDC, Microsoft Entra ID, Passport, guards, roles/permisos/ABAC, multi-tenant, OWASP API Top 10, threat modeling, CORS, Helmet, rate limiting, secretos, SSRF, subida de ficheros, mTLS, seguridad de dependencias, seguridad de aplicaciones con IA generativa (OWASP Top 10 para LLM) o normativa UE (RGPD, ENS, NIS2, DORA, AI Act). No usar como generador de código por defecto.'
---

# Seguridad, identidad y exposición

## Objetivo
Diseñar identidad y controles de seguridad proporcionados al riesgo. No cierres ninguna recomendación sin indicar el control, dónde se aplica y cómo se verifica.

## 1. Modelo de amenazas (siempre primero)
Identifica activos, actores, fronteras de confianza y superficies (API pública, admin, interna, webhooks, mensajería). Usa STRIDE o similar y OWASP API Security Top 10 como checklist: autorización a nivel de objeto (BOLA), autenticación rota, autorización a nivel de propiedad, consumo sin límites, autorización a nivel de función, flujos de negocio sensibles, SSRF, configuración insegura, inventario de APIs y consumo inseguro de APIs de terceros.

## 2. Autenticación
- Prefiere un proveedor de identidad (Entra ID, Keycloak, Auth0, etc.) con OIDC/OAuth 2.0 antes que gestionar credenciales propias.
- Flujos: Authorization Code + PKCE para usuarios, Client Credentials para máquina a máquina, On-Behalf-Of cuando una API llama a otra en nombre del usuario. No uses Implicit ni Password.
- SPA con API propia: valora un **BFF** con cookies `HttpOnly`/`Secure`/`SameSite` en lugar de tokens en el navegador. Con cookies, exige protección CSRF.
- Validación de JWT: verificar firma con JWKS en caché, algoritmo fijado, `iss`, `aud`, `exp`/`nbf` y tenant. Access tokens de vida corta. Refresh tokens con rotación y detección de reutilización. Estrategia de revocación o "kill switch" explícita.
- Passport es un adaptador, no la arquitectura. La validación debe ser idéntica en todos los transportes (HTTP, GraphQL, WebSocket, microservicios).
- mTLS o identidad gestionada (managed identity/workload identity) para servicio a servicio.

## 3. Autorización
- **Denegar por defecto**: guard global (`APP_GUARD`) y excepción explícita para rutas públicas (`@Public()`).
- Modelo según complejidad: RBAC simple, ABAC/ReBAC para reglas por recurso o propietario, o motor de políticas externo (OPA, Cedar, Casbin) si las reglas cambian a menudo.
- La autorización por recurso (propiedad, tenant) se aplica **en el caso de uso/repositorio**, no solo en el guard, para evitar BOLA. En multi-tenant, el `tenantId` sale del token y filtra todas las consultas. Considera Row-Level Security.
- Guards, interceptores y pipes deben usar el contexto correcto (HTTP, GraphQL, RPC, WS) o no se aplicarán.

## 4. Exposición y entrada
- `ValidationPipe` global con `whitelist`, `forbidNonWhitelisted` y `transform`. Valida también mensajes de brokers y webhooks.
- Helmet, CORS con lista explícita de orígenes (nunca `*` con credenciales), límites de tamaño de body, timeouts.
- Rate limiting con `@nestjs/throttler` (almacén compartido como Redis con varias instancias) y también en el borde (API gateway/WAF/Front Door). Protege login y flujos de negocio sensibles.
- Subida de ficheros: límite de tamaño y tipo por contenido (no solo extensión), almacenamiento fuera del webroot, antivirus si procede, nombres generados. Prevención de path traversal.
- SSRF: lista de destinos permitidos, bloqueo de rangos privados y de metadatos cloud (169.254.169.254) en cualquier llamada con URL aportada por el usuario.
- Errores sin filtrar detalles internos ni stack traces. Swagger/GraphQL introspección restringidos en producción.

## 5. Secretos, datos y cadena de suministro
- Secretos en Key Vault o equivalente con identidad gestionada. Nunca en el repositorio, imágenes ni logs. Rotación definida.
- Cifrado en tránsito (TLS) y en reposo. Hash de contraseñas con Argon2id o bcrypt solo si se gestionan credenciales propias. Minimiza y enmascara PII en logs. Define retención.
- Dependencias: lockfile, `npm audit`/Dependabot/Renovate, SBOM, imágenes mínimas y sin root, firma/proveniencia donde sea posible. Auditoría de acciones sensibles (quién, qué, cuándo) inmutable.

## Compliance
Si hay RGPD, ENS, NIS2, DORA, EAA, AI Act, CRA, ISO 27001, PCI u otro marco, mapea controles a requisitos con `reference/eu-regulatory-map.md` y marca como pendiente cualquier interpretación legal. No afirmes cumplimiento.

## IA generativa
Revisa el OWASP Top 10 para aplicaciones con LLM: inyección de prompts (prompt injection) directa e indirecta a través de documentos recuperados, divulgación de información sensible, manejo inseguro de la salida (es entrada no confiable), agencia excesiva de las herramientas, fuga del prompt de sistema (sin secretos en prompts), debilidades de vectores y embeddings (fugas entre usuarios o tenants si la recuperación no filtra por permisos) y consumo no acotado. Define qué datos pueden salir al proveedor (clasificación, residencia, retención y uso para entrenamiento según contrato) y clasifica el caso de uso frente al AI Act con cumplimiento.

## Salida
En revisiones de seguridad de una API o sistema, recorre `reference/security-review-checklist.md` y marca cada punto como Cumple / No cumple / No verificado.
Modelo de amenazas resumido, decisión de identidad y flujo (diagrama de secuencia textual), modelo de autorización, controles por capa, riesgos residuales priorizados, pruebas de seguridad (SAST/DAST, tests de autorización, pentest) y ADR.

## Autoevaluación
¿Hay denegación por defecto? ¿La autorización por recurso está fuera del controller? ¿El mismo control aplica en todos los transportes? ¿Se han tratado secretos, límites y logs? ¿Se evita inventar un sistema de identidad propio sin necesidad?
