---
name: nestjs-security
description: Seguridad NestJS a nivel de código. Usar al implementar login, registro, JWT, Passport, refresh tokens, guards de autenticación o roles, @Public(), permisos, autorización por recurso, y al revisar o endurecer código frente a OWASP: inyección, SSRF, path traversal, asignación masiva, subida de ficheros, helmet, CORS, CSRF, rate limiting, secretos, criptografía y dependencias. No usar para diseñar identidad (OAuth/OIDC, multi-tenant) ni normativa UE (skill nestjs-security-identity).
---

# Seguridad del backend

## Reglas clave
- Autenticación y autorización reales en el servidor; un UUID no sustituye la autorización **por recurso**.
- Sin asignación masiva: copia campo a campo desde el DTO validado; nunca `save(body)` ni `Object.assign(entity, body)`.
- Consultas parametrizadas; sin `exec` con entrada del usuario ni rutas de fichero construidas con ella.
- Contraseñas con hash adaptativo (argon2/bcrypt); secretos solo vía `ConfigService`, nunca en el repo.
- `helmet`, CORS restrictivo, rate limiting, límites de tamaño y validación de ficheros subidos.
- Llamadas a URLs externas: lista de destinos permitidos (SSRF) y timeout.
- Guards globales válidos en HTTP, GraphQL y microservicios.
- Audita dependencias antes y después de instalar (`npm audit`).

## Referencias
| Tema | Fichero |
|---|---|
| Guards, JWT, roles, permisos, recursos | [auth.md](references/auth.md) |
| OWASP Top 10/API, ficheros, SSRF, cabeceras, checklist | [security.md](references/security.md) |
