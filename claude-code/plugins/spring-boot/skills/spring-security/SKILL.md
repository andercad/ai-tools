---
name: spring-security
description: Backend Spring Boot. Seguridad de aplicación. Usar al implementar login, JWT, OAuth2 Resource Server, SecurityFilterChain, roles, @PreAuthorize, autorización por recurso, hash de contraseñas, CORS, CSRF, rate limiting, o al revisar vulnerabilidades como inyección, SSRF, deserialización, subida de ficheros, asignación masiva, Actuator expuesto, secretos y dependencias (OWASP Top 10). No usar para decisiones de arquitectura de identidad (spring-security-identity).
---

# Autenticación, autorización y seguridad del código

## Reglas clave
- Autorización por recurso: el usuario autenticado solo accede a lo suyo; un UUID no sustituye la comprobación. Denegar por defecto en `SecurityFilterChain`; `@PreAuthorize` en servicios.
- Sin asignación masiva: copia campo a campo desde el DTO validado, nunca el cuerpo completo sobre una entidad.
- Inyección: consultas parametrizadas, sin SpEL evaluado con entrada del usuario, sin `Runtime.exec` ni rutas de fichero construidas con ella; protege contra SSRF y deserialización insegura.
- Contraseñas con `DelegatingPasswordEncoder`/BCrypt/Argon2; tokens validados (firma, `iss`, `aud`, `exp`); nunca secretos en el repositorio.
- CORS con orígenes explícitos; CSRF según el tipo de cliente; rate limiting en login y operaciones sensibles.
- Actuator: solo los endpoints necesarios, nunca `env`, `heapdump`, `configprops` ni `loggers` sin protección.
- No registres contraseñas, tokens ni datos personales; errores sin detalles internos.

## Referencias
| Tema | Fichero |
|---|---|
| Autenticación, `SecurityFilterChain`, JWT, roles, autorización por recurso | [auth.md](references/auth.md) |
| Checklist OWASP: inyección, SSRF, ficheros, deserialización, Actuator, dependencias | [security.md](references/security.md) |
