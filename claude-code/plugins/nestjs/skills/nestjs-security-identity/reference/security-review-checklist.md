# Checklist de revisión de seguridad para APIs NestJS

Marca cada punto como Cumple / No cumple / No verificado y cita la evidencia. "No verificado" nunca equivale a "Cumple".

## Identidad y sesión
- [ ] Proveedor de identidad externo con OIDC/OAuth 2.0. Sin flujos Implicit ni Password.
- [ ] JWT validado: firma (JWKS en caché), algoritmo fijado, `iss`, `aud`, `exp`/`nbf`, tenant.
- [ ] Access tokens de vida corta. Refresh tokens rotados con detección de reutilización. Revocación definida.
- [ ] SPA: BFF con cookies `HttpOnly`/`Secure`/`SameSite` o justificación de tokens en el navegador. CSRF tratado si hay cookies.
- [ ] Servicio a servicio con identidad gestionada, mTLS o Client Credentials. Sin secretos compartidos estáticos.

## Autorización (OWASP API1, API3, API5)
- [ ] Guard global con denegación por defecto (`APP_GUARD`) y rutas públicas explícitas.
- [ ] Autorización a nivel de objeto en el caso de uso o consulta (propietario/tenant), no solo por rol.
- [ ] Autorización a nivel de propiedad: DTO de salida sin campos sensibles. DTO de entrada sin campos asignables indebidos (mass assignment).
- [ ] Funciones administrativas separadas y protegidas.
- [ ] Mismos controles en HTTP, GraphQL, WebSocket y consumidores de mensajes.
- [ ] Multi-tenant: `tenantId` del token aplicado a todas las consultas. RLS valorado.

## Entrada y exposición (API4, API8)
- [ ] `ValidationPipe` global con `whitelist`, `forbidNonWhitelisted`, `transform`.
- [ ] Límites de tamaño de body, de paginación y de subida de ficheros.
- [ ] Rate limiting por usuario/IP con almacén compartido y en el borde. Login y flujos sensibles reforzados (API6).
- [ ] Helmet. CORS con orígenes explícitos.
- [ ] Errores sin stack ni detalles internos. Swagger e introspección GraphQL restringidos en producción.
- [ ] GraphQL: límites de profundidad, complejidad, aliases y batching.

## SSRF y terceros (API7, API10)
- [ ] URLs aportadas por el usuario validadas contra lista permitida. Bloqueo de IP privadas y metadatos cloud.
- [ ] Respuestas de APIs de terceros validadas y con timeout. Webhooks con firma HMAC y anti-replay.

## Inventario y configuración (API8, API9)
- [ ] Inventario de APIs y versiones expuestas. Versiones antiguas retiradas.
- [ ] Entornos no productivos sin datos reales o con datos enmascarados.
- [ ] Cabeceras de seguridad y TLS en todos los saltos.

## Secretos y datos
- [ ] Secretos en Key Vault o equivalente, con rotación. Nada en repositorio, imagen o logs.
- [ ] PII minimizada, cifrada y enmascarada en logs. Retención definida.
- [ ] Auditoría de acciones sensibles inmutable y con correlación.

## Cadena de suministro
- [ ] Lockfile. Auditoría y actualización automatizada de dependencias. SBOM.
- [ ] Imagen mínima, sin root, escaneada. Pipeline con escaneo de secretos y SAST.

## Resultado
Lista de riesgos priorizada (crítico/alto/medio/bajo) con control recomendado, responsable y forma de verificarlo.
