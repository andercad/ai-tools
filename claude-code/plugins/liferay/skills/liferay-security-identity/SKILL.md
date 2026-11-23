---
name: liferay-security-identity
description: 'Asesoría arquitectónica sobre seguridad e identidad en Liferay DXP: SSO con SAML u OpenID Connect, LDAP y aprovisionamiento de usuarios, Microsoft Entra ID, modelo de usuarios, organizaciones, sites, grupos de usuarios y cuentas, roles y permisos, OAuth2 y scopes para Headless, Service Access Policies, CORS, CSRF, sesiones, secretos, auditoría, protección de datos personales, IA generativa y normativa UE (RGPD, ENS, NIS2, AI Act). Usar cuando se pregunte cómo autenticar usuarios en Liferay, cómo modelar roles y permisos, cómo proteger APIs Headless o integraciones, cómo aprovisionar usuarios desde un IdP, qué auditar o qué normativa aplica. No usar como generador de configuración ni para inventar claims o endpoints de un proveedor de identidad.'
---

# Seguridad e identidad

## Objetivo
Diseñar autenticación, autorización y auditoría con mínimo privilegio, separando claramente quién eres (identidad) de qué puedes hacer (permisos), y protegiendo APIs e integraciones.

## Criterios de decisión: autenticación
| Opción | Encaja cuando | Cuidado con |
|---|---|---|
| OpenID Connect | IdP moderno (por ejemplo, Entra ID), aplicaciones web y móviles | Mapeo de claims a usuario, cierre de sesión |
| SAML | IdP corporativo que solo ofrece SAML o requisitos de federación existentes | Certificados y su rotación, metadatos |
| LDAP | Directorio como fuente de usuarios y grupos | Rendimiento de importación, no es SSO por sí mismo |
No inventes claims, endpoints ni configuraciones del IdP; verifica en su documentación y en la de la release de Liferay.

## Aprovisionamiento
Decide la fuente de verdad de usuarios y grupos (IdP, LDAP o Liferay), el momento (JIT en el login, importación periódica o protocolo de aprovisionamiento si la release lo soporta) y la baja: la revocación de acceso debe ser oportuna y verificable.

## Modelo de autorización
- Estructura: compañía, sites, organizaciones, grupos de usuarios, cuentas (cuando aplica) y equipos.
- Roles regulares, de site, de organización y de cuenta; asígnalos a grupos, no a usuarios individuales.
- Mínimo privilegio y segregación de funciones; limita y revisa a los administradores.
- Permisos sobre entidades (incluidos Objects) en el servidor; ocultar UI no es autorización.
- Matriz `Rol | Ámbito | Recurso | Acciones | Justificación`.

## APIs e integraciones
- OAuth2 con aplicaciones separadas por integración y scopes mínimos; perfiles User Agent para usuarios y Headless Server para servicio a servicio.
- Service Access Policies para limitar qué servicios son accesibles por cada mecanismo de autenticación.
- CORS con orígenes explícitos; CSRF activo en llamadas con sesión.
- Rotación de secretos y certificados; secretos en almacén externo, nunca en repositorios ni imágenes.

## Sesiones
Tiempo de expiración, cookies `Secure` y `HttpOnly`, comportamiento en cluster y cierre de sesión coordinado con el IdP.

## Auditoría y datos personales
- Registra accesos administrativos, cambios de permisos y acciones sensibles; centraliza los registros con retención definida.
- No registres tokens, secretos ni datos personales innecesarios.
- Exportación y borrado de datos personales según la normativa aplicable.
- Usa `reference/eu-regulatory-map.md` para traducir RGPD, ENS, NIS2, EAA, AI Act y otras normas aplicables en controles y evidencias.

## IA generativa
El contenido del portal puede llevar inyección de prompts (prompt injection) indirecta hacia un asistente que lo use. Decide qué datos pueden salir al proveedor del modelo, haz que la recuperación respete los permisos de Liferay, no amplíes los scopes OAuth2 por necesidades de la IA y clasifica el caso de uso frente al AI Act con cumplimiento.

## Modelo de amenazas
Revisa límites de confianza: navegador, portal, Client Extensions, servicios externos, IdP, motor de búsqueda y almacenamiento. Considera suplantación, escalada de privilegios, exposición de datos por búsqueda o APIs y abuso de cuentas de servicio.

## Antipatrones
- Confundir autenticación con autorización.
- Permisos asignados usuario a usuario.
- Un único cliente OAuth2 con todos los scopes.
- Motor de búsqueda o consola de administración expuestos sin protección.
- Credenciales en `portal-ext.properties` versionado.

## Salida
Usa `templates/permissions-matrix.md` para identidad, roles y permisos.
Diagrama de autenticación, decisión de protocolo con matriz, estrategia de aprovisionamiento y baja, matriz de roles y permisos, política de OAuth2 y scopes, controles de sesión, plan de auditoría, riesgos y ADR.

## Autoevaluación
¿He separado identidad y autorización? ¿Se aplica mínimo privilegio? ¿La baja de usuarios es verificable? ¿Los scopes son mínimos y por integración? ¿He inventado algún dato del IdP?
